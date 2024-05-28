from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Vehicle, Driver, Customer, Crate, DeliveryBatch, \
    FleetSubscription, User, Contact, Address


# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'is_staff', 'is_active')  # Fields to display in admin list
#     fieldsets = (
#         (None, {'fields': ('username', 'password', 'email')}),
#         ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#     )  # Group user creation fields
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'password1', 'password2')
#         }),
#     )  # Make password fields wider


class DeliveryBatchInline(admin.TabularInline):  # Or admin.StackedInline
    model = DeliveryBatch
    extra = 0  # No extra forms on the add page
    readonly_fields = ('customer', 'crates', 'delivery_address')  # Make fields read-only

    def has_add_permission(self, request, obj=None):
        return False  # Disable adding new delivery batches inline


class CrateInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = Crate
    extra = 1  # Number of extra blank forms to display initially
    # You can further customize the inline form with attributes like fields, readonly_fields, etc.


class DeliveryBatchAdmin(admin.ModelAdmin):
    # ... other customizations ...
    inlines = [CrateInline]

class AddressInline(admin.TabularInline):
    model = Address
    extra = 1


class CustomerAdmin(admin.ModelAdmin):
    inlines = [AddressInline]





class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'groups')}),  # Include 'groups' field
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'groups')}),  # Include 'groups' field
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not (request.user.groups.filter(name='pierr_admin').exists() or request.user.is_superuser):
            qs = qs.exclude(groups__name='pierr_admin').exclude(is_superuser=True)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not (request.user.groups.filter(name='pierr_admin').exists() or request.user.is_superuser):
            # Disable the "is_superuser" field
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].disabled = True

            # Hide "pierr_admin" group from available choices
            if 'groups' in form.base_fields:
                # Hide "pierr_admin" group from available choices
                form.base_fields['groups'].queryset = Group.objects.exclude(name='pierr_admin')
        return form




class CustomVehicleAdmin(admin.ModelAdmin):
    # Exclude the 'is_allocated' and 'is_loaded' fields


    # Add any other customizations as needed, such as list_display, search_fields, etc.
    # For example:
    list_display = ('license_plate', 'vehicle_type')
    inlines = [DeliveryBatchInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not (request.user.groups.filter(name='pierr_admin').exists() or request.user.is_superuser):
            # Disable the "is_superuser" field
            if 'is_allocated' in form.base_fields:
                form.base_fields['is_allocated'].disabled = True

            if 'is_loaded' in form.base_fields:
                form.base_fields['is_loaded'].disabled = True

        return form


admin.site.register(Vehicle, CustomVehicleAdmin)
admin.site.register(Driver)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Crate)
# admin.site.register(DeliveryBatch, DeliveryBatchAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Contact)
# admin.site.register(VehicleAllocation)
admin.site.register(FleetSubscription)
