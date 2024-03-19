import random

from django.core.files.storage import FileSystemStorage
from django.db.models import Avg, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .models import *
from datetime import datetime, timedelta

import smtplib
from email.mime.text import MIMEText

from random import random


#####################################Common##########################################

def home(request):
    try:
        obj = Login.objects.get(id=request.session.get('id'))
        if obj.usertype == 'admin':
            request.session['type'] = 'admin'
            return render(request, 'Admins/index.html')
        elif obj.usertype == 'owner':
            if Owner.objects.filter(LOGIN=obj, LOGIN__usertype='Pending'):
                return HttpResponse('You dont have access yet... Wait for admin to Approve ')
            else:
                request.session['type'] = 'owner'
                return render(request, 'owner/index.html')
        elif obj.usertype == 'traffic':
            return render(request, 'traffic/index.html')
        elif obj.usertype == 'agency':
            return render(request, 'agency/index.html')
    except:
        return render(request, 'index.html')


def login(request):
    return render(request, 'login.html')


def login_post(request):
    username = request.POST['username']
    password = request.POST['password']
    obj = Login.objects.filter(email=username, password=password)
    if obj.exists():
        if obj[0].usertype == 'pending':
            return HttpResponse(
                "<script>alert('Give some time for Admin to verify your account, Thank you');window.location='/login'</script>")
        elif obj[0].usertype == 'rejected':
            return HttpResponse(
                "<script>alert('Account Got Rejected on some purpose, Thank you');window.location='/login'</script>")
        request.session['id'] = obj[0].id
        return redirect('/')
    else:
        return HttpResponse(
            "<script>alert('Email or password is not correct, Try again');window.location='/login'</script>")


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def logout(request):
    request.session['id'] = None
    request.session['type'] = None
    return redirect('/login')


#####################################Admin#########################################


def view_owners(request):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Owner.objects.all().order_by('-id')
    return render(request, 'Admins/view-owners.html', {'data': obj})


def owner_approval(request, status, id):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    if status == 'Approved':
        Login.objects.filter(id=Owner.objects.get(id=id).LOGIN.id).update(usertype='owner')
    elif status == 'Rejected':
        Owner.objects.filter(id=id).update(usertype='Rejected')

    return redirect('/view_owners')


def admin_view_agency(request):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = TravelAgency.objects.all().order_by('-id')
    return render(request, 'Admins/view_agency.html', {"data": obj})


def agency_approval(request, status, id):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    if status == 'Approved':
        Login.objects.filter(id=TravelAgency.objects.get(id=id).LOGIN.id).update(usertype='agency')
    elif status == 'Rejected':
        Owner.objects.filter(id=id).update(usertype='Rejected')
    return redirect('/admin_view_agency')


def admin_view_owners(request):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Owner.objects.filter(LOGIN__usertype='owner')
    return render(request, 'Admins/view-owners-list.html', {'data': obj})


def admin_view_bus(request, id):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    item = []
    obj = Bus.objects.filter(OWNER=id)
    for i in obj:
        avg = Rating.objects.filter(BUS=i.id).aggregate(Avg('rating'))
        item.append({
            'id': i.id,
            'name': i.name,
            'rc': i.rc,
            'regno': i.regno,
            'status': i.status,
            'complaints': [j.complaint for j in Complaints.objects.filter(BUS=i.id)],
            'avgrating': avg['rating__avg'] if avg['rating__avg'] is not None else 0
        })
    request.session['ownerid'] = id
    return render(request, 'Admins/view-bus-list.html', {'data': item})


def set_busroutes(request, id):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Route.objects.all()
    item = []
    routeList = Busroute.objects.filter(BUS=id)
    for i in routeList:
        item.append(i.ROUTE.id)
    return render(request, 'Admins/set-bus-routes.html',
                  {'data': obj, 'busname': Bus.objects.get(id=id).name, 'id': id, 'list': item})


def set_busroutes_post(request, id):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    routeList = request.POST.getlist('checkbox')
    Busroute.objects.filter(BUS=id).delete()
    for i in routeList:
        obj = Busroute()
        obj.ROUTE = Route.objects.get(id=i)
        obj.BUS = Bus.objects.get(id=id)
        obj.save()
    return redirect('/admin_view_bus/' + str(Bus.objects.get(id=id).OWNER.id) + '')


def add_routes(request):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Route.objects.all()
    return render(request, 'Admins/add-routes.html', {'data': obj})


