from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import  AbstractUser
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class FleetSubscription(models.Model):
    total_slots = models.IntegerField(default=0, help_text="Total number of vehicle slots available for allocation.")

    @classmethod
    def get_instance(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Total slots: {self.total_slots}"

    class Meta:
        verbose_name_plural = "Fleet Subscriptions"


# class UserType(models.TextChoices):
#     PIERRADMIN = 'PIERRADMIN', 'PIERR Admin'
#     ADMIN = 'ADMIN', 'Admin'
#     BILLINGSTAFF = 'BILLINGSTAFF', 'Billing Staff'
#     TRANSPORTALLOCATIONSTAFF = 'TRANSPORTALLOCATIONSTAFF', 'Transport Allocation Staff'
#     DRIVER = 'DRIVER', 'Driver'

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     # driver = models.OneToOneField('Driver', on_delete=models.SET_NULL, null=True, blank=True,
#     #                               related_name='user_profile')
#
#     # Add any additional fields here
#
#     def __str__(self):
#         return f"{self.user.username}'s profile"


# Signal to create or update user profile when the User model is saved
class User(AbstractUser):
    pass


class Contact(models.Model):
    name = models.CharField(max_length=255)
    login_enabled = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='contact', null=True, blank=True)

    def __str__(self):
        return self.name


@receiver(pre_save, sender=Contact)
def check_if_login_enabled(sender, instance, *args, **kwargs):
    if not instance.login_enabled:
        instance.user = None


class Vehicle(models.Model):
    vehicle_type = models.CharField(max_length=255)
    license_plate = models.CharField(max_length=20, unique=True)
    vehicle_allocation = models.ForeignKey('VehicleAllocation', related_name='allocated_vehicles',
                                           on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle_type} - {self.license_plate}"


class VehicleAllocation(models.Model):

    @classmethod
    def get_instance(cls):
        # Ensure only one instance of VehicleAllocation exists
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def allocate_vehicle(self, vehicle: Vehicle):
        # Ensure we don't go over the total slots available
        if Vehicle.objects.filter(vehicle_allocation=self).count() >= FleetSubscription.get_instance().total_slots:
            raise ValidationError("No available slots left to allocate.")
        vehicle.vehicle_allocation = self
        vehicle.save()

    def deallocate_vehicle(self, vehicle: Vehicle):
        if vehicle.vehicle_allocation_id == self.pk:
            vehicle.vehicle_allocation = None
            vehicle.save()

    def save(self, *args, **kwargs):
        # Prevent creating more than one instance
        if not self.pk and VehicleAllocation.objects.exists():
            raise ValidationError("There is already a VehicleAllocation instance.")
        super(VehicleAllocation, self).save(*args, **kwargs)

    def __str__(self):
        return f"Vehicle Allocation - ID: {self.pk}"


class Driver(models.Model):
    name = models.CharField(max_length=255)
    current_vehicle = models.OneToOneField(Vehicle, related_name='current_driver', on_delete=models.SET_NULL, null=True, blank=True)
    # user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='driver')
    # Add additional fields as necessary
    # ...

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=255)
    contact_details = models.CharField(max_length=255)

    # Additional fields like address, preferences can be added later
    # ...

    def __str__(self):
        return self.name


class DeliveryBatch(models.Model):
    # batch_id = models.CharField(max_length=50, unique=True)
    # For simplicity, let's say one delivery batch goes to one customer.
    # customer = models.ForeignKey(Customer, related_name='delivery_batches', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, related_name='delivery_batches', on_delete=models.SET_NULL, null=True, blank=True)
    # ...


# class Order(models.Model):
#     contents = models.TextField()
#     customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.PROTECT, null=False, blank=False)
#     delivery_batch = models.OneToOneField(DeliveryBatch, related_name='order', on_delete=models.CASCADE, null=True,
#                                           blank=True)


# Assuming that a Crate is part of your system
class Crate(models.Model):
    crate_id = models.CharField(max_length=50, unique=True, primary_key=True)
    contents = models.TextField()
    # This is a simple ForeignKey relationship. For real-world scenarios, consider using a ManyToManyField if crates can be part of multiple batches.
    delivery_batch = models.ForeignKey('DeliveryBatch', related_name='crates', on_delete=models.SET_NULL, null=True,
                                       blank=True)

    # ...

    def __str__(self):
        return f'Crate #{self.crate_id}'

# Additional models for managing user accounts, subscriptions, and other data might be necessary as the system grows.