from django.contrib.auth.models import Group
from rest_framework import serializers
from .models import Crate, DeliveryBatch, Customer, Driver, Vehicle, User, Contact


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'contact_details']
        read_only_fields = ('id',)


class CrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crate
        fields = ['crate_id', 'contents', 'delivery_batch']
        read_only_fields = ('id',)

class SimpleVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_type', 'license_plate']

class DeliveryBatchSerializer(serializers.ModelSerializer):
    crates = CrateSerializer(many=True, read_only=True)
    vehicle = SimpleVehicleSerializer(read_only=True)

    class Meta:
        model = DeliveryBatch
        fields = ['id', 'vehicle', 'crates']
        read_only_fields = ('id',)


class VehicleSerializer(serializers.ModelSerializer):
    delivery_batches = DeliveryBatchSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_type', 'license_plate', 'delivery_batches']





class DriverSerializer(serializers.ModelSerializer):
    current_vehicle = SimpleVehicleSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Driver
        fields = ['id', 'name', 'current_vehicle']


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    # driver = DriverSerializer(read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'groups']


class ContactSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = ['name', 'login_enabled', 'user', 'id']