def add_routes_post(request):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    bus_from = request.POST['from']
    bus_to = request.POST['to']
    route_type = request.POST['type']
    if Route.objects.filter(tripfrom=bus_from, tripto=bus_to):
        return HttpResponse(
            "<script>alert('This Route is added Already, Add diffrent !'); window.location='/add_routes'</script>")
    else:
        obj = Route()
        obj.tripfrom = bus_from
        obj.tripto = bus_to
        obj.type = route_type
        obj.save()

        obj1 = Route()
        obj1.tripfrom = bus_to
        obj1.tripto = bus_from
        obj1.type = route_type
        obj1.save()
    return redirect('/add_routes')


def delete_route(request, routeid):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    Route.objects.filter(id=routeid).delete()
    return redirect('/add_routes')


def add_stops(request, id):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Stop.objects.filter(ROUTE=id)
    return render(request, 'Admins/add-stops.html', {'data': obj, 'id': id})


def add_stops_post(request, id):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    name = request.POST['stop'].capitalize()
    if Stop.objects.filter(name=name, ROUTE=id).exists():
        return HttpResponse(
            "<script>alert('This Stop is Already there, Check Properly Before Adding Stops');window.location='/add_stops/" + id + "'</script>")
    obj = Stop()
    obj.name = name
    obj.ROUTE = Route.objects.get(id=id)
    obj.save()
    return redirect('/add_stops/' + id)


def block_bus(request, status, busid):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    Bus.objects.filter(id=busid).update(status=status)
    return redirect('/admin_view_bus/' + request.session['ownerid'] + '')


def admin_view_feedback(request):
    if request.session['type'] != 'admin' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Feedback.objects.all()
    return render(request, 'Admins/view-feedbacks.html', {'data': obj})


def admin_reply_post(request, complaintid):
    reply = request.POST['replytext']
    date = datetime.now().strftime("%d-%m-%Y")
    Complaints.objects.filter(id=complaintid).update(reply=reply, replydate=date)
    return redirect('/admin_view_owners')


def admin_add_traffic_police(request):
    return render(request, 'Admins/add_traffic_police.html')


def admin_add_traffic_police_post(request):
    name = request.POST['name']
    email = request.POST['email']
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']
    if Login.objects.filter(email__iexact=email):
        return HttpResponse(
            "<script>alert('This email id is already used, try another'); location='/admin_add_traffic_police'</script>")
    obj = Login()
    obj.email = email
    obj.password = str(int(random() * 10000000))
    obj.usertype = 'traffic'
    obj.save()
    obj1 = TrafficPolice()
    obj1.name = name
    obj1.email = email
    obj1.latitude = latitude
    obj1.longitude = longitude
    obj1.LOGIN = obj
    obj1.save()
    return HttpResponse("<script>alert('Successfully Added'); location='/admin_view_traffic_police'</script>")


def admin_view_traffic_police(request):
    obj = TrafficPolice.objects.all().order_by('-id')
    return render(request, 'Admins/view_traffic_police.html', {"data": obj})


def admin_delete_traffic_police(request, trafficid):
    Login.objects.filter(id=trafficid).delete()
    return HttpResponse("<script>alert('Successfully Deleted'); location='/admin_view_traffic_police'</script>")


#####################################Owner##########################################
def signup(request):
    return render(request, 'owner/signup.html')


def signup_post(request):
    email = request.POST['email']
    name = request.POST['name']
    phone = request.POST['phone']
    photo = request.FILES['photo']
    password = request.POST['password']
    if Login.objects.filter(email=email).exists():
        return HttpResponse(
            "<script>alert('Email or Phone number is already used, Try another Email');window.location='/signup'</script>")
    else:
        filename = str(datetime.now().strftime("%y%m%d%H%M%S")) + '.jpg'
        FileSystemStorage().save(r'D:\Abhinand\bustimelocation\bus\static\owner_photo\\' + filename, photo)
        path = "static/owner_photo/" + filename
        obj = Login()
        obj.email = email
        obj.password = password
        obj.usertype = 'pending'
        obj.save()
        obj1 = Owner()
        obj1.email = email
        obj1.name = name
        obj1.phone = phone
        obj1.photo = path
        obj1.LOGIN = obj
        obj1.save()
        return HttpResponse(
            "<script>alert('Registration Successfull, Login to Continue.'); window.location='/login'</script>")


def add_bus(request):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Route.objects.all()
    return render(request, 'owner/add-bus.html', {'data': obj})


