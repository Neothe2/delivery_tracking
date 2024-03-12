from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Crate, DeliveryBatch, Customer, Vehicle, Contact, User
from core.serializers import CrateSerializer, DeliveryBatchSerializer, CustomerSerializer, VehicleSerializer, \
    ContactSerializer


class CrateViewSet(viewsets.ModelViewSet):
    queryset = Crate.objects.all()
    serializer_class = CrateSerializer


class DeliveryBatchViewSet(viewsets.ModelViewSet):
    queryset = DeliveryBatch.objects.all()
    serializer_class = DeliveryBatchSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


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




def get_user_group(request):
    if request.user:
        return Response(request.user.groups, status.HTTP_200_OK)
    else:
        return Response('Unauthorized', status.HTTP_401_UNAUTHORIZED)
