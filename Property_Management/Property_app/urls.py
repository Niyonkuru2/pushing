from django.urls import path
from . import views
urlpatterns =[
# URL for authentication API
path('user/register',views.register_user,name='register_user'),
path('user/login',views.login_user,name='login_user'),
path('logout/', views.logout_user, name='logout_user'),

# URL to interact with Property model API
path('',views.get_allprop,name='get_allprop'),
path('search',views.search_properties,name='search_properties'),
path('property/get/<int:pk>',views.get_single_property,name='get_single_property'),
path('property/appartment', views.apartment, name='apartment'),
path('property/house', views.hause, name='house'),
path('property/commercial', views.commercial, name='commercial'),
path('property/create',views.add_property,name='add_property'),
path('property/<int:pk>',views.single_property,name='single_property'),
path('property/list', views.get_property_for_tenant, name='get_property_for_tenant'),
path('property/units/<int:pk>', views.property_units, name='property_units'),
path('property/image',views.upload_property_image,name='upload_property_image'),
path('delete-property/<int:pk>/', views.delete_property, name='delete_property'),

# rendering some pages 
path('about/',views.about,name='about'),
path('contact/',views.contact,name='contact'),

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
path('lease/client',views.get_leases_for_client,name='get_leases_for_client'),
path('lease/tracks',views.track_my_lease_on_other_side,name='track_my_lease_on_other_side'),

#Issues notification
path('report_issue/<int:lease_id>/', views.report_issue, name='report_issue'),
path('owner_notifications/', views.owner_notifications, name='owner_notifications'),
path('mark_issue_as_read/<int:issue_id>/', views.mark_issue_as_read, name='mark_issue_as_read'),

# URL To interact with tenant API 
path('tenant/create',views.add_tenant,name='add_tenant'),
path('tenant/edit/<int:pk>',views.edit_tenant,name='edit_tenant'),
path('tenant/<int:pk>',views.get_single_tenant,name='get_single_tenant'),
path('tenant/list',views.get_info_for_user,name='get_info_for_user'),

# Api for Admin dashboard
path('admins/properties/list',views.get_allproperties,name='get_allproperties'),
path('admins/property/add',views.admin_add_property,name='admin_add_property'),
path('admins/property/imagesupload',views.admin_upload_property_image,name='admin_upload_property_image'),
path('admins/property/edit/<int:property_id>',views.admin_update_property,name='admin_update_property'),
path('admins/delete-property/<int:pk>/', views.admin_delete_property, name='admin_delete_property'),
path('admins/units/list',views.get_allunits,name='get_allunits'),
path('admins/units/adding',views.admin_add_unit,name='admin_add_unit'),
path('admins/units/editing/<int:pk>/',views.admin_edit_unit,name='admin_edit_unit'),
path('admins/unit/delete/<int:pk>/',views.admin_delete_unit,name='admin_delete_unit'),
path('admins/leases/list',views.get_allleases,name='get_allleases'),
path('admins/leases/add',views.admin_add_lease,name='admin_add_lease'),
path('admins/lease/edit/<int:pk>/',views.admin_edit_lease,name='admin_edit_lease'),
path('admins/lease/delete/<int:pk>/',views.admin_delete_lease,name='admin_delete_lease'),
path('admins/tenants/list',views.get_alltenants,name='get_alltenants'),
path('admins/tenant/adding',views.admin_add_tenant,name='admin_add_tenant'),
path('admins/tenant/adit/<int:pk>/',views.admin_edit_tenant,name='admin_edit_tenant'),

#handle Payment By stripe Urls
path('process_payment/<int:pk>/', views.process_payment, name='process_payment'),
path('payment/success/', views.payment_success, name='payment_success'),
path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
]