def add_bus_post(request):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    name = request.POST['name']
    rc = request.POST['rc']
    regno = request.POST['regno']
    route = request.POST.getlist('route')
    if Bus.objects.filter(Q(regno=regno) | Q(rc=rc)):
        return HttpResponse(
            "<script>alert('RC or Regno is Already used Check once before adding');window.location='/add_bus'</script>")
    else:
        obj = Bus()
        obj.name = name
        obj.rc = rc
        obj.regno = regno
        obj.status = 'Unblocked'
        obj.OWNER = Owner.objects.get(LOGIN=request.session['id'])
        obj.save()
        for i in route:
            obj1 = Busroute()
            obj1.BUS = obj
            obj1.ROUTE = Route.objects.get(id=i)
            obj1.save()
        return HttpResponse("<script>alert('Successfully Added');window.location='/view_bus'</script>")


def view_bus(request):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Bus.objects.filter(OWNER__LOGIN=request.session['id'])

    return render(request, 'owner/view-bus.html', {'data': obj})


def edit_bus(request, id):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Bus.objects.get(id=id)
    routes = Route.objects.all()
    check = []
    for i in Busroute.objects.filter(BUS=obj):
        check.append(i.ROUTE.id)
    return render(request, 'owner/edit-bus.html', {'data': obj, 'list': routes, 'check': check})


def edit_bus_post(request, id):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    # Bus Time is not getting deleted Update is required
    name = request.POST['name']
    rc = request.POST['rc']
    regno = request.POST['regno']
    route = request.POST.getlist('route')
    Bus.objects.filter(id=id).update(name=name, rc=rc, regno=regno)
    Busroute.objects.filter(BUS=id).delete()
    for i in range(len(route)):
        obj = Busroute()
        obj.BUS = Bus.objects.get(id=id)
        obj.ROUTE = Route.objects.get(id=route[i])
        obj.save()
    return HttpResponse("<script>alert('Successfully Updated');window.location='/view_bus'</script>")


def delete_bus(request, id):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    # Bus.objects.get(id=id).delete()
    return redirect('/view_bus')


def view_driver(request):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Driver.objects.filter(OWNER=Owner.objects.get(LOGIN=request.session['id']))
    item = []
    for i in obj:
        item.append({
            'id': i.id,
            'name': i.name,
            'email': i.email,
            'phone': i.phone,
            'license': i.license,
            'status': Allocation.objects.filter(DRIVER=i.id).exists(),
            'busname': Allocation.objects.get(DRIVER=i.id).BUS.name if Allocation.objects.filter(
                DRIVER=i.id).exists() else ""

        })

    return render(request, 'owner/view-driver.html', {'data': item})


def delete_allocation(request, id):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    Allocation.objects.filter(DRIVER=id).delete()
    return redirect('/view_driver')


def add_driver(request):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    return render(request, 'owner/add-driver.html')


def add_driver_post(request):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    name = request.POST['name']
    email = request.POST['email']
    phone = request.POST['phone']
    licens = request.POST['license']
    if Login.objects.filter(email=email).exists() or Driver.objects.filter(Q(license=licens) | Q(phone=phone)).exists():
        return HttpResponse(
            "<script>alert('Your Email or License are used by Someone else, Try with other');window.location='add_driver'</script>")
    else:
        obj1 = Login()
        obj1.email = email
        # Password is going to send
        password = str(int(random() * 10000000))
        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)

            gmail.ehlo()

            gmail.starttls()

            gmail.login('riss.abhinand@gmail.com', 'fxac lquj yewo eenv')

        except Exception as e:
            print("Couldn't setup email!!" + str(e))

        msg = MIMEText("Your Password for TimeWheels will be " + password)

        msg['Subject'] = 'TimeWheel Driver Account Creation'

        msg['To'] = email

        msg['From'] = 'riss.abhinand@gmail.com'

        try:

            gmail.send_message(msg)

        except Exception as e:

            print("COULDN'T SEND EMAIL", str(e))

        obj1.password = password
        obj1.usertype = 'driver'
        obj1.save()
        obj = Driver()
        obj.name = name
        obj.email = email
        obj.phone = phone
        obj.license = licens
        obj.OWNER = Owner.objects.get(LOGIN=request.session['id'])
        obj.LOGIN = obj1
        obj.save()
        return HttpResponse("<script>alert('Successfully Added'); window.location='/view_driver'</script>")


def edit_driver(request, id):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Driver.objects.get(id=id)
    return render(request, 'owner/edit-driver.html', {'data': obj})


def edit_driver_post(request, id):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    name = request.POST['name']
    phone = request.POST['phone']
    licens = request.POST['license']
    Driver.objects.filter(id=id).update(name=name, phone=phone, license=licens)
    return redirect('/view_driver')


