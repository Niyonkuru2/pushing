from django.shortcuts import render,redirect,get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from .serializers import PropertySerializer,PropertyImageSerializer,UnitSerializer,LeaseSerializer,TenantSerializer
from .models import Property, Unit,Lease,Issue,Tenant
from django.db.models import Q
from django.http import JsonResponse
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages

# Api To register user

def register_user(request):
    """API to register user in the system"""
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
    """API to login user in the system"""
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

def logout_user(request):
    """API to logout user from the system"""
    logout(request)
    return redirect('/')

@api_view(['GET'])
def get_allprop(request):
    """API to get fast 6 property to index.html"""
    properties = Property.objects.all().order_by('-created_at')[:6]
    serializer = PropertySerializer(properties, many=True, context={'request': request})
    return render(request, 'index.html', {'properties': serializer.data})
     

api_view(['GET'])
def get_single_property(request, pk):
    """API to get single property and thier details on propertyDetail.html"""
    try:
        property = Property.objects.get(pk=pk)
        return render(request, 'properties/propertyDetail.html', {'property': property})
    except Property.DoesNotExist:
        return render(request, '404.html', status=404)
 
@api_view(['GET'])
def search_properties(request):
    """API to search properties depend on name and address on search.html"""
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

api_view(['GET'])
def apartment(request):
    """API To filter Appartment on appartment.html template"""
    apartments = Property.objects.filter(property_type='Appartment')
    return render(request, 'categories/appartment.html', {'properties': apartments})

api_view(['GET'])
def hause(request):
    """API To filter house on house.html template"""
    houses = Property.objects.filter(property_type='House')
    return render(request, 'categories/house.html', {'properties': houses})

api_view(['GET'])
def commercial(request):
    """API To filter Filter on Filter.html template"""
    commercials = Property.objects.filter(property_type='Commercial')
    return render(request, 'categories/commercial.html', {'properties': commercials})

def about(request):
   """ View to get About.html template"""
   return render(request, 'webinfo/about.html')

def contact(request):
    """ View to get Contact.html template"""
    return render(request,'webinfo/contact.html')

@api_view(['POST', 'GET'])
def add_property(request):
    """API To add property by rendering addProperty.html template to input data"""
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


def get_property_for_tenant(request):
    """ API to get All property releted to Landrolrd"""
    if not request.user.is_authenticated:
        return redirect('login_user')

    owner = request.user
    properties = Property.objects.filter(owner=owner)

    if not properties.exists():
        return render(request, 'properties/myProperty.html', {'properties': []})

    return render(request, 'properties/myProperty.html', {'properties': properties})

@api_view(['POST', 'GET'])
def single_property(request, pk):
    """API to get Single property and edit its attribute"""
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
        

def property_units(request, pk):
    """API to get unit associated to a property if is available"""
    try:
        property = Property.objects.get(pk=pk)
        units = property.units.all()
        return render(request, 'properties/unitProperty.html', {'property': property, 'units': units})
    
    except Property.DoesNotExist:
        return render(request, '404.html', {"detail": "Property not found."})        


@api_view(['POST', 'GET'])
def upload_property_image(request):
    """API to Upload Images of property once landlord has add property to the system"""
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



def delete_property(request, pk):
    """API to delete a Property"""
    property = get_object_or_404(Property, pk=pk)
    property.delete()
    return redirect('get_property_for_tenant') 



@api_view(['POST', 'GET'])
def add_unit(request):
    """API to add Unit associated to landload"""
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
    

def get_unit_for_tenant(request):
    """API to get unit associated to landload"""
    if not request.user.is_authenticated:
        messages.error(request, "Login To Continue.")
        return redirect('login_user')
    try:
        properties = Property.objects.filter(owner=request.user)
        units = Unit.objects.filter(property__in=properties)
        return render(request, 'units/myUnits.html', {'units': units})
    except Property.DoesNotExist:
        return messages.error("Product not found.")


@api_view(['GET'])  
def get_single_unit(request, pk):
    """API to get single unit and their details unitDetail.html"""
    try:
        unit = Unit.objects.get(pk=pk)
        property = unit.property 
        return render(request, 'units/unitDetail.html', {'unit': unit, 'property': property})
    except Unit.DoesNotExist:
        return redirect('get_single_property', pk=pk)

@api_view(['POST', 'GET'])
def single_unit(request, pk):
    """API to Edit unit """
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


def delete_unit(request, pk):
    """API to delete a unit"""
    unit = get_object_or_404(Unit, pk=pk)
    unit.delete()
    return redirect('get_unit_for_tenant')

