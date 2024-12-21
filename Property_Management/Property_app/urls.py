from django.urls import path
from . import views
urlpatterns =[
# URL for authentication API
path('user/register',views.register_user,name='register_user'),
path('user/login',views.login_user,name='login_user'),
path('logout/', views.logout_user, name='logout_user'),

# URL to interact with Property model API
path('',views.get_allprop,name='get_allprop'),
path('property/create',views.add_property,name='add_property'),
path('property/image',views.upload_property_image,name='upload_property_image'),
path('property/appartment', views.apartment, name='apartment'),
path('property/house', views.hause, name='house'),
path('property/commercial', views.commercial, name='commercial'),
path('property/units/<int:pk>', views.property_units, name='property_units'),
path('search',views.search_properties,name='search_properties'),
path('property/get/<int:pk>',views.get_single_property,name='get_single_property'),
path('property/<int:pk>',views.single_property,name='single_property'),
path('property/list', views.get_property_for_tenant, name='get_property_for_tenant'),
path('delete-property/<int:pk>/', views.delete_property, name='delete_property'),
path('property/delete/<int:pk>', views.delete_property, name='delete_property'),

# URL to interact Unit model API
path('unit/create',views.add_unit,name='add_unit'),
path('unit/list',views.get_unit_for_tenant,name='get_unit_for_tenant'),
path('unit/get/<int:pk>',views.get_single_unit,name='get_single_unit'),
path('unit/<int:pk>', views.single_unit, name='single_unit'),
path('unit/delete/<int:pk>', views.delete_unit, name='delete_unit'),


# URL to interact Lease model API
path('lease/create',views.add_lease,name='add_lease'),
path('lease/list',views.get_leases_for_tenant,name='get_leases_for_tenant'),
path('lease/<int:pk>',views.edit_lease,name='lease_edit_or_delete'),
path('lease/get/<int:pk>/', views.single_lease, name='single_lease'),
path('lease/delete/<int:pk>', views.delete_lease, name='delete_lease'),

# URL To interact with tenant API 
path('tenant/create',views.add_tenant,name='add_tenant'),
path('tenant/edit/<int:pk>',views.edit_tenant,name='edit_tenant'),
path('tenant/<int:pk>',views.get_single_tenant,name='get_single_tenant'),
path('tenant/list',views.get_info_for_user,name='get_info_for_user'),

# rendering some pages 
path('about/',views.about,name='about'),
path('contact/',views.contact,name='contact'),

# Api for Admin dashboard
path('properties/list',views.get_allproperties,name='get_allproperties'),
path('property/add',views.admin_add_property,name='admin_add_property'),
path('property/imagesupload',views.admin_upload_property_image,name='admin_upload_property_image'),
path('units/list',views.get_allunits,name='get_allunits'),
path('leases/list',views.get_allleases,name='get_allleases'),
]