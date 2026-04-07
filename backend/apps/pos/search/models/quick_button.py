"""
QuickButtonGroup & QuickButton models for POS product shortcuts.

Allows POS operators to configure grid-based quick buttons for
frequently sold products, organized in named groups.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class QuickButtonGroup(BaseModel):
    """A named group containing a grid of quick-select product buttons."""

    name = models.CharField(
        max_length=100,
        verbose_name=_("Group Name"),
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Code"),
        help_text=_("Unique identifier for this group"),
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name=_("Icon"),
        help_text=_("Icon name or class for the group tab"),
    )
    color = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name=_("Color"),
        help_text=_("Hex color code for the group tab"),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name=_("Display Order"),
    )
    rows = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name=_("Rows"),
    )
    columns = models.IntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_("Columns"),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Default Group"),
        help_text=_("Show this group by default when POS opens"),
    )
    terminals = models.ManyToManyField(
        "pos.POSTerminal",
        blank=True,
        related_name="quick_button_groups",
        verbose_name=_("Terminals"),
        help_text=_("Terminals this group is assigned to (blank = all)"),
    )

    class Meta:
        db_table = "pos_quick_button_group"
        ordering = ["display_order", "name"]
        verbose_name = _("Quick Button Group")
        verbose_name_plural = _("Quick Button Groups")

    def __str__(self):
        return self.name

    @property
    def max_buttons(self):
        return self.rows * self.columns

    def get_button_count(self):
        """Return the number of buttons in this group."""
        return self.buttons.count()

    def get_grid_capacity(self):
        """Return total grid capacity (rows * columns)."""
        return self.rows * self.columns

    def is_grid_full(self):
        """Check if all grid positions are occupied."""
        return self.get_button_count() >= self.get_grid_capacity()


class QuickButton(BaseModel):
    """A single quick-select button mapped to a product on the POS grid."""

    group = models.ForeignKey(
        QuickButtonGroup,
        on_delete=models.CASCADE,
        related_name="buttons",
        verbose_name=_("Group"),
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="quick_buttons",
        verbose_name=_("Product"),
    )
    label = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name=_("Label"),
        help_text=_("Custom label (defaults to product name)"),
    )
    image = models.ImageField(
        upload_to="pos/quick_buttons/",
        blank=True,
        null=True,
        verbose_name=_("Image"),
    )
    color = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name=_("Color"),
        help_text=_("Hex color for the button"),
    )
    row = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Row"),
    )
    column = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Column"),
    )
    quick_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=1,
        verbose_name=_("Quick Quantity"),
        help_text=_("Default quantity added when button is pressed"),
    )

    class Meta:
        db_table = "pos_quick_button"
        ordering = ["row", "column"]
        verbose_name = _("Quick Button")
        verbose_name_plural = _("Quick Buttons")
        constraints = [
            models.UniqueConstraint(
                fields=["group", "row", "column"],
                name="unique_quick_button_position",
            ),
        ]
        indexes = [
            models.Index(fields=["group", "row", "column"], name="pos_qb_position"),
        ]

    def __str__(self):
        return self.label or str(self.product)

    @property
    def display_label(self):
        return self.label or self.product.name

    @property
    def position_tuple(self):
        """Return (row, column) tuple."""
        return (self.row, self.column)

    @property
    def is_valid_position(self):
        """Check if button position is within group grid bounds."""
        return (
            1 <= self.row <= self.group.rows
            and 1 <= self.column <= self.group.columns
        )

    def get_display_label(self):
        """Return the display label for this button."""
        return self.label or self.product.name

    def get_position_string(self):
        """Return human-readable position string."""
        return f"Row {self.row}, Col {self.column}"

    def get_effective_color(self):
        """Return button color, falling back to group color."""
        return self.color or self.group.color or ""

    @classmethod
    def get_occupied_positions(cls, group):
        """Return set of occupied (row, column) tuples for a group."""
        return set(
            cls.objects.filter(group=group).values_list("row", "column")
        )

    def find_next_available_position(self):
        """Find the next open (row, col) in this button's group."""
        occupied = set(
            self.group.buttons.values_list("row", "column")
        )
        for r in range(1, self.group.rows + 1):
            for c in range(1, self.group.columns + 1):
                if (r, c) not in occupied:
                    return (r, c)
        return None

    def swap_position_with(self, other):
        """Atomically swap positions with another button in the same group."""
        from django.db import transaction

        if self.group_id != other.group_id:
            raise ValueError("Cannot swap buttons from different groups")
        with transaction.atomic():
            self.row, other.row = other.row, self.row
            self.column, other.column = other.column, self.column
            self.save(update_fields=["row", "column", "updated_on"])
            other.save(update_fields=["row", "column", "updated_on"])

    def move_to(self, row, column):
        """Move this button to a specific position."""
        from django.core.exceptions import ValidationError

        if row < 1 or row > self.group.rows:
            raise ValidationError(f"Row must be between 1 and {self.group.rows}")
        if column < 1 or column > self.group.columns:
            raise ValidationError(
                f"Column must be between 1 and {self.group.columns}"
            )
        if (
            self.group.buttons.filter(row=row, column=column)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(f"Position ({row}, {column}) is already occupied")
        self.row = row
        self.column = column
        self.save(update_fields=["row", "column", "updated_on"])
