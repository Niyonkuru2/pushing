from django.shortcuts import render,redirect,get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from .serializers import PropertySerializer,UnitSerializer,LeaseSerializer,TenantSerializer,PropertyImageSerializer
from .models import Property ,Unit,Lease,Tenant,Issue
from django.db.models import Q
from django.conf import settings
import stripe
from django.http import JsonResponse
stripe.api_key = settings.STRIPE_SECRET_KEY



# Api To register user

def register_user(request):
    if request.method == 'POST':
        first_name= request.POST['first_name']
        last_name= request.POST['first_name']
        username= request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        repeatPassword=request.POST['repeatPassword']
        if password == repeatPassword:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    )
                user.save()
                return redirect('login_user')
            except:
                error_message='Error creating account'
                return render(request, 'register.html',{'error_message':error_message})
        else:
            error_message='Password do not match'
            return render(request, 'register.html',{'error_message':error_message})
    return render(request,'register.html')

def login_user(request):
    if request.method == 'POST':
        username= request.POST['username']
        password=request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            print(f"User logged in: {user}")
            return redirect('/')
        else:
            error_message="Imvalid username or password"
            return render(request, 'login.html',{'error_message':error_message})
    return render(request,'login.html')

#logout user
def logout_user(request):
    logout(request)
    return redirect('/')

#Api to interact with property model
# get all
@api_view(['GET'])
def get_allprop(request):
    properties = Property.objects.all().order_by('-created_at')[:6]
    serializer = PropertySerializer(properties, many=True, context={'request': request})
    return render(request, 'index.html', {'properties': serializer.data})

# Load only properties property_type of Appartment
api_view(['GET'])
def apartment(request):
    apartments = Property.objects.filter(property_type='Appartment')
    return render(request, 'categories/appartment.html', {'properties': apartments})

# Load only properties property_type of House
api_view(['GET'])
def hause(request):
    houses = Property.objects.filter(property_type='House')
    return render(request, 'categories/house.html', {'properties': houses})

# Load only properties property_type of Commercial
api_view(['GET'])
def commercial(request):
    commercials = Property.objects.filter(property_type='Commercial')
    return render(request, 'categories/commercial.html', {'properties': commercials})

# add property api
@api_view(['POST', 'GET'])
def add_property(request):
    if not request.user.is_authenticated:
        return redirect('login_user')

    if request.method == 'GET':
        return render(request, 'properties/addProperty.html')

    if request.method == 'POST':
        data = request.data.copy()
        data['owner'] = request.user.id

        serializer = PropertySerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return redirect('upload_property_image')
        else:
            return render(request, 'properties/addProperty.html', {
                'errors': serializer.errors,
                'form_data': request.data
            })

# Get unity assigned to property
def property_units(request, pk):
    try:
        property = Property.objects.get(pk=pk)
        units = property.units.all()
        return render(request, 'properties/unitProperty.html', {'property': property, 'units': units})
    
    except Property.DoesNotExist:
        return render(request, '404.html', {"detail": "Property not found."})        

# get property of to tenant
def get_property_for_tenant(request):
    if not request.user.is_authenticated:
        messages.error(request, "Login to continue.")
        return redirect('login_user')

    owner = request.user
    properties = Property.objects.filter(owner=owner)

    if not properties.exists():
        return render(request, 'properties/myProperty.html', {'properties': []})

    return render(request, 'properties/myProperty.html', {'properties': properties})

# Single property
api_view(['GET'])
def get_single_property(request, pk):
    try:
        property = Property.objects.get(pk=pk)
        return render(request, 'properties/propertyDetail.html', {'property': property})
    except Property.DoesNotExist:
        return render(request, '404.html', status=404)
 
# Search product 
@api_view(['GET'])
def search_properties(request):
    if not request.user.is_authenticated:
        messages.error(request, "Login To Continue.")
        return redirect('login_user')
    
    query = request.GET.get('q', '')
    if query:
        properties = Property.objects.filter(
            Q(name__icontains=query) | Q(address__icontains=query)
        )
    else:
        properties = Property.objects.all()
    properties = properties.prefetch_related('images')
    return render(request, 'search.html', {'properties': properties})