def delete_driver(request, id):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    Allocation.objects.filter(DRIVER=id).delete()
    Driver.objects.get(id=id).delete()
    return redirect('/view_driver')


def allocate(request, id):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj1 = Allocation.objects.filter(DRIVER=id)
    if obj1.exists():
        item = [i.BUS.id for i in Allocation.objects.all()]
        item.remove(Allocation.objects.get(DRIVER=id).BUS.id)
        obj = Bus.objects.filter(OWNER__LOGIN=request.session['id']).exclude(id__in=item)
        return render(request, 'owner/driver-allocation.html', {'data': obj, 'check': obj1, 'id': id})
    else:
        item = [i.BUS.id for i in Allocation.objects.all()]
        obj = Bus.objects.filter(OWNER__LOGIN=request.session['id']).exclude(id__in=item)
        return render(request, 'owner/driver-allocation.html', {'data': obj, 'id': id})


def allocate_post(request, id):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    bus_id = request.POST['busid']
    if Allocation.objects.filter(DRIVER=id).exists():
        Allocation.objects.filter(DRIVER=id).update(BUS=bus_id)
    else:
        obj = Allocation()
        obj.DRIVER = Driver.objects.get(id=id)
        obj.BUS = Bus.objects.get(id=bus_id)
        obj.save()
    return redirect('/view_driver')


def view_bus_routes(request):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Bus.objects.filter(OWNER__LOGIN=request.session['id'])
    print(obj)
    return render(request, 'owner/view-routes.html', {'data': obj})


def view_routes(request, id):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Busroute.objects.filter(BUS=id)
    return render(request, 'owner/view-route_list.html', {'data': obj})


def set_bus_timings(request, busid):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    obj = Busroute.objects.filter(BUS=busid)
    return render(request, 'owner/set-timings.html', {'data': obj, 'busid': busid})


def list_route_list(request, routeid, busid):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    data = Bustime.objects.filter(ROUTE=routeid, BUS=busid)
    item = []
    for i in data:
        item.append({
            'name': i.STOP.name,
            'time': i.time
        })
    if not data.exists():
        data = Stop.objects.filter(ROUTE=routeid)
        for i in data:
            item.append({
                'name': i.name,
                'time': ''
            })
    return render(request, "owner/ajax_stop.html", {"data": item})


def set_bus_timings_post(request, busid):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    route = request.POST['route']
    time_list = request.POST.getlist('stop')
    data = Stop.objects.filter(ROUTE=route)
    obj = Bustime.objects.filter(ROUTE=route, BUS=busid)
    if obj.exists():
        for i in range(len(time_list)):
            Bustime.objects.filter(ROUTE=route, BUS=busid, STOP=data[i]).update(time=time_list[i])
    else:
        for i in range(data.count()):
            obj = Bustime()
            obj.ROUTE = Route.objects.get(id=route)
            obj.BUS = Bus.objects.get(id=busid)
            obj.time = time_list[i]
            obj.STOP = data[i]
            obj.save()
    return redirect('/set_bus_timings/' + busid + '')


def track_bus(request, busid):
    if request.session['type'] != 'owner' and request.session['id'] is None:
        return HttpResponse("<script>alert('Session Expired, Login Again'); window.location='/login'</script>")
    track = Track.objects.filter(BUS=busid)
    if track.exists():
        latitude = track[0].latitude
        longitude = track[0].longitude
        return redirect('https://www.google.com/maps/?q=' + latitude + ',' + longitude)
    return HttpResponse(
        '<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><center style="color:red;">Wait for Driver '
        'to Start Live Location</center>')


# ---------------------------------------Traffic police---------------------------------------#


def traffic_view_complaints(request):
    obj = Complaints.objects.filter(TRAFFICPOLICE__LOGIN=request.session['id'])
    return render(request, 'traffic/view_complaints.html', {"data": obj})


def traffic_reply(request, complaintid):
    return render(request, 'traffic/complaint_reply.html', {"complaintid": complaintid})


def traffic_reply_post(request, complaintid):
    reply = request.POST['replytext']
    date = datetime.now().strftime("%d-%m-%Y")
    Complaints.objects.filter(id=complaintid).update(reply=reply, replydate=date)
    return HttpResponse("<script>alert('Added'); location='traffic_view_complaints'</script>")


def traffic_view_blocks(request):
    obj = Blocks.objects.filter(TRAFFICPOLICE__LOGIN=request.session['id']).order_by('-id')
    return render(request, 'traffic/view_blocks.html', {"data": obj})


