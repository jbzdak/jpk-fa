# coding=utf-8


import dataclasses
import abc
import datetime
import decimal
import typing

import jinja2

import pathlib


TaxRates = typing.Sequence[int]

Seller = dict


def quantize(number: decimal.Decimal) -> decimal.Decimal:
  return number.quantize(decimal.Decimal(".01"), rounding=decimal.ROUND_HALF_DOWN)



@dataclasses.dataclass()
class BuyerTaxId(object):
  country_code: str
  tax_id: str


@dataclasses.dataclass()
class InvoiceLine(object):
  name: str
  unit: str
  quantity: decimal.Decimal
  unit_price_pre_tax: decimal.Decimal
  tax_rate: int
  tax_rate_percent: int = None

  invoice_no: str = None

  @property
  def total_net_price(self) -> decimal.Decimal:
    return quantize(self.quantity * self.unit_price_pre_tax)


@dataclasses.dataclass()
class Buyer(object):
  name: str
  address: str
  buyer_eu_tax_id: typing.Optional[BuyerTaxId]


@dataclasses.dataclass()
class Header(object):
  date_from: datetime.date
  date_to: datetime.date
  currency: str = 'PLN'
  tax_authority_code: str = 'REPLACE_ME_WITH_GREP'



TAX_LINE_NET_FIELD_NAMES = {
  0: "13_1",
  1: "13_2",
  2: "13_3",
  3: "13_4",
  4: "13_5",
  -1: "13_6",
}


TAX_LINE_TAX_FIELD_NAMES = {
  0: "14_1",
  1: "14_2",
  2: "14_3",
  3: "14_4",
  4: "14_5",
  -1: None
}


@dataclasses.dataclass()
class TaxLine(object):
  tax_rate_id: int
  total_pre_tax: decimal.Decimal
  tax_rate: int = None

  @property
  def field_name(self) -> str:
    return TAX_LINE_NET_FIELD_NAMES[self.tax_rate_id]

  @property
  def tax_field_name(self) -> typing.Optional[str]:
    return TAX_LINE_TAX_FIELD_NAMES[self.tax_rate_id]

  @property
  def total_tax(self) -> decimal.Decimal:
    tax_rate = quantize(decimal.Decimal(self.tax_rate) / decimal.Decimal(100))
    return quantize(tax_rate * self.total_pre_tax)


@dataclasses.dataclass()
class InvoiceChecksum(object):

  invoice_count: int
  grand_total: decimal.Decimal


@dataclasses.dataclass()
class LinesChecksum(object):
  line_count: int
  trand_total_pre_tax: decimal.Decimal


@dataclasses.dataclass()
class Invoice(object):
  invoice_no: str
  issue_date: datetime.date
  buyer: Buyer
  service_date: datetime.date
  lines: typing.Sequence[InvoiceLine]

  total_after_tax: decimal.Decimal
  tax_lines: typing.Sequence[TaxLine]

  seller: Seller = None


@dataclasses.dataclass()
class JPKFAContext(object):
  tax_rates: TaxRates

  header: Header
  seller: Seller
  invoices: typing.Sequence[Invoice]

  invoice_checksum: InvoiceChecksum = None
  lines_checksum: LinesChecksum = None

  now: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)

  lines: typing.Sequence[InvoiceLine] = None

  def __post_init__(self):
    self.invoice_checksum = InvoiceChecksum(
      invoice_count=len(self.invoices),
      grand_total=sum((i.total_after_tax for i in self.invoices), decimal.Decimal("0"))
    )
    self.lines_checksum = LinesChecksum(0, decimal.Decimal(0))
    self.lines = []
    for invoice in self.invoices:
      invoice.seller = self.seller
      for tax_line in invoice.tax_lines:
        tax_line.tax_rate = self.tax_rates[tax_line.tax_rate_id]
      for line in invoice.lines:
        line.invoice_no = invoice.invoice_no
        line.tax_rate_percent = self.tax_rates[line.tax_rate]
        self.lines_checksum.line_count+=1
        self.lines_checksum.trand_total_pre_tax+=line.total_net_price
        self.lines.append(line)