"""
Management command to seed the database with sample category data.

Creates a hierarchical category tree with Sri Lankan business
context for development, testing, and demo purposes.

Usage::

    python manage.py seed_categories
    python manage.py seed_categories --clear
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.products.models import Category


# ── Sample category tree ────────────────────────────────────────────
# Each entry: (name, icon, children)
# Children follow the same recursive structure.
CATEGORY_TREE = [
    (
        "Electronics",
        "fas fa-tv",
        [
            (
                "Mobile Phones",
                "fas fa-mobile-alt",
                [
                    ("Smartphones", "fas fa-mobile-alt", []),
                    ("Feature Phones", "fas fa-phone", []),
                ],
            ),
            (
                "Laptops & Computers",
                "fas fa-laptop",
                [
                    ("Gaming Laptops", "fas fa-gamepad", []),
                    ("Business Laptops", "fas fa-briefcase", []),
                ],
            ),
            (
                "Accessories",
                "fas fa-headphones",
                [
                    ("Chargers & Cables", "fas fa-plug", []),
                    ("Cases & Covers", "fas fa-shield-alt", []),
                ],
            ),
            ("Home Appliances", "fas fa-blender", []),
        ],
    ),
    (
        "Clothing",
        "fas fa-tshirt",
        [
            (
                "Men's Wear",
                "fas fa-male",
                [
                    ("Shirts", "fas fa-tshirt", []),
                    ("Trousers", "fas fa-tshirt", []),
                ],
            ),
            (
                "Women's Wear",
                "fas fa-female",
                [
                    ("Sarees", "fas fa-female", []),
                    ("Dresses", "fas fa-female", []),
                ],
            ),
            ("Children's Wear", "fas fa-child", []),
            (
                "Traditional Wear",
                "fas fa-vest-patches",
                [
                    ("National Dress", "fas fa-vest-patches", []),
                ],
            ),
        ],
    ),
    (
        "Food & Grocery",
        "fas fa-shopping-basket",
        [
            (
                "Rice & Grains",
                "fas fa-seedling",
                [
                    ("Samba Rice", "fas fa-seedling", []),
                    ("Basmati Rice", "fas fa-seedling", []),
                    ("Red Rice", "fas fa-seedling", []),
                ],
            ),
            (
                "Spices",
                "fas fa-pepper-hot",
                [
                    ("Cinnamon (Ceylon)", "fas fa-pepper-hot", []),
                    ("Pepper", "fas fa-pepper-hot", []),
                    ("Cardamom", "fas fa-pepper-hot", []),
                ],
            ),
            (
                "Beverages",
                "fas fa-mug-hot",
                [
                    ("Tea (Ceylon)", "fas fa-mug-hot", []),
                    ("Soft Drinks", "fas fa-glass-whiskey", []),
                ],
            ),
            ("Local Products", "fas fa-store", []),
        ],
    ),
    (
        "Hardware & Construction",
        "fas fa-hammer",
        [
            ("Construction Materials", "fas fa-hard-hat", []),
            ("Power Tools", "fas fa-tools", []),
            ("Hand Tools", "fas fa-wrench", []),
            ("Plumbing", "fas fa-faucet", []),
        ],
    ),
    (
        "Ayurveda & Traditional Medicine",
        "fas fa-leaf",
        [
            ("Herbal Remedies", "fas fa-mortar-pestle", []),
            ("Wellness Products", "fas fa-spa", []),
            ("Essential Oils", "fas fa-oil-can", []),
        ],
    ),
]


class Command(BaseCommand):
    """Seed the database with sample categories for development."""

    help = (
        "Create sample hierarchical categories for development and "
        "testing. Includes Sri Lankan business context."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing categories before seeding.",
        )

    # ── Main entry point ────────────────────────────────────────────

    def handle(self, *args, **options):
        if options["clear"]:
            count = Category.objects.count()
            Category.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Deleted {count} existing categories.")
            )

        created_count = 0
        skipped_count = 0

        for order, (name, icon, children) in enumerate(CATEGORY_TREE):
            c_created, c_skipped = self._create_category(
                name=name,
                icon=icon,
                parent=None,
                display_order=order * 10,
                children=children,
            )
            created_count += c_created
            skipped_count += c_skipped

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding complete: {created_count} created, "
                f"{skipped_count} skipped (already existed)."
            )
        )
        self.stdout.write(
            f"Total categories in database: {Category.objects.count()}"
        )

    # ── Recursive helper ────────────────────────────────────────────

    def _create_category(
        self, name, icon, parent, display_order, children
    ):
        """Create a category and recursively create its children."""
        slug = slugify(name)
        category, created = Category.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "icon": icon,
                "parent": parent,
                "display_order": display_order,
                "is_active": True,
            },
        )

        created_count = 1 if created else 0
        skipped_count = 0 if created else 1

        if created:
            self.stdout.write(f"  Created: {category.get_full_path()}")
        else:
            self.stdout.write(
                f"  Skipped (exists): {slug}"
            )

        for child_order, (child_name, child_icon, grandchildren) in enumerate(
            children
        ):
            c_created, c_skipped = self._create_category(
                name=child_name,
                icon=child_icon,
                parent=category,
                display_order=child_order * 10,
                children=grandchildren,
            )
            created_count += c_created
            skipped_count += c_skipped

        return created_count, skipped_count