def traffic_add_blocks_post(request):
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']
    obj = Blocks()
    obj.latitude = latitude
    obj.longitude = longitude
    obj.TRAFFICPOLICE = TrafficPolice.objects.get(LOGIN=request.session['id'])
    obj.save()
    return redirect('/traffic_view_blocks')


def traffic_delete_block(request, blockid):
    Blocks.objects.filter(id=blockid).delete()
    return HttpResponse("<script>alert('Deleted Successfully'); location='/traffic_view_blocks'</script>")



# -----------------------------------Travel Agency--------------------------------------


def agency_registration(request):
    return render(request, 'agency/registration.html')


def agency_registration_post(request):
    email = request.POST['email']
    name = request.POST['name']
    phone = request.POST['phone']
    password = request.POST['password']
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']

    if Login.objects.filter(email__iexact=email):
        return HttpResponse("<script>alert('Email is already used'); location='agency_registration'</script>")
    obj = Login()
    obj.email = email
    obj.password = password
    obj.usertype = 'pending'
    obj.save()

    obj1 = TravelAgency()
    obj1.email = email
    obj1.name = name
    obj1.phone = phone
    obj1.latitude = latitude
    obj1.longitude = longitude
    obj1.LOGIN = obj
    obj1.save()
    return HttpResponse("<script>alert('Successfully Added'); location = '/login'</script>")


def agency_view_bus(request):
    obj = TravelBus.objects.filter(TRAVELAGENCY__LOGIN=request.session['id'])
    return render(request, 'agency/view_bus.html', {"data": obj})


def agency_add_bus_post(request):
    name = request.POST['name']
    rc = request.POST['rc']
    regno = request.POST['regno']
    seats = request.POST['seats']

    if TravelBus.objects.filter(Q(rc=rc) | Q(regno=regno)).exists():
        return HttpResponse(
            "<script>alert('This Credentials are already Exists, Try another'); location = '/agency_view_bus'</script>")
    obj = TravelBus()
    obj.name = name
    obj.rc = rc
    obj.regno = regno
    obj.seats = seats
    obj.TRAVELAGENCY = TravelAgency.objects.get(LOGIN=request.session['id'])
    obj.save()
    return HttpResponse("<script>alert('Added Successfully'); location = '/agency_view_bus'</script>")


def agency_delete_bus(request, busid):
    TravelBus.objects.filter(id=busid).delete()
    return HttpResponse("<script>alert('Deleted Successfully'); location = '/agency_view_bus'</script>")


def agency_edit_bus(request, busid):
    obj = TravelBus.objects.get(id=busid)
    return render(request, 'agency/edit_bus.html', {"data": obj})


def agency_edit_bus_post(request, busid):
    name = request.POST['name']
    TravelAgency.objects.filter(id=busid).update(name=name)
    return HttpResponse("<script>alert('Edited Successfully'); location = '/agency_view_bus'</script>")


def allocate_routes(request):
    busobj = TravelBus.objects.filter(TRAVELAGENCY__LOGIN=request.session['id'])
    routeobj = Route.objects.filter(type='Long')

    obj = TravelAllocate.objects.filter(TRAVELBUS__TRAVELAGENCY__LOGIN=request.session['id'])
    # arr = [] for i in obj: arr.append({"busname": i.TRAVELBUS.name, "routename": [j.ROUTE.tripfrom + " to " +
    # j.ROUTE.tripto for j in TravelAllocate.objects.filter(TRAVELBUS__id=i.id)]}) print((set(arr))
    return render(request, 'agency/routes.html', {"data": obj, "buses": busobj, "routes": routeobj})


def allocate_routes_post(request):
    busid = request.POST['busid']
    routeid = request.POST['routeid']
    amount = request.POST['amount']
    obj = TravelAllocate()
    obj.amount = amount
    obj.ROUTE_id = routeid
    obj.TRAVELBUS_id = busid
    obj.save()
    return HttpResponse("<script>alert('Successfully Added'); location='/allocate_routes'</script>")


def agency_delete_allocation(request, allocationid):
    TravelAllocate.objects.filter(id=allocationid).delete()
    return HttpResponse("<script>alert('Successfully Deleted'); location='/allocate_routes'</script")


def agency_schedule(request, allocateid):
    obj = TravelAllocate.objects.get(id=allocateid)
    data = ScheduleBus.objects.filter(TRAVELALLOCATE=allocateid)
    return render(request, 'agency/schedule.html', {"obj": obj, "data": data})


