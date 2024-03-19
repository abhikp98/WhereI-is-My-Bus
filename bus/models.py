from django.db import models


# Create your models here.
class Login(models.Model):
    email = models.CharField(max_length=30)
    password = models.CharField(max_length=15)
    usertype = models.CharField(max_length=20)


class Owner(models.Model):
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=40)
    photo = models.CharField(max_length=100)
    LOGIN = models.ForeignKey(Login, on_delete=models.CASCADE)


class User(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=40)
    phone = models.CharField(max_length=15)
    photo = models.CharField(max_length=100)
    LOGIN = models.ForeignKey(Login, on_delete=models.CASCADE)


class Driver(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=40)
    phone = models.CharField(max_length=15)
    license = models.CharField(max_length=30)
    OWNER = models.ForeignKey(Owner, on_delete=models.CASCADE)
    LOGIN = models.ForeignKey(Login, on_delete=models.CASCADE)


class Route(models.Model):
    tripfrom = models.CharField(max_length=30)
    tripto = models.CharField(max_length=30)
    type = models.CharField(max_length=10)


class Bus(models.Model):
    name = models.CharField(max_length=30)
    rc = models.CharField(max_length=100)
    regno = models.CharField(max_length=20)
    status = models.CharField(max_length=10)
    OWNER = models.ForeignKey(Owner, on_delete=models.CASCADE)


class Stop(models.Model):
    name = models.CharField(max_length=30)
    ROUTE = models.ForeignKey(Route, on_delete=models.CASCADE)


class Feedback(models.Model):
    feedback = models.CharField(max_length=300)
    date = models.CharField(max_length=15)
    time = models.CharField(max_length=10)
    USER = models.ForeignKey(User, on_delete=models.CASCADE)


class Bustime(models.Model):
    time = models.CharField(max_length=10)
    STOP = models.ForeignKey(Stop, on_delete=models.CASCADE)
    BUS = models.ForeignKey(Bus, on_delete=models.CASCADE)
    ROUTE = models.ForeignKey(Route, on_delete=models.CASCADE)


class Track(models.Model):
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    BUS = models.ForeignKey(Bus, on_delete=models.CASCADE)


class Delay(models.Model):
    time = models.CharField(max_length=10, default=0)
    setontime = models.CharField(max_length=10)
    BUS = models.ForeignKey(Bus, on_delete=models.CASCADE)


class TrafficPolice(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=40)
    latitude = models.CharField(max_length=200)
    longitude = models.CharField(max_length=200)
    LOGIN = models.ForeignKey(Login, on_delete=models.CASCADE)


class Complaints(models.Model):
    complaint = models.CharField(max_length=300)
    complaindate = models.CharField(max_length=15)
    reply = models.CharField(max_length=300)
    replydate = models.CharField(max_length=15)
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    BUS = models.ForeignKey(Bus, on_delete=models.CASCADE)
    TRAFFICPOLICE = models.ForeignKey(TrafficPolice, on_delete=models.CASCADE)


class Blocks(models.Model):
    latitude = models.CharField(max_length=200)
    longitude = models.CharField(max_length=200)
    TRAFFICPOLICE = models.ForeignKey(TrafficPolice, on_delete=models.CASCADE)


class Rating(models.Model):
    date = models.CharField(max_length=15)
    rating = models.FloatField(max_length=5)
    USER = models.ForeignKey(User, on_delete=models.CASCADE)
    BUS = models.ForeignKey(Bus, on_delete=models.CASCADE)


class Allocation(models.Model):
    DRIVER = models.ForeignKey(Driver, on_delete=models.CASCADE)
    BUS = models.ForeignKey(Bus, on_delete=models.CASCADE)


class Busroute(models.Model):
    BUS = models.ForeignKey(Bus, on_delete=models.CASCADE)
    ROUTE = models.ForeignKey(Route, on_delete=models.CASCADE)


class TravelAgency(models.Model):
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=40)
    latitude = models.CharField(max_length=200)
    longitude = models.CharField(max_length=200)
    LOGIN = models.ForeignKey(Login, on_delete=models.CASCADE)


class TravelBus(models.Model):
    name = models.CharField(max_length=30)
    rc = models.CharField(max_length=30)
    seats = models.IntegerField()
    regno = models.CharField(max_length=20)
    TRAVELAGENCY = models.ForeignKey(TravelAgency, on_delete=models.CASCADE)


class TravelAllocate(models.Model):
    amount = models.FloatField()
    TRAVELBUS = models.ForeignKey(TravelBus, on_delete=models.CASCADE)
    ROUTE = models.ForeignKey(Route, on_delete=models.CASCADE)


class TravelRating(models.Model):
    rating = models.FloatField()
    TRAVELBUS = models.ForeignKey(TravelBus, on_delete=models.CASCADE)
    USER = models.ForeignKey(User, on_delete=models.CASCADE)


class ScheduleBus(models.Model):
    date = models.CharField(max_length=20)
    timefrom = models.CharField(max_length=10)
    timeto = models.CharField(max_length=10)
    TRAVELALLOCATE = models.ForeignKey(TravelAllocate, on_delete=models.CASCADE)


class ScheduleBusSub(models.Model):
    seat = models.CharField(max_length=10)
    status = models.CharField(max_length=10)
    SCHEDULEBUS = models.ForeignKey(ScheduleBus, on_delete=models.CASCADE)


class Bookings(models.Model):
    seatlist = models.CharField(max_length=200)
    SCHEDULEBUS = models.ForeignKey(ScheduleBus, on_delete=models.CASCADE)
    USER = models.ForeignKey(User, on_delete=models.CASCADE)


class Bank(models.Model):
    name = models.CharField(max_length=30)
    accno = models.CharField(max_length=30)
    ifsc = models.CharField(max_length=20)
    balance = models.FloatField()

