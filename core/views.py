from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Crate, DeliveryBatch, Customer, Vehicle, Contact, User, FleetSubscription, Driver
from core.serializers import CrateSerializer, DeliveryBatchSerializer, CustomerSerializer, VehicleSerializer, \
    ContactSerializer, AddDeliveryBatchSerializer, SimpleDeliveryBatchSerializer, DriverSerializer


class CrateViewSet(viewsets.ModelViewSet):
    queryset = Crate.objects.all()
    serializer_class = CrateSerializer

    @action(methods=['GET'], detail=False)
    def get_unallocated_crates(self, request):
        unallocated_crates = Crate.objects.filter(delivery_batch=None)
        serializer = CrateSerializer(data=unallocated_crates, many=True)
        serializer.is_valid()

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def add_multiple_crates(self, request):
        data = request.data
        crate_ids = data.get('crateIds', [])  # Get the list of crate IDs

        created_crates = []
        errors = []

        for crate_id in crate_ids:
            try:
                crate = Crate.objects.create(crate_id=crate_id)
                created_crates.append(crate)
            except IntegrityError:  # Handle duplicate crate ID
                errors.append(f'Crate ID "{crate_id}" already exists.')

        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CrateSerializer(created_crates, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeliveryBatchViewSet(viewsets.ModelViewSet):
    queryset = DeliveryBatch.objects.all()

    # serializer_class = DeliveryBatchSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddDeliveryBatchSerializer
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return SimpleDeliveryBatchSerializer
        return DeliveryBatchSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    @action(detail=True, methods=['POST'])
    def assign_delivery_batch(self, request, pk):

        # Extract delivery batch ID from request data
        delivery_batch_id = request.data.get('id')

        if not delivery_batch_id:
            raise ValueError('Missing delivery batch ID in request body')

        # Get the delivery vehicle (instance) and delivery batch instances
        vehicle: Vehicle = self.get_queryset().get(pk=pk)
        delivery_batch: DeliveryBatch = DeliveryBatch.objects.get(pk=delivery_batch_id)
        if delivery_batch.vehicle is not None:
            delivery_batch_vehicle: Vehicle = delivery_batch.vehicle
            delivery_batch_vehicle.delivery_batches.remove(delivery_batch)
            if delivery_batch_vehicle.delivery_batches.count() == 0:
                delivery_batch_vehicle.deallocate()
        if FleetSubscription.get_instance().available_slots_left() or vehicle.is_allocated:
            vehicle.allocate()
            vehicle.delivery_batches.add(delivery_batch)

            return Response({"message": "Delivery Batch assigned successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Not enough subscribed vehicles."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def assign_driver(self, request, pk):

        # Extract delivery batch ID from request data
        driver_id = request.data.get('id')

        if not driver_id:
            raise ValueError('Missing driver ID in request body')

        # Get the delivery vehicle (instance) and delivery batch instances
        vehicle: Vehicle = self.get_queryset().get(pk=pk)
        driver: Driver = Driver.objects.get(pk=driver_id)
        # if driver.current_vehicle is not None:
        #     driver_previous_vehicle: Vehicle = driver.current_vehicle
        #     driver_previous_vehicle.driver = None
        if driver.current_vehicle is not None:
            driver_previous_vehicle = driver.current_vehicle
            driver_previous_vehicle.current_driver = None
            driver_previous_vehicle.save()

        print()
        try:
            if vehicle.current_driver:
                vehicle_previous_driver: Driver = vehicle.current_driver
                vehicle_previous_driver.current_vehicle = None
                vehicle_previous_driver.save()
        except ObjectDoesNotExist:
            pass

        vehicle.current_driver = driver

        vehicle.save()
        driver.save()

        return Response({"message": "Delivery Batch assigned successfully."}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def get_crates_of_vehicle(self, request, pk):
        try:
            vehicle = Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get delivery batches associated with the vehicle
        delivery_batches = vehicle.delivery_batches.all()

        # Collect crates from all delivery batches
        crates = []
        for batch in delivery_batches:
            crates.extend(batch.crates.all())

        # Serialize the crates
        serializer = CrateSerializer(crates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['PATCH', 'PUT'], detail=True)
    def load_vehicle(self, request, pk):
        vehicle: Vehicle = Vehicle.objects.filter(pk=pk).first()
        if vehicle is None:
            return Response({"error": "There is no vehicle with that id"}, status=status.HTTP_400_BAD_REQUEST)
        if len(vehicle.delivery_batches.all()) > 0:
            vehicle.is_loaded = True
            vehicle.save()
            return Response({"message": "Successfully loaded"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Vehicle does not have any delivery batches in it."}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['PATCH', 'PUT'], detail=True)
    def unload_delivery_batch(self, request, pk):
        delivery_batch_id = request.data.get('id')
        if delivery_batch_id is None:
            return Response({"error": 'There is no delivery batch id supplied in the request.'},
                            status=status.HTTP_400_BAD_REQUEST)
        vehicle = Vehicle.objects.filter(pk=pk).first()
        if vehicle is None:
            return Response({"error": 'There is no vehicle with that id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            delivery_batch = DeliveryBatch.objects.get(pk=delivery_batch_id)
        except ObjectDoesNotExist:
            return Response({"error": "Delivery batch with ID %d not found" % delivery_batch_id},
                            status=status.HTTP_404_NOT_FOUND)

        # Delete the delivery batch
        delivery_batch.delete()



        # Vehicle save is not required after delete (commented out)
        # vehicle.save()

        return Response({"message": "Delivery batch unloaded successfully"}, status=status.HTTP_200_OK)

    @action(methods=['PUT', 'PATCH'], detail=True)
    def unload_vehicle(self, request, pk):
        vehicle = Vehicle.objects.filter(pk=pk).first()
        if vehicle is None:
            return Response({"error": "There is no vehicle with that id."}, status=status.HTTP_400_BAD_REQUEST)

        if len(vehicle.delivery_batches.all()) == 0:
            vehicle.is_loaded = False
        else:
            return Response({"error": "There are delivery batches in this vehicle and so it cannot be set as unloaded"}, status=status.HTTP_400_BAD_REQUEST)

        vehicle.save()
        return Response({"message": "Vehicle set as unloaded"}, status=status.HTTP_200_OK)





        # if FleetSubscription.get_instance().available_slots_left():
        #     vehicle.allocate()
        #     driver = DeliveryBatch.objects.get(pk=driver_id)
        #
        #     # Assign delivery batch to the vehicle (considering ManyToMany or ForeignKey)
        #     vehicle.delivery_batches.add(driver)  # Assuming ManyToMany relationship
        #     # OR
        #     # vehicle.driver = driver  # If ForeignKey relationship
        #
        #     vehicle.save()  # Save changes to the vehicle instance
        #
        #     # Return a serialized response (adapt based on your serializer)
        #     # serializer = DeliveryBatchAssignmentSerializer(driver)
        #     return Response("Assignment Successful", status=status.HTTP_200_OK)
        # else:
        #     return Response({'error': "No more subscribed vehicles."}, status=status.HTTP_400_BAD_REQUEST)


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    @action(detail=False, methods=['post'])
    def add_contact_and_user(self, request):
        name = request.data.get('name')
        login_enabled = request.data.get('login_enabled')
        username = request.data.get('username')
        password = request.data.get('password')

        contact = Contact.objects.create(name=name, login_enabled=login_enabled)
        if login_enabled:
            user = User.objects.create_user(username=username, password=password)
            contact.user = user
            user.save()
        contact.save()

        return Response(ContactSerializer(instance=contact).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete_contact_and_user(self, request, pk=None):
        instance = Contact.objects.get(pk=pk)
        if instance.user is not None:
            user = instance.user
            instance.delete()
            user.delete()
        else:
            instance.delete()
        return Response('Deleted', status.HTTP_200_OK)

    @action(detail=True, methods=['patch', 'put'])
    def edit_contact_and_user(self, request, pk=None):
        name = request.data.get('name')
        login_enabled = request.data.get('login_enabled')
        username = request.data.get('username')
        password = request.data.get('password')

        contact = Contact.objects.get(pk=pk)
        # user = contact.user
        contact.name = name
        if login_enabled is False:
            if contact.user is not None:
                contact.user.delete()
            contact.login_enabled = False
        elif login_enabled is True:
            if contact.user is None:
                user = User.objects.create_user(username=username, password=password)
                contact.user = user
                user.save()
            contact.login_enabled = True
            contact.user.username = username

        contact.save()
        return Response(ContactSerializer(instance=contact).data, status.HTTP_200_OK)


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    @action(methods=['GET'], detail=False)
    def get_driver_of_user(self, request):
        contact_id = request.user.contact.pk
        driver = Driver.objects.filter(contact__id=contact_id).first()
        if driver is not None:
            serializer = DriverSerializer(driver)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No driver found with that contact id"}, status=status.HTTP_400_BAD_REQUEST)


def get_user_group(request):
    if request.user:
        return Response(request.user.groups, status.HTTP_200_OK)
    else:
        return Response('Unauthorized', status.HTTP_401_UNAUTHORIZED)


def get_subscribed_vehicles(request):
    return HttpResponse(f"{FleetSubscription.get_instance().total_slots}", status=status.HTTP_200_OK)
