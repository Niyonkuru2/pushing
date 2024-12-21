from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Property,PropertyImage,Tenant,Lease,Unit

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image','property']

class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'name', 'address', 'property_type', 'description', 'number_of_unit', 'owner', 'images','status']

class UnitSerializer(serializers.ModelSerializer):
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())
    class Meta:
        model=Unit
        fields=['id','property','unit_number','bedroom','bathrom','rent']

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model=Tenant
        fields=['id','user','phone_number']

class LeaseSerializer(serializers.ModelSerializer):
    class Meta:
        model=Lease
        fields=['id','unit','tenant','start_date','end_date','rent_Ammount']
    