# coding=utf-8
import datetime
import decimal
import typing
import dataclasses
from collections.abc import Sequence
from types import MappingProxyType


@dataclasses.dataclass()
class FieldDescription(object):

  type: typing.Type
  is_optional: bool = False
  is_sequence: bool = False
  default: typing.Any = None
  name: str = None


@dataclasses.dataclass()
class FieldDefault(object):

  has_default: bool = False
  default_value: typing.Any = None


def date_transformer(value):
  if isinstance(value, datetime.date):
    return value
  return datetime.date.fromisoformat(value)


def datetime_transformer(value):
  if isinstance(value, datetime.date):
    return value
  if isinstance(value, datetime.datetime):
    return value
  return datetime.datetime.fromisoformat(value)

def default_type_map():
  return MappingProxyType({
    int: int,
    float: float,
    str: str,
    decimal.Decimal: decimal.Decimal,
    datetime.date: date_transformer,
    datetime.datetime: datetime_transformer,
    dict: lambda x: x
  })



class FieldParsingException(Exception):
  pass


MISSING = object()

@dataclasses.dataclass()
class DataclassParser(object):


  path: str
  """
  Input path
  """
  input_data: typing.Dict[str, typing.Any]
  """
  Input Yaml data
  """

  created_dataclass: typing.Type

  type_map: typing.Mapping[type, typing.Callable] = default_type_map()
  """
  Maps type to factory class that converts to this type
  """

  init_kwargs: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)
  """
  Kwargs used to construct this instance
  """

  @classmethod
  def parse(cls, input: dict, type: typing.Type):
    return DataclassParser(".", input, type).parse_data()

  def has_default(self, field: dataclasses.Field) -> FieldDefault:
    if field.default != dataclasses.MISSING:
      return FieldDefault(True, field.default)
    if field.default_factory != dataclasses.MISSING:
      return FieldDefault(True, field.default_factory())
    return FieldDefault()

  def parse_union(self, field_type):
    parameters = set(field_type.__args__)
    if len(parameters) != 2:
      raise ValueError(f"We support only optional annotation not {type}")
    if type(None) not in parameters:
      raise ValueError(f"We support only optional annotation not {type}")
    parameters.remove(type(None))
    if len(parameters) != 1:
      raise ValueError(f"We support only optional annotation not {type}")
    return FieldDescription(is_sequence=False, is_optional=True, type=parameters.pop())

  def parse_sequence(self, field_type):
    return FieldDescription(is_sequence=True, is_optional=False, type=field_type.__args__[0])

  def parse_field(self, field: dataclasses.Field) -> FieldDescription:
    type = field.type
    if isinstance(type, typing._GenericAlias):
      if type.__origin__ not in {typing.Union, Sequence}:
        raise ValueError(f"We support only optional and sequence annotation not {type}")
      if type.__origin__ == typing.Union:
        response = self.parse_union(type)
      else:
        response = self.parse_sequence(type)
    else:
      response = FieldDescription(is_optional=False, is_sequence=False, type=type)
    default = self.has_default(field)
    if default.has_default:
      response.is_optional = True
      response.default = default.default_value
    response.name = field.name
    return response

  def parse_data(self):
    for field in dataclasses.fields(self.created_dataclass):
      field_description = self.parse_field(field)
      self.process_field(field_description)
    return self.created_dataclass(**self.init_kwargs)

  def create_dataclass_parser(self, field: FieldDescription):
    def parse_func(value: typing.Mapping):
      parser = DataclassParser(
        path=f"{self.path}.{field.name}",
        input_data=value,
        type_map=self.type_map,
        created_dataclass=field.type
      )
      return parser.parse_data()
    return parse_func

  def get_transformer(self, field: FieldDescription):
    if field.type in self.type_map:
      return self.type_map[field.type]
    try:
      dataclasses.fields(field.type)
      return self.create_dataclass_parser(field)
    except TypeError:
      raise ValueError(f"Unparseable field type {type}.")

  def process_field(self, field: FieldDescription):

    raw_value = self.input_data.get(field.name, MISSING)

    if raw_value is MISSING:
      if not field.is_optional:
        raise ValueError(f"Field {field.name} is missing and not optional at path {self.path}")
      self.init_kwargs[field.name] = field.default
      return

    transformer = self.get_transformer(field)

    try:
      if field.is_sequence:
        response = [transformer(item) for item in raw_value]
      else:
        response = transformer(raw_value)
    except FieldParsingException as e:
      raise
    except Exception as e:
      raise FieldParsingException(f"Field {field.name} unparseable at path {self.path}") from e

    self.init_kwargs[field.name] = response