#Api to interact with Lease Model

@api_view(['GET'])
def get_leases_for_tenant(request):
    """API to get leases assigned to a landload"""
    if not request.user.is_authenticated:
        messages.error(request, "Authentication is required.")
        return redirect('login') 

    tenant = request.user
    leases = Lease.objects.filter(tenant=tenant)

    if not leases.exists():
        return render(request, 'leases/myLease.html', {'leases': []})

    return render(request, 'leases/myLease.html', {'leases': leases})


def single_lease(request, pk):
    """API to get single lease assigned to a landload"""
    lease = get_object_or_404(Lease, pk=pk)
    return render(request, 'leases/leaseDetail.html', {'lease': lease})

 
@api_view(['GET', 'POST'])
def add_lease(request):
    """API to add lease between a landloard and a buyer on a property"""
    if not request.user.is_authenticated:
        messages.error(request, "Login to continue.")
        return redirect('login_user')

    if request.method == 'GET':
        units = Unit.objects.filter(property__owner=request.user)
        buyers = Tenant.objects.all()
        if not units.exists():
            return render(request, 'units/addUnit.html', {
                'message': "You don't have any units to add a lease for. Add a unit to continue."
            })

        return render(request, 'leases/addLease.html', {'units': units, 'buyers': buyers})

    if request.method == 'POST':
        units = Unit.objects.filter(property__owner=request.user)
        if not units.exists():
            messages.error(request, "You don't have any units to add a lease for. Add a unit to continue.")
            return redirect('add_unit')
        data = request.POST.copy()
        data['tenant'] = request.user.id
        serializer = LeaseSerializer(data=data)
        if serializer.is_valid():
            try:
                unit_id = data.get('unit')
                unit = Unit.objects.get(id=unit_id)

                if unit.property.owner != request.user:
                    messages.error(request, "You are not the owner of this unit, so you cannot create a lease for it.")
                    return redirect('add_lease')
                buyer_id = data.get('buyer')
                buyer = Tenant.objects.get(id=buyer_id)
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


@api_view(['GET', 'POST',])
def edit_lease(request, pk):
    """API to edit Lease for landload"""
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


@api_view(['GET'])
def get_leases_for_client_or_tenant(request):
    """API to get list of buyers to landlord property"""
    if not request.user.is_authenticated:
        return redirect('login') 

    tenant = request.user
    leases = Lease.objects.filter(tenant=tenant)

    if not leases.exists():
        return render(request, 'lease/my_lease.html', {'leases': []})

    return render(request, 'lease/my_lease.html', {'leases': leases})


@api_view(['GET'])
def get_leases_for_client(request):
    """API to get A lease on buyer side """
    if not request.user.is_authenticated:
        return redirect('login')
    owned_units = Unit.objects.filter(property__owner=request.user)
    leases = Lease.objects.filter(unit__in=owned_units)

    return render(request, 'leases/my_contract.html', {'leases': leases})

 
@api_view(['GET'])
def track_my_lease_on_other_side(request):
    """API to track leases  landlord has to ather landlord"""
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        buyer = Tenant.objects.get(user=request.user)
    except Tenant.DoesNotExist:
        return render(request, 'leases/track_my_lease_on_other.html', {'leases': []})
    leases = Lease.objects.filter(buyer=buyer)

    return render(request, 'leases/track_my_lease_on_other.html', {'leases': leases})

def delete_lease(request, pk):
    """API to delete Lease"""
    lease = get_object_or_404(Lease, pk=pk)
    lease.delete()
    return redirect('get_leases_for_tenant')  

#API To interact with Issue Model

def report_issue(request, lease_id):
    """API to let a client lise issue to the owner of a property"""
    if not request.user.is_authenticated:
        return redirect('login_user') 
    
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


def owner_notifications(request):
    """API to send notification to landlord when client rise an issue"""
    if not request.user.is_authenticated:
        return redirect('login')
    issues = Issue.objects.filter(lease__unit__property__owner=request.user).order_by('-created_at')
    return render(request, 'notifications/owner_notifications.html', {'issues': issues})

def mark_issue_as_read(request, issue_id):
    """API to handle Read notification if the landlord read it"""
    issue = Issue.objects.get(id=issue_id, lease__unit__property__owner=request.user)
    issue.is_read = True
    issue.save()
    return redirect('owner_notifications')


# API To interact with tenant model

@api_view(['GET', 'POST'])
def add_tenant(request):
    """API to add Tenant and make sure whether tenant added once"""
    if not request.user.is_authenticated:
        return redirect('login_user')
    

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