def agency_schedule_post(request, allocateid):
    start = request.POST['start']
    end = request.POST['end']
    date = request.POST['date']
    d = datetime.strptime(date, "%Y-%m-%d")
    obj = ScheduleBus()
    obj.date = d.strftime("%d-%m-%Y")
    obj.timefrom = start
    obj.timeto = end
    obj.TRAVELALLOCATE_id = allocateid
    obj.save()
    total_seat = int(TravelAllocate.objects.get(id=allocateid).TRAVELBUS.seats)
    for i in range(1, total_seat+1):
        obj1 = ScheduleBusSub()
        obj1.seat = i
        obj1.status = 'pending'
        obj1.SCHEDULEBUS = obj
        obj1.save()

    return redirect('/agency_schedule/'+allocateid+'#data')


def agency_delete_schedule(request, allocateid, scheduleid):
    ScheduleBus.objects.filter(id=scheduleid).delete()
    return redirect('/agency_schedule/'+allocateid+'#data')


def agency_view_bookings(request):
    obj = Bookings.objects.all().order_by('-id')
    return render(request, 'agency/view_bookings.html', {"data": obj})


def agency_view_rating(request):
    obj = TravelRating.objects.filter(TRAVELBUS__TRAVELAGENCY__LOGIN=request.session['id'])
    return render(request, 'agency/view_rating.html', {"data": obj})


# ########################################Android#############################################


def check(request):
    return JsonResponse({"status": "ok"})


def andlogin(request):
    username = request.POST['username']
    password = request.POST['password']
    obj = Login.objects.filter(email=username, password=password)
    if obj.exists():
        if obj[0].usertype == 'driver':
            qry = Driver.objects.get(LOGIN=obj[0].id)
            nm = qry.name
            em = qry.email
            typ = 'driver'
            blockstatus = "No" if Allocation.objects.filter(
                DRIVER__LOGIN=obj[0].id).exists() and Allocation.objects.get(
                DRIVER__LOGIN=obj[0].id).BUS.status == 'Unblocked' else "Yes"
            busid = Allocation.objects.get(DRIVER=qry.id).BUS.id if Allocation.objects.filter(
                DRIVER=qry.id).exists() else ""
            return JsonResponse(
                {"status": "ok", "lid": obj[0].id, "name": nm, "email": em, "type": typ, "busstatus": blockstatus,
                 "busid": busid})

        if obj[0].usertype == 'user':
            print("yes")
            qry = User.objects.get(LOGIN=obj[0].id)
            nm = qry.name
            em = qry.email
            typ = 'user'
            print({"status": "ok", "lid": obj[0].id, "name": nm, "email": em, "type": typ, "profilepic": qry.photo})
            return JsonResponse(
                {"status": "ok", "lid": obj[0].id, "name": nm, "email": em, "type": typ, "profilepic": qry.photo})
    else:
        return JsonResponse({"status": "no"})


# ########################################Driver#############################################


def allocated_bus(request):
    lid = request.POST['id']
    timedelay = "0"
    qry = Allocation.objects.filter(DRIVER__LOGIN=lid)
    if qry.exists():
        qry = qry[0]
        delqry = Delay.objects.filter(BUS=qry.BUS.id)
        if delqry.exists():
            timedelay = delqry[0].time
        busname = qry.BUS.name
        ownername = qry.DRIVER.OWNER.name
        blockstatus = blockstatus = "No" if qry.BUS.status == 'Unblocked' else "Yes"
        return JsonResponse(
            {"status": "ok", "busname": busname, "ownername": ownername, "delay": timedelay, "busstatus": blockstatus})

    else:
        return JsonResponse({"status": "no"})


def add_delay(request):
    lid = request.POST['id']
    delay = request.POST['delay']
    settime = datetime.now().strftime("%H:%M")
    qry = Allocation.objects.get(DRIVER__LOGIN=lid)
    if Delay.objects.filter(BUS=qry.BUS.id).exists():
        Delay.objects.filter(BUS=qry.BUS.id).update(time=delay, setontime=settime)
    else:
        obj = Delay()
        obj.BUS = qry.BUS
        obj.time = delay
        obj.setontime = settime
        obj.save()
    return JsonResponse({"status": "ok"})


def driver_location_updation(request):
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']
    busid = request.POST['busid']

    qry = Track.objects.filter(BUS=busid)
    if qry.exists():
        # if obj.objects.filter(BUS=busid).exists():
        Track.objects.filter(BUS=busid).update(latitude=latitude, longitude=longitude)
    else:
        obj = Track()
        obj.latitude = latitude
        obj.longitude = longitude
        obj.BUS_id = busid
        obj.save()
    return JsonResponse({"status": "ok"})


