# coding=utf-8
import dataclasses
import abc
import datetime
import decimal
import typing

import yaml

import jinja2

import pathlib


from jinja2 import Template
from jinja2.runtime import Context, resolve_or_missing
from jinja2.utils import missing

from . import api, parser

TEMPLATES = str(pathlib.Path(__file__).parent / 'templates')


class RaisingContext(Context):

  def resolve(self, key):
    if self._legacy_resolve_mode:
      rv = resolve_or_missing(self, key)
    else:
      rv = self.resolve_or_missing(key)
    if rv is missing:
      raise KeyError(key)
    if rv is None:
      raise ValueError(key)
    return rv


ENV = jinja2.Environment(
  loader=jinja2.FileSystemLoader(TEMPLATES),
)

ENV.context_class = RaisingContext


def render(context: api.JPKFAContext):
  template = ENV.get_template('template.xml')
  return template.render(**{
    field.name: getattr(context, field.name)
    for field in dataclasses.fields(context)
  })


def render_from_source_file(seller: pathlib.Path, invoices: pathlib.Path):
  seller_data = yaml.load(seller.open('r'))
  invoice_data = yaml.load(invoices.open('r'))
  seller_data.update(invoice_data)
  context = parser.DataclassParser.parse(seller_data, api.JPKFAContext)
  xml_text = render(context)
  # from xml import etree
  # xml_text = etree.tostring(etree.fromstring(xml_text.encode('utf-8')), pretty_print=True)
  return xml_text



