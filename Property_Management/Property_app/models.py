from django.db import models
from django.contrib.auth.models import User

# property model
from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    Property_types = [
        ('Appartment', 'Appartment'),
        ('House', 'House'),
        ('Commercial', 'Commercial')
    ]
    Property_status = [
        ('Rent', 'Rent'),
        ('Buy', 'Buy')
    ]
    name = models.CharField(max_length=255)
    address = models.TextField()
    property_type = models.CharField(max_length=20, choices=Property_types)
    description = models.TextField(null=True, blank=True)
    number_of_unit = models.PositiveIntegerField()
    owner = models.ForeignKey(User, related_name='properties', on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=10,choices=Property_status,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Properties'

    def __str__(self):
        return self.name

# PropertyImage
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='prop_images/')

    def __str__(self):
        return f"Image for {self.property.name}"


#unit model
class Unit(models.Model):
    property = models.ForeignKey(Property,related_name='units',on_delete=models.CASCADE)
    unit_number = models.PositiveIntegerField()
    bedroom = models.PositiveIntegerField()
    bathrom = models.PositiveIntegerField()
    rent = models.DecimalField(max_digits=8,decimal_places=2)
    is_Available = models.BooleanField(default=True)
    payment_status = models.BooleanField(default=False) 

    def __str__(self):
         return f'{self.property.name} - Unit {self.unit_number}'

# Tenant model
class Tenant (models.Model):
    user = models.ForeignKey(User, related_name='tenant', on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"Tenant: {self.user}" 
# Lease Model

class Lease(models.Model):
    tenant = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    buyer = models.ForeignKey(Tenant,on_delete=models.CASCADE,null=True)
    unit = models.ForeignKey(Unit,on_delete=models.CASCADE,null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    rent_Ammount = models.DecimalField(max_digits=8,decimal_places=2)
    def __str__(self):
        buyer_name = self.buyer.user.username if self.buyer and self.buyer.user else "No buyer"
        return f'Lease for {self.tenant.username} And {buyer_name}'
    
class Issue(models.Model):
    lease = models.ForeignKey('Lease', on_delete=models.CASCADE, related_name='issues')
    description = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Issue for Lease {self.lease.id} - {self.description[:20]}"
