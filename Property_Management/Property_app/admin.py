from django.contrib import admin

# Register your models here.
from .models import Property,PropertyImage,Unit,Tenant,Lease,Issue
admin.site.register(Property)
admin.site.register(PropertyImage)
admin.site.register(Unit)
admin.site.register(Tenant)
admin.site.register(Lease)
admin.site.register(Issue)
