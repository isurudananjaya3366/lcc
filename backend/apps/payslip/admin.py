"""Django admin configuration for Payslip models."""

from django.contrib import admin

from apps.payslip.models import (
    Payslip,
    PayslipBatch,
    PayslipDeduction,
    PayslipEarning,
    PayslipEmployerContribution,
    PayslipTemplate,
)


class PayslipEarningInline(admin.TabularInline):
    model = PayslipEarning
    extra = 0
    readonly_fields = ("component_code", "component_name", "amount", "ytd_amount")


class PayslipDeductionInline(admin.TabularInline):
    model = PayslipDeduction
    extra = 0
    readonly_fields = ("component_code", "component_name", "amount", "ytd_amount")


class PayslipEmployerContributionInline(admin.TabularInline):
    model = PayslipEmployerContribution
    extra = 0
    readonly_fields = ("component_code", "component_name", "amount", "ytd_amount")


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = (
        "slip_number",
        "employee",
        "payroll_period",
        "status",
        "email_sent",
        "view_count",
        "download_count",
        "generated_at",
    )
    list_filter = ("status", "payroll_period", "email_sent", "generated_at")
    search_fields = ("slip_number", "employee__first_name", "employee__last_name")
    readonly_fields = (
        "slip_number",
        "generated_at",
        "generated_by",
        "sent_at",
        "sent_to",
        "first_viewed_at",
        "view_count",
        "first_downloaded_at",
        "download_count",
        "created_on",
        "updated_on",
    )
    date_hierarchy = "generated_at"
    inlines = [
        PayslipEarningInline,
        PayslipDeductionInline,
        PayslipEmployerContributionInline,
    ]
    fieldsets = (
        (
            "Identification",
            {"fields": ("slip_number", "employee", "payroll_period", "employee_payroll")},
        ),
        (
            "Status & Generation",
            {"fields": ("status", "generated_at", "generated_by", "pdf_file")},
        ),
        (
            "Email Distribution",
            {"fields": ("email_sent", "sent_at", "sent_to")},
        ),
        (
            "Tracking",
            {
                "fields": (
                    "first_viewed_at",
                    "view_count",
                    "first_downloaded_at",
                    "download_count",
                ),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_on", "updated_on")},
        ),
    )
    actions = ["generate_pdfs", "send_emails"]

    @admin.action(description="Generate PDFs for selected payslips")
    def generate_pdfs(self, request, queryset):
        from apps.payslip.services.generator import PayslipGenerator

        generator = PayslipGenerator()
        count = 0
        for payslip in queryset.filter(status="DRAFT"):
            try:
                generator.generate(payslip.pk, request.user)
                count += 1
            except Exception:
                pass
        self.message_user(request, f"Generated {count} payslip PDF(s).")

    @admin.action(description="Send email for selected payslips")
    def send_emails(self, request, queryset):
        from apps.payslip.services.emailer import PayslipEmailer

        emailer = PayslipEmailer()
        count = 0
        for payslip in queryset.filter(email_sent=False, pdf_file__isnull=False):
            try:
                emailer.send(payslip)
                count += 1
            except Exception:
                pass
        self.message_user(request, f"Sent {count} payslip email(s).")


@admin.register(PayslipBatch)
class PayslipBatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "batch_type",
        "payroll_period",
        "status",
        "total_count",
        "success_count",
        "failed_count",
        "started_at",
    )
    list_filter = ("batch_type", "status")
    readonly_fields = (
        "initiated_by",
        "started_at",
        "completed_at",
        "success_count",
        "failed_count",
        "error_log",
    )


@admin.register(PayslipTemplate)
class PayslipTemplateAdmin(admin.ModelAdmin):
    list_display = ("company_name", "is_active", "paper_size", "show_ytd", "show_employer_contributions")
    list_filter = ("is_active", "paper_size")
    search_fields = ("company_name",)
