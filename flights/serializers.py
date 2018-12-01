from rest_framework import serializers

from flights.models import FlightPlan, Airline


class FlightPlanSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = FlightPlan
    fields = '__all__'


class AirlineSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = Airline
    fields = '__all__'
