from django.contrib import admin
from .models import Vehicle, Driver, Customer, Crate, DeliveryBatch, VehicleAllocation, \
    FleetSubscription, User, Contact

admin.site.register(Vehicle)
admin.site.register(Driver)
admin.site.register(Customer)
admin.site.register(Crate)
admin.site.register(DeliveryBatch)
admin.site.register(User)
admin.site.register(Contact)
admin.site.register(VehicleAllocation)
admin.site.register(FleetSubscription)
