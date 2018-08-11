from django.db import models


# from django.contrib.gis.db.models import PointField


class Airline(models.Model):
  code = models.CharField(max_length=2, primary_key=True)
  name = models.CharField(max_length=30)


class Airport(models.Model):
  code = models.CharField(max_length=3, primary_key=True)
  name = models.CharField(max_length=50)
  # location = PointField()


class FlightPlan(models.Model):
  airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
  number = models.IntegerField()
  departure_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='departures')
  arrival_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='arrivals')
  duration = models.DurationField(blank=True)

  class Meta:
    unique_together = (('number', 'airline'),)
    get_latest_by = ["airline", 'number']


class Flight(models.Model):
  flight_plan = models.ForeignKey(FlightPlan, on_delete=models.PROTECT)
  departure_time = models.DateTimeField()