def get_single_tenant(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    return render(request, 'tenants/tenantDetail.html', {'tenant': tenant})


def get_info_for_user(request):
    tenants = Tenant.objects.filter(user=request.user)
    return render(request, 'tenants/myInfo.html', {'tenants': tenants})


@api_view(['POST', 'GET'])
def edit_tenant(request, pk):
    """API to edit the Tenant and make sure record in user model also edited"""
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
        

# admin dashboard

@api_view(['GET'])
def get_allproperties(request):
    """API to get all property in admin dashboard"""
    properties = Property.objects.prefetch_related('images').all()
    return render(request, 'admin/Property/allProperty.html', {'properties': properties})


@api_view(['GET'])
def get_allunits(request):
    """API to get all Unit in admin dashboard"""
    units = Unit.objects.all()
    return render(request,'admin/Unit/allUnit.html',{'units':units})

@api_view(['GET'])
def get_allleases(request):
    """API to get all Lease in admin dashboard"""
    leases = Lease.objects.all()
    return render(request,'admin/lease/allLease.html',{'leases':leases})
 
@api_view(['GET'])
def get_alltenants(request):
    """API to get all Tenants in admin dashboard"""
    tenants = Tenant.objects.all()
    return render(request,'admin/Tenant/allTenant.html',{'tenants':tenants})
 
@api_view(['POST', 'GET'])
def admin_add_property(request):
    """API to add property in admin dashboard"""
    if not request.user.is_authenticated:
        messages.error(request, "Login To Continue.")
        return redirect('login_user')

    if request.method == 'GET':
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

@api_view(['POST', 'GET'])
def admin_upload_property_image(request):
    """API to upload images on property in admin dashboard"""
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
        else:
            messages.error(request, "Failed to upload image. Please check your inputs.")
        
        return redirect('admin_upload_property_image')


def admin_update_property(request, property_id):
    """API to update property in admin dashboard"""
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

def admin_delete_property(request, pk):
    """API to delete a Property"""
    property = get_object_or_404(Property, pk=pk)
    property.delete()
    return redirect('get_allproperties') 

def admin_add_unit(request):
    """API to add Unit for admin side """
    if not request.user.is_authenticated:
        return redirect('login_user')
    
    if request.method == 'GET':
        properties = Property.objects.all()
        
        if not properties.exists():
            return render(request, 'admin/Property/addProperty.html', {
                'message': "No property to add unit for"
            })

        return render(request, 'admin/Unit/addUnit.html', {'properties': properties})

    if request.method == 'POST':
        properties = Property.objects.all()

        if not properties.exists():
            return redirect('admin_add_property')

        serializer = UnitSerializer(data=request.POST)
        if serializer.is_valid():
            property = serializer.validated_data.get('property')
            if property:
                serializer.save()
                return redirect('get_allunits')
    
@api_view(['POST', 'GET'])
def admin_edit_unit(request, pk):
    """API to Edit unit """
    if not request.user.is_authenticated:
        return redirect('login_user')
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'GET':
        return render(request, 'admin/Unit/editUnit.html', {'unit': unit})
    elif request.method == 'POST':
        serializer = UnitSerializer(unit, data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect('get_single_unit', pk=unit.pk)
        return render(request, 'admin/Unit/editUnit.html', {'unit': unit, 'errors': serializer.errors})

def admin_delete_unit(request, pk):
    """API to delete a Property"""
    unit = get_object_or_404(Unit, pk=pk)
    unit.delete()
    return redirect('get_allunits') 

@api_view(['GET', 'POST'])
def admin_add_lease(request):
    """API to add lease between a landlord and a buyer on a property on the admin side."""
    if not request.user.is_authenticated:
        return redirect('login_user')

    if request.method == 'GET':
        units = Unit.objects.all()
        buyers = Tenant.objects.all()
        tenants = User.objects.all()

        if not units.exists():
            return render(request, 'admin/Unit/addUnit.html', {
                'message': "No units available. Please add units first."
            })

        return render(request, 'admin/Lease/addLease.html', {
            'units': units,
            'buyers': buyers,
            'tenants': tenants
        })

    if request.method == 'POST':
        data = request.POST.copy()
        units = Unit.objects.all()
        if not units.exists():
            messages.error(request, "No units available. Please add units first.")
            return redirect('admin_add_unit')
        serializer = LeaseSerializer(data=data)
        if serializer.is_valid():
            try:
                unit = Unit.objects.get(id=data.get('unit'))
                tenant = User.objects.get(id=data.get('tenant'))
                buyer = Tenant.objects.get(id=data.get('buyer'))

                # Save the lease
                serializer.save(unit=unit, tenant=tenant, buyer=buyer)
                messages.success(request, "Lease created successfully.")
                return redirect('get_allleases')

            except (Unit.DoesNotExist, User.DoesNotExist, Tenant.DoesNotExist) as e:
                messages.error(request, f"Error: {str(e)}")
                return redirect('admin_add_lease')
        else:
            return redirect('admin_add_lease')


@api_view(['GET', 'POST'])
def admin_edit_lease(request,pk):
    """API to edit an existing lease on the admin side."""
    if not request.user.is_authenticated:
        return redirect('login_user')

    try:
        lease = Lease.objects.get(id=pk)
    except Lease.DoesNotExist:
        messages.error(request, "Lease not found.")
        return redirect('get_allleases')

    if request.method == 'GET':
        units = Unit.objects.all()
        buyers = Tenant.objects.all()
        tenants = User.objects.all()

        return render(request, 'admin/Lease/editLease.html', {
            'lease': lease,
            'units': units,
            'buyers': buyers,
            'tenants': tenants
        })

    if request.method == 'POST':
        data = request.POST.copy()
        serializer = LeaseSerializer(instance=lease, data=data, partial=True)
        if serializer.is_valid():
            try:
                unit = Unit.objects.get(id=data.get('unit'))
                tenant = User.objects.get(id=data.get('tenant'))
                buyer = Tenant.objects.get(id=data.get('buyer'))

                
                serializer.save(unit=unit, tenant=tenant, buyer=buyer)
                messages.success(request, "Lease updated successfully.")
                return redirect('get_allleases')

            except (Unit.DoesNotExist, User.DoesNotExist, Tenant.DoesNotExist) as e:
                messages.error(request, f"Error: {str(e)}")
                return redirect('admin_edit_lease', lease_id=pk)
        else:
            messages.error(request, "Invalid data provided. Please check and try again.")
            return redirect('admin_edit_lease', lease_id=pk)

def admin_delete_lease(request, pk):
    """API to delete a Property"""
    lease = get_object_or_404(Lease, pk=pk)
    lease.delete()
    return redirect('get_allleases') 

@api_view(['POST', 'GET'])
def admin_add_tenant(request):
    """
    API to add a new Tenant and create a corresponding record in the User model.
    """
    if request.method == 'GET':
        return render(request, 'admin/Tenant/addTenant.html')

    elif request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        username = email.split('@')[0]

        # Check if all fields are provided
        if not all([first_name, last_name, email, phone_number]):
            messages.error(request, "All fields are required.")
            return render(request, 'admin/Tenant/addTenant.html')

        try:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            Tenant.objects.create(user=user, phone_number=phone_number)

            return redirect('get_alltenants')

        except Exception:
            return render(request, 'admin/Tenant/addTenant.html')

@api_view(['POST', 'GET'])
def admin_edit_tenant(request, pk):
    """API to edit the Tenant and make sure record in user model also edited for admin side"""
    tenant = get_object_or_404(Tenant, pk=pk)
    if request.method == 'GET':
        return render(request, 'admin/Tenant/editTenant.html', {
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
            return redirect('get_alltenants')

        except Exception:
            return render(request, 'admin/Tenant/editTenant.html', {'tenant': tenant})
        

# Payment Integrations Apis

stripe.api_key = settings.STRIPE_SECRET_KEY

def process_payment(request, pk):
    if not request.user.is_authenticated:
        return redirect('login_user')
    
    unit = get_object_or_404(Unit, id=pk)
    if request.method == "POST":
        try:
            # Create a Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'{unit.property.name} - Unit {unit.unit_number}',
                        },
                        'unit_amount': int(unit.rent * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/payment/success/') + f'?unit_id={unit.id}',
                cancel_url=request.build_absolute_uri('/payment/cancel/'),
            )
            return JsonResponse({'id': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return render(request, 'payment/process_payment.html', {
    'unit': unit,
    'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
})
    

def payment_success(request):
    unit_id = request.GET.get('unit_id')
    unit = get_object_or_404(Unit, id=unit_id)
    unit.payment_status = True
    unit.is_Available = False
    unit.save()
    messages.success(request, "Payment successful!")
    return render(request, 'payment/payment_success.html', {
        'unit': unit
    })

def payment_cancel(request):
    messages.error(request, "Payment canceled.")
    return render(request, 'payment/payment_cancelled.html')
