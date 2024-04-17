from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import F
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver


class FleetSubscription(models.Model):
    total_slots = models.IntegerField(default=0, help_text="Total number of vehicle slots available for allocation.")
    allocated_slots = models.IntegerField(default=0,
                                          validators=[
                                              MinValueValidator(0)
                                          ], )

    @classmethod
    def get_instance(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def get_total_slots(self):
        return self.total_slots

    def get_allocated_slots(self):
        return self.allocated_slots

    def available_slots_left(self):
        return self.allocated_slots < self.total_slots

    def __str__(self):
        return f"Total slots: {self.total_slots}"

    def save(self, *args, **kwargs):
        if self.allocated_slots > self.total_slots:
            raise ValidationError("The allocated slots are greater than the total slots :/")
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Fleet Subscriptions"


# @receiver(pre_save, sender=FleetSubscription)
# def validate_allocated_slots(sender, instance, *args, **kwargs):
#     if FleetSubscription.get_instance().allocated_slots > FleetSubscription.get_instance().total_slots:
#         raise ValidationError('The allocated slots are greater than the total slots :/')


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
    # login_enabled = models.BooleanField(default=False)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='contact', null=True, blank=True)

    def __str__(self):
        return self.name


# @receiver(pre_save, sender=Contact)
# def check_if_login_enabled(sender, instance, *args, **kwargs):
#     if not instance.login_enabled:
#         instance.user = None


class Vehicle(models.Model):
    vehicle_type = models.CharField(max_length=255)
    license_plate = models.CharField(max_length=20, unique=True)
    is_allocated = models.BooleanField(default=False)
    is_loaded = models.BooleanField(default=False)

    # current_driver = models.OneToOneField('Driver', on_delete=models.SET_NULL, related_name='current_vehicle',
    #                                       null=True, blank=True)

    def allocate(self):
        if self.is_allocated is not True:
            if FleetSubscription.get_instance().available_slots_left():
                if FleetSubscription.objects.filter(pk=1).update(allocated_slots=F('allocated_slots') + 1) > 0:
                    self.is_allocated = True
                    self.save()  # Save Vehicle changes
            else:
                raise ValueError('There are no subscribed vehicles left.')

    def deallocate(self):
        if self.is_allocated is True:
            if FleetSubscription.objects.filter(pk=1).update(allocated_slots=F('allocated_slots') - 1) > 0:
                self.is_allocated = False
                self.save()  # Save Vehicle changes
            else:
                raise ValidationError('Failed to deallocate vehicle. Consistency issue?')

    def __str__(self):
        return f"{self.vehicle_type} - {self.license_plate}"


@receiver(post_delete, sender=Vehicle)
def decrement_allocated_slots(sender, instance, **kwargs):
    if instance.is_allocated:
        fleet_subscription = FleetSubscription.get_instance()
        fleet_subscription.allocated_slots -= 1
        fleet_subscription.save()


# class VehicleAllocation(models.Model):
#
#     @classmethod
#     def get_instance(cls):
#         # Ensure only one instance of VehicleAllocation exists
#         obj, created = cls.objects.get_or_create(pk=1)
#         return obj
#
#     def allocate_vehicle(self, vehicle: Vehicle):
#         # Ensure we don't go over the total slots available
#         if Vehicle.objects.filter(vehicle_allocation=self).count() >= FleetSubscription.get_instance().total_slots:
#             raise ValidationError("No available slots left to allocate.")
#         vehicle.vehicle_allocation = self
#         vehicle.save()
#
#     def deallocate_vehicle(self, vehicle: Vehicle):
#         if vehicle.vehicle_allocation_id == self.pk:
#             vehicle.vehicle_allocation = None
#             vehicle.save()
#
#     def save(self, *args, **kwargs):
#         # Prevent creating more than one instance
#         if not self.pk and VehicleAllocation.objects.exists():
#             raise ValidationError("There is already a VehicleAllocation instance.")
#         super(VehicleAllocation, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return f"Vehicle Allocation - ID: {self.pk}"


class Driver(models.Model):
    # name = models.CharField(max_length=255)
    current_vehicle = models.OneToOneField(Vehicle, related_name='current_driver', on_delete=models.SET_NULL,
                                           null=True, blank=True)
    contact = models.OneToOneField(Contact, related_name='driver', on_delete=models.CASCADE)

    # user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='driver')
    # Add additional fields as necessary
    # ...

    def __str__(self):
        return self.contact.name


class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)

    # Additional fields like address, preferences can be added later
    # ...

    def __str__(self):
        return self.name


class DeliveryBatch(models.Model):
    # batch_id = models.CharField(max_length=50, unique=True)
    # For simplicity, let's say one delivery batch goes to one customer.
    customer = models.ForeignKey(Customer, related_name='delivery_batches', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, related_name='delivery_batches', on_delete=models.SET_NULL, null=True,
                                blank=True)
    delivery_address = models.TextField()
    # ...


# class Order(models.Model):
#     contents = models.TextField()
#     customer = models.ForeignKey(Customer, related_name='orders', on_delete=models.PROTECT, null=False, blank=False)
#     delivery_batch = models.OneToOneField(DeliveryBatch, related_name='order', on_delete=models.CASCADE, null=True,
#                                           blank=True)


# Assuming that a Crate is part of your system
class Crate(models.Model):
    crate_id = models.CharField(max_length=50, unique=True, primary_key=True)
    # contents = models.TextField()
    # This is a simple ForeignKey relationship. For real-world scenarios, consider using a ManyToManyField if crates can be part of multiple batches.
    delivery_batch = models.ForeignKey('DeliveryBatch', related_name='crates', on_delete=models.SET_NULL, null=True,
                                       blank=True)

    # ...

    def __str__(self):
        return f'Crate #{self.crate_id}'

# Additional models for managing user accounts, subscriptions, and other data might be necessary as the system grows.