# Editing product
@api_view(['POST', 'GET'])
def single_property(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Login To Continue.")
        return redirect('login_user')

    property = get_object_or_404(Property, pk=pk)

    if property.owner != request.user:
        messages.error(request, "You are not allowed to edit this Property")
        return redirect('get_property_for_tenant')

    if request.method == 'GET':
        return render(request, 'properties/editProperty.html', {'property': property})

    if request.method == 'POST':
        parser_classes = [MultiPartParser, FormParser]

        data = request.data.copy()
        serializer = PropertySerializer(
            property, 
            data=data, 
            context={'request': request}, 
            partial=True 
        )

        if serializer.is_valid():
            serializer.save()
            return redirect('get_single_property', pk=pk)
        else:
            return render(request, 'properties/editProperty.html', {
                'property': property,
                'errors': serializer.errors
            })

# Deleting Product
def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property.delete()
    return redirect('get_property_for_tenant') 

#api interact with unit model
# api to add unit
@api_view(['POST', 'GET'])
def add_unit(request):
    if not request.user.is_authenticated:
        messages.error(request, "Authentication is required.")
        return redirect('login_user')
    
    if request.method == 'GET':
        properties = Property.objects.filter(owner=request.user)
        
        if not properties.exists():
            return render(request, 'properties/addProperty.html', {
                'message': "You don't have any properties to add a unit for. Add a property to continue."
            })

        return render(request, 'units/addUnit.html', {'properties': properties})

    if request.method == 'POST':
        properties = Property.objects.filter(owner=request.user)

        if not properties.exists():
            messages.error(request, "You don't have any properties to add a unit for. Add a property to continue.")
            return redirect('add_property')

        serializer = UnitSerializer(data=request.POST)
        if serializer.is_valid():
            property = serializer.validated_data.get('property')
            if property.owner == request.user:
                serializer.save()
                return redirect('get_unit_for_tenant')
            else:
                messages.error(request, "You are not authorized to add units to this property.")
    
# get property related to tenant
def get_unit_for_tenant(request):
    if not request.user.is_authenticated:
        messages.error(request, "Login To Continue.")
        return redirect('login_user')
    try:
        properties = Property.objects.filter(owner=request.user)
        units = Unit.objects.filter(property__in=properties)
        return render(request, 'units/myUnits.html', {'units': units})
    except Property.DoesNotExist:
        return messages.error("Product not found.")

# get single unit
@api_view(['GET'])  
def get_single_unit(request, pk):
    try:
        unit = Unit.objects.get(pk=pk)
        property = unit.property 
        return render(request, 'units/unitDetail.html', {'unit': unit, 'property': property})
    except Unit.DoesNotExist:
        return redirect('get_single_property', pk=pk)

# Editing unit
@api_view(['POST', 'GET'])
def single_unit(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Login To Continue.")
        return redirect('login_user')
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'GET':
        return render(request, 'units/editUnit.html', {'unit': unit})
    elif request.method == 'POST':
        serializer = UnitSerializer(unit, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect('get_single_unit', pk=unit.pk)
        return render(request, 'units/editUnit.html', {'unit': unit, 'errors': serializer.errors})

# Deleting Unit
def delete_unit(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    unit.delete()
    return redirect('get_unit_for_tenant')  

#Api to interact with Lease Model
# Get all lease related to tenant
@api_view(['GET'])
def get_leases_for_tenant(request):
    if not request.user.is_authenticated:
        messages.error(request, "Authentication is required.")
        return redirect('login') 

    tenant = request.user
    leases = Lease.objects.filter(tenant=tenant)

    if not leases.exists():
        return render(request, 'leases/myLease.html', {'leases': []})

    return render(request, 'leases/myLease.html', {'leases': leases})

# Get Single Lease
def single_lease(request, pk):
    lease = get_object_or_404(Lease, pk=pk)
    return render(request, 'leases/leaseDetail.html', {'lease': lease})

#Add lease API 
@api_view(['GET', 'POST'])
def add_lease(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "Login to continue.")
        return redirect('login_user')

    # Handle GET request
    if request.method == 'GET':
        # Get units owned by the logged-in user
        units = Unit.objects.filter(property__owner=request.user)
        buyers = Tenant.objects.all()  # Fetch all tenants as potential buyers

        # Check if the user has any units
        if not units.exists():
            return render(request, 'units/addUnit.html', {
                'message': "You don't have any units to add a lease for. Add a unit to continue."
            })

        return render(request, 'leases/addLease.html', {'units': units, 'buyers': buyers})

    # Handle POST request
    if request.method == 'POST':
        # Check if the user has any units
        units = Unit.objects.filter(property__owner=request.user)
        if not units.exists():
            messages.error(request, "You don't have any units to add a lease for. Add a unit to continue.")
            return redirect('add_unit')

        # Create mutable copy of request data
        data = request.POST.copy()
        data['tenant'] = request.user.id  # Set logged-in user as the tenant

        # Validate and save lease using the serializer
        serializer = LeaseSerializer(data=data)
        if serializer.is_valid():
            try:
                # Validate unit ownership
                unit_id = data.get('unit')
                unit = Unit.objects.get(id=unit_id)

                if unit.property.owner != request.user:
                    messages.error(request, "You are not the owner of this unit, so you cannot create a lease for it.")
                    return redirect('add_lease')

                # Fetch and validate buyer
                buyer_id = data.get('buyer')
                buyer = Tenant.objects.get(id=buyer_id)

                # Save the lease with the buyer
                serializer.save(buyer=buyer)
                messages.success(request, "Lease created successfully.")
                return redirect('get_leases_for_tenant')

            except Unit.DoesNotExist:
                messages.error(request, "The specified unit does not exist.")
                return redirect('add_lease')

            except Tenant.DoesNotExist:
                messages.error(request, "The specified buyer does not exist.")
                return redirect('add_lease')

        else:
            return redirect('add_lease')

#API To edit or delete lease
@api_view(['GET', 'POST',])
def edit_lease(request, pk):
    lease = get_object_or_404(Lease, pk=pk)
    user = request.user
    if not user.is_authenticated:
        return redirect('login_user')
    if lease.unit.property.owner != user:
        messages.error(request, "You are not authorized to modify this lease.")
        return redirect('add_property')
    
    user_units = Unit.objects.filter(property__owner=user)
    buyers = Tenant.objects.all()

    if request.method == 'GET':
        return render(request, 'leases/editLease.html', {'lease': lease, 'units': user_units, 'buyers': buyers})

    if request.method == 'POST':
        data = request.POST.dict()
        data['tenant'] = user.id
        serializer = LeaseSerializer(lease, data=data)
        if serializer.is_valid():
            serializer.save()
            return redirect('single_lease', pk=lease.pk)
        messages.error(request, "Failed to update lease. Please correct the errors below.")
        return render(request, 'leases/editLease.html', {'lease': lease, 'units': user_units, 'buyers': buyers, 'errors': serializer.errors})
# get lease for landlord
@api_view(['GET'])
def get_leases_for_client_or_tenant(request):
    if not request.user.is_authenticated:
        return redirect('login') 

    tenant = request.user
    leases = Lease.objects.filter(tenant=tenant)

    if not leases.exists():
        return render(request, 'lease/my_lease.html', {'leases': []})

    return render(request, 'lease/my_lease.html', {'leases': leases})

#get lease for buyer
@api_view(['GET'])
def get_leases_for_client(request):
    if not request.user.is_authenticated:
        return redirect('login')
    owned_units = Unit.objects.filter(property__owner=request.user)
    leases = Lease.objects.filter(unit__in=owned_units)

    return render(request, 'leases/my_contract.html', {'leases': leases})

# track my lease on other side 
@api_view(['GET'])
def track_my_lease_on_other_side(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        buyer = Tenant.objects.get(user=request.user)
    except Tenant.DoesNotExist:
        return render(request, 'leases/track_my_lease_on_other.html', {'leases': []})
    leases = Lease.objects.filter(buyer=buyer)

    return render(request, 'leases/track_my_lease_on_other.html', {'leases': leases})

# Deleting Lease
def delete_lease(request, pk):
    lease = get_object_or_404(Lease, pk=pk)
    lease.delete()
    return redirect('get_leases_for_tenant')  

# API To interact with tenant model
# Add Tenant API
@api_view(['GET', 'POST'])
def add_tenant(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    
    # Check if the user already has a tenant profile
    existing_tenant = Tenant.objects.filter(user=request.user).first()
    if existing_tenant:
        messages.info(request, "You already have a tenant profile. Redirecting to your information page.")
        return redirect('get_info_for_user') 
    
    if request.method == 'POST':
        data = request.data.copy()
        data['user'] = request.user.id 
        
        serializer = TenantSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return redirect('get_info_for_user')
        else:
            return render(request, 'tenants/addTenant.html', {
                'errors': serializer.errors,
                'data': request.data
            })
    
    return render(request, 'tenants/addTenant.html')
#Get single
def get_single_tenant(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    return render(request, 'tenants/tenantDetail.html', {'tenant': tenant})

# single tenant 
def get_info_for_user(request):
    tenants = Tenant.objects.filter(user=request.user)
    return render(request, 'tenants/myInfo.html', {'tenants': tenants})

# API To edit  tenant
@api_view(['POST', 'GET'])
def edit_tenant(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    if tenant.user is None or tenant.user.id != request.user.id:
        messages.error(request, "You are not authorized to edit this tenant.")
        return redirect('tenant_list')
    if request.method == 'GET':
        return render(request, 'tenants/editTenant.html', {
            'tenant': tenant,
            'tenant_data': {
                'id': tenant.id,
                'user': tenant.user.id,
                'first_name': tenant.user.first_name,
                'last_name': tenant.user.last_name,
                'email': tenant.user.email,
                'phone_number': tenant.phone_number,
            },
        })

    elif request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        if not all([first_name, last_name, email, phone_number]):
            messages.error(request, "All fields are required.")
            return render(request, 'tenants/editTenant.html', {'tenant': tenant})

        try:
            tenant.user.first_name = first_name
            tenant.user.last_name = last_name
            tenant.user.email = email
            tenant.user.save()
            tenant.phone_number = phone_number
            tenant.save()
            return redirect('get_single_tenant', pk=tenant.pk)

        except Exception:
            return render(request, 'tenants/editTenant.html', {'tenant': tenant})

#api to report issue
def report_issue(request, lease_id):
    if not request.user.is_authenticated:
        return redirect('login_user')  # Redirect to login if the user is not authenticated
    
    if request.method == 'POST':
        try:
            lease = Lease.objects.get(id=lease_id, buyer__user=request.user)
        except Lease.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Lease not found or you do not have permission to report issues on this lease.'}, status=404)
        
        description = request.POST.get('description', '')
        
        if description:
            Issue.objects.create(lease=lease, description=description)
            return JsonResponse({'success': True, 'message': 'Issue reported successfully!'})
        
        return JsonResponse({'success': False, 'message': 'Description is required.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

#issue notification
def owner_notifications(request):
    if not request.user.is_authenticated:
        return redirect('login')
    issues = Issue.objects.filter(lease__unit__property__owner=request.user).order_by('-created_at')
    return render(request, 'notifications/owner_notifications.html', {'issues': issues})

# mark as read
def mark_issue_as_read(request, issue_id):
    issue = Issue.objects.get(id=issue_id, lease__unit__property__owner=request.user)
    issue.is_read = True
    issue.save()
    return redirect('owner_notifications')

#load Contact page
def contact(request):
    print("About page accessed!")
    return render(request,'webinfo/contact.html')
#load About Us page
def about(request):
   return render(request, 'webinfo/about.html')

# upload images
@api_view(['POST', 'GET'])
def upload_property_image(request):
    if not request.user.is_authenticated:
        messages.error(request, "Authentication is required.")
        return redirect('login_user')

    if request.method == 'GET':
        properties = Property.objects.filter(owner=request.user)
        return render(request, 'properties/propertyImages.html', {'properties': properties})

    if request.method == 'POST':
        property_id = request.data.get('property')
        image = request.FILES.get('image')

        if not property_id or not image:
            messages.error(request, "Property and image are required.")
            return redirect('upload_property_image')

        property_instance = Property.objects.get(id=property_id) 
        serializer = PropertyImageSerializer(data={'property': property_instance.id, 'image': image})

        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Image uploaded successfully.")
            return redirect('upload_property_image') 
        else:
            messages.error(request, "Failed to upload image.")
            return redirect('upload_property_image') 

# admin dashboard
# get all prop
@api_view(['GET'])
def get_allproperties(request):
    properties = Property.objects.prefetch_related('images').all()
    return render(request, 'admin/Property/allProperty.html', {'properties': properties})

# get all units
@api_view(['GET'])
def get_allunits(request):
    units = Unit.objects.all()
    return render(request,'admin/Unit/allUnit.html',{'units':units})

# get all leases 
@api_view(['GET'])
def get_allleases(request):
    leases = Lease.objects.all()
    return render(request,'admin/lease/allLease.html',{'leases':leases})
 
 # add property for admin
@api_view(['POST', 'GET'])
def admin_add_property(request):
    if not request.user.is_authenticated:
        messages.error(request, "Login To Continue.")
        return redirect('login_user')

    if request.method == 'GET':
        # Fetch all users to display in the form
        users = User.objects.all()
        return render(request, 'admin/Property/addProperty.html', {'users': users})

    if request.method == 'POST':
        data = request.POST.copy()
        owner_id = data.get('owner')
        if not owner_id:
            return render(request, 'admin/Property/addProperty.html', {
                'errors': {"owner": ["This field is required."]},
                'form_data': data,
            })
        owner = get_object_or_404(User, id=owner_id)
        data['owner'] = owner.id 
        serializer = PropertySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Property added successfully.")
            return redirect('upload_property_image')
        else:
            return render(request, 'admin/Property/addProperty.html', {
                'errors': serializer.errors,
                'form_data': data,
            })

# handle image upload for admin
@api_view(['POST', 'GET'])
def admin_upload_property_image(request):
    if not request.user.is_authenticated:
        return redirect('login_user')

    if request.method == 'GET':
        properties = Property.objects.all()
        return render(request, 'admin/Property/imageUpload.html', {'properties': properties})

    if request.method == 'POST':
        property_id = request.POST.get('property')
        image = request.FILES.get('image')
        if not property_id or not image:
            messages.error(request, "Both property and image are required.")
            return redirect('admin_upload_property_image')
        property_instance = get_object_or_404(Property, id=property_id)
        serializer = PropertyImageSerializer(data={'property': property_instance.id, 'image': image})
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Image uploaded successfully.")
        else:
            messages.error(request, "Failed to upload image. Please check your inputs.")
        
        return redirect('admin_upload_property_image')

# Admin add image 
def admin_update_property(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        data = request.POST
        serializer = PropertySerializer(property_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return redirect('property_list')
        else:
            return render(request, 'admin/Property/editProp.html', {
                'errors': serializer.errors,
                'form_data': data,
                'property': property_instance,
            })
    else:
        return render(request, 'admin/Property/editProp.html', {
            'property': property_instance,
        })

# payment
def create_checkout_session(request, lease_id):
    try:
        lease = Lease.objects.get(id=lease_id)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"Lease Payment - Unit {lease.unit.unit_number}",
                        },
                        'unit_amount': int(lease.rent_Ammount * 100),  # Amount in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/payment-success/'),
            cancel_url=request.build_absolute_uri('/payment-cancel/'),
        )
        return JsonResponse({'id': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