# ------------------------------------Passenger--------------------------------------


def user_registration(request):
    name = request.POST['name']
    email = request.POST['email']
    if Login.objects.filter(email=email).exists():
        return JsonResponse({"status": "no", "dup": "email"})
    phone = request.POST['phone']
    password = request.POST['password']
    image = request.FILES['pic']
    filename = datetime.now().strftime("%y%m%d%H%M%S")
    fs = FileSystemStorage()
    fs.save(r"D:\Abhinand\bustimelocation\bus\static\userphoto\\" + filename + ".jpg", image)
    path = "/static/userphoto/" + filename + ".jpg"

    obj = Login()
    obj.email = email
    obj.password = password
    obj.usertype = 'user'

    obj1 = User()
    obj1.email = email
    obj1.name = name
    obj1.phone = phone
    obj1.photo = path
    obj1.LOGIN = obj
    obj.save()
    obj1.save()
    return JsonResponse({"status": "ok"})


def buslist(request):
    qry1 = request.POST['from'].strip()
    qry2 = request.POST['to'].strip()
    data = []
    runningstatus = "False"
    currenttime = float(datetime.now().strftime("%H.%M"))
    search = Route.objects.filter(tripfrom__icontains=qry1, tripto__icontains=qry2, type='local')
    if search.exists():
        routeId = search[0].id
        routename = search[0].tripfrom + " to " + search[0].tripto
        busobj = Busroute.objects.filter(ROUTE=routeId, BUS__status="Unblocked")
        if busobj.exists():
            for i in busobj:
                timelist = []
                for j in Bustime.objects.filter(BUS=i.BUS.id, ROUTE=routeId):
                    timelist.append(float(j.time.replace(":", ".")))
                if timelist[0] <= currenttime <= timelist[-1]:
                    runningstatus = "True"
                data.append({
                    "id": i.BUS.id,
                    "name": i.BUS.name,
                    "delay": Delay.objects.get(BUS=i.BUS.id).time if Delay.objects.filter(
                        BUS=i.BUS.id).exists() else "0",
                    "running": runningstatus})
        return JsonResponse({"status": "ok", "data": data, "routeid": routeId, "routename": routename})
    return JsonResponse({"status": "no", "data": [], "routeid": 0})


def bustimings(request):
    data = []
    routeid = request.POST['routeid']
    busid = request.POST['busid']
    currentrating = Rating.objects.filter(BUS=busid).aggregate(Avg('rating'))
    busname = Bus.objects.get(id=busid).name
    obj = Bustime.objects.filter(ROUTE=routeid, BUS=busid)
    delayqry = Delay.objects.filter(BUS=busid)
    delay = float(delayqry[0].time.replace(":", ".")) if delayqry.exists() else 0
    committime = float(delayqry[0].setontime.replace(":", ".")) if delayqry.exists() else 0

    delaytime = ""
    for i in obj:
        if float(i.time.replace(":", ".")) <= committime:
            delaytime = i.time
        else:
            delaytime = (datetime.strptime(i.time, "%H:%M") + timedelta(minutes=delay)).strftime("%H:%M")
        data.append({"stop": i.STOP.name,
                     "time": i.time,
                     "delaytime": delaytime})
    return JsonResponse(
        {"status": "ok", "data": data, "busname": busname, "currentrating": currentrating['rating__avg']})


def user_add_rating(request):
    date = datetime.now().strftime("%d-%m-%Y")
    userid = request.POST['userid']
    busid = request.POST['busid']
    rating = request.POST['rating']
    rateqry = Rating.objects.filter(USER__LOGIN=userid, BUS=busid)
    if rateqry.exists():
        rateqry.update(rating=rating, date=date)
    else:
        obj = Rating()
        obj.rating = rating
        obj.BUS = Bus.objects.get(id=busid)
        obj.date = date
        obj.USER = User.objects.get(LOGIN=userid)
        obj.save()
    return JsonResponse({"status": "ok"})


def user_add_feedback(request):
    userid = request.POST['userid']
    feedback = request.POST['feedback']
    obj = Feedback()
    obj.feedback = feedback
    obj.time = datetime.now().strftime("%H:%M:%S")
    obj.date = datetime.now().strftime("%d-%m-%Y")
    obj.USER = User.objects.get(LOGIN=userid)
    obj.save()
    return JsonResponse({"status": "ok"})


