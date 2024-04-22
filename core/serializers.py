from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import Crate, DeliveryBatch, Customer, Driver, Vehicle, User, Contact, Address


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'value']
        read_only_fields = ('id',)


class CustomerSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone_number', 'addresses']
        read_only_fields = ('id',)


class CrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crate
        fields = ['crate_id', 'delivery_batch']
        read_only_fields = ('id',)


class SimpleVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_type', 'license_plate', 'is_loaded']


class AddDeliveryBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBatch
        fields = ['id', 'crates', 'customer', 'delivery_address']


class SimpleDeliveryBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBatch
        fields = ['id', 'vehicle', 'customer', 'crates', 'delivery_address']
        read_only_fields = ('id',)


class DeliveryBatchSerializer(serializers.ModelSerializer):
    crates = CrateSerializer(many=True, read_only=True)
    vehicle = SimpleVehicleSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    delivery_address = AddressSerializer(read_only=True)

    class Meta:
        model = DeliveryBatch
        fields = ['id', 'vehicle', 'customer', 'crates', 'delivery_address']
        read_only_fields = ('id',)


class VehicleSerializer(serializers.ModelSerializer):
    delivery_batches = DeliveryBatchSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_type', 'license_plate', 'delivery_batches', 'is_loaded']


class ContactSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = ['name', 'user', 'id']


class DriverSerializer(serializers.ModelSerializer):
    current_vehicle = SimpleVehicleSerializer(read_only=True, allow_null=True)
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Driver
        fields = ['id', 'current_vehicle', 'contact']


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    contact = ContactSerializer(read_only=True)

    # driver = DriverSerializer(read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'groups', 'contact']
