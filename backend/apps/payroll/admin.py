from django.contrib import admin

from apps.payroll.models import (
    EmployeePayroll,
    EmployeeSalary,
    EmployeeSalaryComponent,
    EPFContribution,
    EPFSettings,
    ETFContribution,
    ETFSettings,
    PAYECalculation,
    PAYETaxSlab,
    PayrollHistory,
    PayrollLineItem,
    PayrollPeriod,
    PayrollRun,
    PayrollSettings,
    SalaryComponent,
    SalaryGrade,
    SalaryHistory,
    SalaryTemplate,
    TaxExemption,
    TemplateComponent,
)


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "component_type", "category", "is_active")
    list_filter = ("component_type", "category", "is_active", "is_taxable", "is_epf_applicable")
    search_fields = ("name", "code")
    ordering = ("display_order", "name")


@admin.register(SalaryTemplate)
class SalaryTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(TemplateComponent)
class TemplateComponentAdmin(admin.ModelAdmin):
    list_display = ("template", "component", "default_value", "can_override")
    list_filter = ("can_override",)


@admin.register(SalaryGrade)
class SalaryGradeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "level", "min_salary", "max_salary")
    ordering = ("level",)


@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ("employee", "basic_salary", "gross_salary", "effective_from", "is_current")
    list_filter = ("is_current",)


@admin.register(EmployeeSalaryComponent)
class EmployeeSalaryComponentAdmin(admin.ModelAdmin):
    list_display = ("employee_salary", "component", "amount")


@admin.register(SalaryHistory)
class SalaryHistoryAdmin(admin.ModelAdmin):
    list_display = ("employee", "previous_basic", "new_basic", "effective_date", "change_reason")
    ordering = ("-effective_date",)


@admin.register(EPFSettings)
class EPFSettingsAdmin(admin.ModelAdmin):
    list_display = ("employee_rate", "employer_rate", "max_contribution_ceiling")


@admin.register(ETFSettings)
class ETFSettingsAdmin(admin.ModelAdmin):
    list_display = ("employer_rate",)


@admin.register(PAYETaxSlab)
class PAYETaxSlabAdmin(admin.ModelAdmin):
    list_display = ("tax_year", "from_amount", "to_amount", "rate")
    ordering = ("tax_year", "from_amount")


@admin.register(TaxExemption)
class TaxExemptionAdmin(admin.ModelAdmin):
    list_display = ("name", "annual_amount", "monthly_amount", "is_active")
    list_filter = ("is_active",)


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "period_month", "period_year", "status", "pay_date", "is_locked")
    list_filter = ("status", "is_locked", "period_year")
    search_fields = ("name",)
    ordering = ("-period_year", "-period_month")
    readonly_fields = ("locked_at", "locked_by", "created_on", "updated_on")


@admin.register(PayrollSettings)
class PayrollSettingsAdmin(admin.ModelAdmin):
    list_display = ("effective_from", "default_pay_day", "attendance_cutoff_day", "require_approval", "auto_create_period")
    list_filter = ("require_approval", "auto_create_period", "adjust_for_weekends")
    filter_horizontal = ("approvers",)


@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ("payroll_period", "run_number", "status", "total_employees", "total_net", "started_at", "completed_at")
    list_filter = ("status",)
    search_fields = ("payroll_period__name",)
    ordering = ("-created_on",)
    readonly_fields = ("started_at", "completed_at", "approved_at", "created_on", "updated_on")


@admin.register(EmployeePayroll)
class EmployeePayrollAdmin(admin.ModelAdmin):
    list_display = ("employee", "payroll_run", "gross_salary", "total_deductions", "net_salary", "payment_status")
    list_filter = ("payment_status", "is_verified")
    search_fields = ("employee__first_name", "employee__last_name")
    readonly_fields = ("created_on", "updated_on")


@admin.register(PayrollLineItem)
class PayrollLineItemAdmin(admin.ModelAdmin):
    list_display = ("employee_payroll", "component", "line_type", "final_amount")
    list_filter = ("line_type",)


@admin.register(EPFContribution)
class EPFContributionAdmin(admin.ModelAdmin):
    list_display = ("employee_payroll", "epf_base", "employee_amount", "employer_amount", "total_amount", "calculation_date")
    list_filter = ("calculation_date",)
    readonly_fields = ("created_on", "updated_on")


@admin.register(ETFContribution)
class ETFContributionAdmin(admin.ModelAdmin):
    list_display = ("employee_payroll", "etf_base", "employer_amount", "calculation_date")
    list_filter = ("calculation_date",)
    readonly_fields = ("created_on", "updated_on")


@admin.register(PAYECalculation)
class PAYECalculationAdmin(admin.ModelAdmin):
    list_display = ("employee_payroll", "gross_income", "taxable_income", "monthly_tax", "calculation_date")
    list_filter = ("calculation_date",)
    readonly_fields = ("created_on", "updated_on")


@admin.register(PayrollHistory)
class PayrollHistoryAdmin(admin.ModelAdmin):
    list_display = ("payroll_run", "action", "performed_by", "performed_at")
    list_filter = ("action", "performed_at")
    search_fields = ("payroll_run__id", "performed_by__email", "reason")
    readonly_fields = ("performed_at",)
    ordering = ("-performed_at",)
