from django.http import JsonResponse
from rest_framework import viewsets

from flights.models import FlightPlan, Airline
from flights.serializers import FlightPlanSerializer, AirlineSerializer
from parser.grammar import boolCommonExpr
from flights import models
from django.forms.models import model_to_dict


def api(request, entity):
  query_dict = getattr(request, request.method)

  filter_clause = query_dict.get('$filter')

  entity_model = getattr(models, entity)

  if filter_clause:
    filter_ast = boolCommonExpr <= filter_clause
    result_set = entity_model.objects.filter(filter_ast.Q)
  else:
    result_set = entity_model.objects.all()

  return JsonResponse(
    {'@odata.context': '',
     'value': list(map(model_to_dict,
                       result_set))}, safe=False
  )


class FlightPlanViewSet(viewsets.ModelViewSet):
  queryset = FlightPlan.objects.all()
  serializer_class = FlightPlanSerializer


class AirlineViewSet(viewsets.ModelViewSet):
  queryset = Airline.objects.all()
  serializer_class = AirlineSerializer
