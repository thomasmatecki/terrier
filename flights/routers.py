from rest_framework.routers import DefaultRouter
from rest_framework.schemas import SchemaGenerator
from lxml import etree


class ODataMetadataGenerator(SchemaGenerator):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def get_schema(self, request=None, public=False):
    return {}


class ODataRouter(DefaultRouter):
  SchemaGenerator = ODataMetadataGenerator
