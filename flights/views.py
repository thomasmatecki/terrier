from django.shortcuts import render
from django.http import JsonResponse
from parser.grammar import boolCommonExpr
from flights import models
from django.forms.models import model_to_dict


def api(request, entity):
  query_dict = getattr(request, request.method)

  filter_clause = query_dict.get('$filter')

  entity_model = getattr(models, entity)

  if filter_clause:
    filter_ast = boolCommonExpr <= filter_clause

  return JsonResponse(
    list(map(model_to_dict, entity_model.objects.all())), safe=False
  )