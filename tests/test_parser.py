# coding=utf-8
import dataclasses
import datetime
import decimal

import pytest

import typing

from jpk_fa import parser

INVALID_FIELDS = [
  typing.Collection[str],
  typing.Union[str, int],
]

VALID_FIELDS = [
  [typing.Optional[str], parser.FieldDescription(str, True, False)],
  [typing.Optional[int], parser.FieldDescription(int, True, False)],
  [str, parser.FieldDescription(str, False, False)],
  [int, parser.FieldDescription(int, False, False)],
  [typing.Sequence[str], parser.FieldDescription(str, False, True)],
  [typing.Sequence[int], parser.FieldDescription(int, False, True)],
]


@dataclasses.dataclass()
class SimpleDataclass(object):

  foo: str
  bar: int
  baz: float
  foobar: datetime.date
  foobaz: decimal.Decimal


@pytest.fixture()
def simple_parser_factory():
  def factory(input_data):
    return parser.DataclassParser(
      path="/",
      input_data=input_data,
      created_dataclass=SimpleDataclass,
    )
  return factory


@pytest.mark.parametrize('type', INVALID_FIELDS)
def test_invalid(simple_parser_factory, type):
  parser = simple_parser_factory({})
  with pytest.raises(ValueError):
    field = dataclasses.field()
    field.type=type
    parser.parse_field(field)

@pytest.mark.parametrize('type, expected', VALID_FIELDS)
def test_valid(simple_parser_factory, type, expected):
  field = dataclasses.field()
  field.type=type
  parser = simple_parser_factory({})
  assert parser.parse_field(field) == expected


TEST_PARSING_DATA = [
  [
    {'foo': 'foo', "bar": 1, "baz": 1.0, 'foobar': "1985-09-19", 'foobaz': "1.23"},
    SimpleDataclass("foo", 1, 1.0, datetime.date(1985, 9, 19), decimal.Decimal("1.23"))
  ],
  [
    {'foo': 'foo', "bar": '1', "baz": '1.0', 'foobar': "1985-09-19", 'foobaz': "1.23"},
    SimpleDataclass("foo", 1, 1.0, datetime.date(1985, 9, 19), decimal.Decimal("1.23"))
  ],
]

@pytest.mark.parametrize('input, expected', TEST_PARSING_DATA)
def test_simple_parsing(input, expected) :
  assert parser.DataclassParser.parse(input, SimpleDataclass) == expected


@dataclasses.dataclass()
class DataclassWithSequencesAndOptionals(object):

  foo: str
  foobaz: typing.Sequence[str]
  baz: typing.Optional[str]
  bar: str = "default"
  foobar: typing.Optional[str] = "default"


TEST_PARSING_DATA = [
  [
    {'foo': 'foo', "bar": 'bar', "baz": 'baz', 'foobaz': ['foo', 'bar', 'baz'], 'foobar': "foobar"},
    DataclassWithSequencesAndOptionals(
      foo="foo", bar='bar', baz='baz', foobaz=['foo', 'bar', 'baz'], foobar='foobar'
    )
  ],
  [
    {'foo': 'foo', 'foobaz': ['foo', 'bar', 'baz']},
    DataclassWithSequencesAndOptionals(
      foo="foo", foobaz=['foo', 'bar', 'baz'], baz=None
    )
  ],
]

@pytest.mark.parametrize('input, expected', TEST_PARSING_DATA)
def test_optionals_parsing(input, expected) :
  assert parser.DataclassParser.parse(input, DataclassWithSequencesAndOptionals) == expected


@dataclasses.dataclass()
class ChildDataclass(object):
  foo: str

@dataclasses.dataclass()
class NestedDataclass(object):

  foo: ChildDataclass
  bar: typing.Sequence[ChildDataclass]


TEST_PARSING_DATA = [
  [
    {'foo': {'foo': 'foo'}, 'bar': [{'foo': 'barfoo'}, {'foo': 'bazfoo'}]},
    NestedDataclass(
      foo=ChildDataclass('foo'), bar=[ChildDataclass('barfoo'), ChildDataclass('bazfoo')]
    )
  ],
  [
    {'foo': {'foo': 'foo'}, 'bar': []},
    NestedDataclass(
      foo=ChildDataclass('foo'), bar=[]
    )
  ]
]

@pytest.mark.parametrize('input, expected', TEST_PARSING_DATA)
def test_nested_parsing(input, expected) :
  assert parser.DataclassParser.parse(input, NestedDataclass) == expected

