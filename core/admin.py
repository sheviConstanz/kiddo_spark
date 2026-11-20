from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from . import models as m


class AcademicAdminSite(admin.AdminSite):
    site_header = 'Kiddo Spark · Superadministración'
    site_title = 'Kiddo Spark'
    index_title = 'Usuarios, permisos y configuración académica'

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser


site = AcademicAdminSite(name='superadmin')


class KiddoUserAdmin(UserAdmin):
    readonly_fields = ['credits', 'points', 'last_login', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (('Saldos (solo lectura)', {'fields': ['credits', 'points']}),)
    add_fieldsets = ((None, {'classes': ['wide'], 'fields': ['username', 'email', 'password1', 'password2']}),)

    def save_model(self, request, obj, form, change):
        # The currently used super account cannot accidentally lock itself out.
        if obj.pk == request.user.pk:
            obj.is_active = obj.is_staff = obj.is_superuser = True
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'kind', 'approved', 'active']
    list_filter = ['kind', 'approved', 'active']
    filter_horizontal = ['administrators']
    readonly_fields = ['created_by', 'approved']

    def get_readonly_fields(self, request, obj=None):
        return [*self.readonly_fields, 'kind'] if obj else self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
            super().save_model(request, obj, form, change)
        else:
            fields = set(form.changed_data) - {'administrators'}
            if fields:
                obj.save(update_fields=fields)

    def has_delete_permission(self, request, obj=None):
        return False


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


site.register(m.User, KiddoUserAdmin)
site.register(Group)
site.register(m.Organization, OrganizationAdmin)
for model in [m.Booking, m.Movement, m.Membership, m.ServiceRequest, m.RequestEvent, m.Settlement, m.Withdrawal, m.AuditLog, m.ProviderReviewEvent]:
    site.register(model, ReadOnlyAdmin)
