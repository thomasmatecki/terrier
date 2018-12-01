"""RestQueries URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, re_path
# from rest_framework import routers
from django.conf.urls import url, include
from rest_framework.schemas import get_schema_view

from flights.renderers import ODataMetadataRenderer
from flights.views import api, FlightPlanViewSet, AirlineViewSet
from flights.routers import ODataRouter, ODataMetadataGenerator

# Routers provide an easy way of automatically determining the URL conf.
router = ODataRouter()
router.register(r'flights', FlightPlanViewSet)
router.register(r'airlines', AirlineViewSet)

schema_view = get_schema_view(
  title="Example API",
  generator_class=ODataMetadataGenerator,
  renderer_classes=[ODataMetadataRenderer]
)

urlpatterns = [
  url('^schema$', schema_view),
  url(r'^', include(router.urls)),
  path('admin/', admin.site.urls),
  re_path(r'^api/(?P<entity>\w+)', api)
]
