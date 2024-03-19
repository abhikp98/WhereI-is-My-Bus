"""bustimelocation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from bus import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login),
    path('login_post', views.login_post),
    path('logout', views.logout),
    path('signup', views.signup),
    path('signup_post', views.signup_post),
    path('view_owners', views.view_owners, name='viewOwners'),
    path('owner_approval/<status>/<id>', views.owner_approval),
    path('admin_view_agency', views.admin_view_agency, name='viewAgency'),
    path('agency_approval/<status>/<id>', views.agency_approval),
    path('view_bus', views.view_bus, name='view_bus'),
    path('add_bus', views.add_bus, name='add_bus'),
    path('add_bus_post', views.add_bus_post),
    path('edit_bus/<id>', views.edit_bus),
    path('edit_bus_post/<id>', views.edit_bus_post),
    path('delete_bus/<id>', views.delete_bus),
    path('view_driver', views.view_driver, name='view_driver'),
    path('delete_allocation/<id>', views.delete_allocation),
    path('add_driver', views.add_driver, name='add_driver'),
    path('add_driver_post', views.add_driver_post),
    path('edit_driver/<id>', views.edit_driver),
    path('edit_driver_post/<id>', views.edit_driver_post),
    path('delete_driver/<id>', views.delete_driver),
    path('allocate/<id>', views.allocate),
    path('allocate_post/<id>', views.allocate_post),
    path('view_bus_routes', views.view_bus_routes, name='view_bus_routes'),
    path('view_routes/<id>', views.view_routes),
    path('admin_view_owners', views.admin_view_owners, name='view0wnerBus'),
    path('admin_view_bus/<id>', views.admin_view_bus),
    path('admin_reply_post/<complaintid>', views.admin_reply_post),
    path('admin_add_traffic_police', views.admin_add_traffic_police, name='add_traffic'),
    path('admin_view_traffic_police', views.admin_view_traffic_police),
    path('admin_add_traffic_police_post', views.admin_add_traffic_police_post),
    path('admin_delete_traffic_police/<trafficid>', views.admin_delete_traffic_police),
    path('set_busroutes/<id>', views.set_busroutes),
    path('set_busroutes_post/<id>', views.set_busroutes_post),
    path('add_routes', views.add_routes, name='addRoutes'),
    path('add_routes_post', views.add_routes_post),
    path('add_stops/<id>', views.add_stops),
    path('add_stops_post/<id>', views.add_stops_post),
    path('delete_route/<routeid>', views.delete_route),
    path('block_bus/<status>/<busid>', views.block_bus),
    path('admin_view_feedback', views.admin_view_feedback, name='adminViewFeedback'),
    path('set_bus_timings/<busid>', views.set_bus_timings),
    path('track_bus/<busid>', views.track_bus),
    path('list_route_list/<routeid>/<busid>', views.list_route_list),
    path('set_bus_timings_post/<busid>', views.set_bus_timings_post),
    path('about', views.about),
    path('contact', views.contact),

    path('traffic_view_complaints', views.traffic_view_complaints, name='traffic_view_complaint'),
    path('traffic_reply/<complaintid>', views.traffic_reply),
    path('traffic_reply_post', views.traffic_reply_post),
    path('traffic_add_blocks_post', views.traffic_add_blocks_post),
    path('traffic_view_blocks', views.traffic_view_blocks, name='view_block'),
    path('traffic_add_blocks_post', views.traffic_add_blocks_post),
    path('traffic_delete_block/<blockid>', views.traffic_delete_block),


    path('agency_registration', views.agency_registration),
    path('agency_registration_post', views.agency_registration_post),
    path('agency_view_bus', views.agency_view_bus, name='agency_buses'),
    path('agency_add_bus_post', views.agency_add_bus_post),
    path('agency_delete_bus/<busid>', views.agency_delete_bus),
    path('agency_edit_bus/<busid>', views.agency_edit_bus),
    path('agency_edit_bus_post/<busid>', views.agency_edit_bus_post),
    path('allocate_routes', views.allocate_routes, name='allocation'),
    path('allocate_routes_post', views.allocate_routes_post),
    path('agency_delete_allocation/<allocationid>', views.agency_delete_allocation),
    path('agency_view_bookings', views.agency_view_bookings, name='bookings'),
    path('agency_schedule/<allocateid>', views.agency_schedule),
    path('agency_schedule_post/<allocateid>', views.agency_schedule_post),
    path('agency_delete_schedule/<allocateid>/<scheduleid>', views.agency_delete_schedule),
    path('agency_view_rating', views.agency_view_rating, name='rating'),


    path('check', views.check),
    path('andlogin', views.andlogin),

    path('allocated_bus', views.allocated_bus),
    path('add_delay', views.add_delay),
    path('driver_location_updation', views.driver_location_updation),

    path('user_registration', views.user_registration),
    path('buslist', views.buslist),
    path('bustimings', views.bustimings),
    path('user_add_rating', views.user_add_rating),
    path('user_add_feedback', views.user_add_feedback),
    path('user_add_complaint', views.user_add_complaint),
    path('user_view_complaints', views.user_view_complaints),
    path('user_bus_track', views.user_bus_track),
    path('long_buslist', views.long_buslist),
    path('get_seats', views.get_seats),
    path('payment', views.payment),
    path('view_bookings', views.view_bookings),
]
