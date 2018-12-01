from rest_framework import renderers
from lxml import etree

class ODataRenderer(renderers.JSONRenderer):
  def render(self, data, accepted_media_type=None, renderer_context=None):
    response = super(ODataRenderer, self).render(
      {'value': data},
      accepted_media_type=None,
      renderer_context=None)
    return response


class ODataMetadataRenderer(renderers.BaseRenderer):
  def render(self, data, accepted_media_type=None, renderer_context=None):
    metadata_root = etree.Element(
      '{http://docs.oasis-open.org/odata/ns/edmx}Edmx',
      nsmap={'edmx': 'http://docs.oasis-open.org/odata/ns/edmx'}
    )

    return etree.tostring(metadata_root)