def user_add_complaint(request):
    userid = request.POST['userid']
    busid = request.POST['busid']
    complaint = request.POST['complaint']
    obj = Complaints()
    obj.USER = User.objects.get(LOGIN=userid)
    obj.BUS = Bus.objects.get(id=busid)
    obj.complaint = complaint
    obj.complaindate = datetime.now().strftime("%d-%m-%Y")
    obj.reply = "Pending"
    obj.replydate = "Pending"
    obj.save()
    return JsonResponse({"status": "ok"})


def user_view_complaints(request):
    data = []
    userid = request.POST['id']
    obj = Complaints.objects.filter(USER__LOGIN=userid)
    if obj.exists():
        for i in obj:
            data.append({
                "busname": i.BUS.name,
                "complaint": i.complaint,
                "complaintdate": i.complaindate,
                "reply": i.reply,
                "replydate": i.replydate
            })
        return JsonResponse({"status": "ok", "data": data})
    return JsonResponse({"status": "no"})


def user_bus_track(request):
    busid = request.POST['busid']
    obj = Track.objects.filter(BUS=busid)
    if obj.exists():
        obj = obj[0]
        latitude = obj.latitude
        longitude = obj.longitude
        return JsonResponse({"status": "ok", "latitude": latitude, "longitude": longitude})
    else:
        return JsonResponse({"status": "no"})


def long_buslist(request):
    qry1 = request.POST['from'].strip()
    qry2 = request.POST['to'].strip()
    qry3 = request.POST['date'].strip()
    search = ScheduleBus.objects.filter(TRAVELALLOCATE__ROUTE__tripfrom__icontains=qry1, TRAVELALLOCATE__ROUTE__tripto__icontains=qry2, TRAVELALLOCATE__ROUTE__type='long', date=qry3)
    arr = []
    if search.exists():
        routename = search[0].TRAVELALLOCATE.ROUTE.tripfrom+" to "+search[0].TRAVELALLOCATE.ROUTE.tripto
        for i in search:
            arr.append({"id": i.id,
                         "start": i.timefrom,
                         "end": i.timeto,
                         "amount": i.TRAVELALLOCATE.amount,
                         "name": i.TRAVELALLOCATE.TRAVELBUS.name})
        print(arr)
        return JsonResponse({"status": "ok", "data": arr, "routename": routename})
    else:
        return JsonResponse({"status": "no", "data": arr})


def get_seats(request):
    scheduleid = request.POST['scheduleid']
    obj = ScheduleBusSub.objects.filter(SCHEDULEBUS=scheduleid)
    amount = obj[0].SCHEDULEBUS.TRAVELALLOCATE.amount
    arr = []
    for i in obj:
        arr.append({"sid": i.id,
                    "seat": i.seat,
                    "status": i.status})
    return JsonResponse({"status": "ok", "data": arr, "amount": amount, "reqid": scheduleid})


def payment(request):
    reqid = request.POST['reqid']
    loginid = request.POST['loginid']
    bankname = request.POST['bname']
    accno = request.POST['accn']
    ifsc = request.POST['ifsc']
    total = request.POST['total']
    if Bank.objects.filter(name__iexact=bankname, accno=accno, ifsc=ifsc, balance__gte=total).exists():
        seatnumbers = request.POST['seatnumbers'][:-2]
        arr = seatnumbers.split(", ")
        arrr = [int(i) for i in arr]
        print(arrr)

        for i in arr:
            print(i)
            s = str(int(i)+1)
            ScheduleBusSub.objects.filter(SCHEDULEBUS=reqid, seat=s).update(status="approved")
        obj = Bookings()
        obj.USER = User.objects.get(LOGIN=loginid)
        obj.SCHEDULEBUS_id = reqid
        obj.seatlist = seatnumbers
        obj.save()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "no"})


def view_bookings(request):
    loginid = request.POST['loginid']
    obj = Bookings.objects.filter(USER__LOGIN=loginid).order_by('-id')
    arr = []
    for i in obj:
        arr.append({"busname": i.SCHEDULEBUS.TRAVELALLOCATE.TRAVELBUS.name,
                    "date": i.SCHEDULEBUS.date,
                    "stime": i.SCHEDULEBUS.timefrom,
                    "etime": i.SCHEDULEBUS.timeto,
                    "seatlist": i.seatlist,
                    "from": i.SCHEDULEBUS.TRAVELALLOCATE.ROUTE.tripfrom,
                    "to": i.SCHEDULEBUS.TRAVELALLOCATE.ROUTE.tripto})
    print(arr)
    return JsonResponse({"status": "ok", "data": arr})
