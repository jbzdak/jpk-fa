# coding=utf-8

import pathlib

from jpk_fa import utils

from freezegun import freeze_time

from lxml import etree

from doctest import Example
from lxml.doctestcompare import LXMLOutputChecker

DATA_DIR = pathlib.Path(__file__).parent / "data"

SELLER = DATA_DIR  / 'seller.yml'
INVOICE = DATA_DIR / 'invoice1.yml'



def test_render():
  with freeze_time("1985-09-19"):
    expected = (DATA_DIR / 'expected.xml').read_text().strip()

    # from xml import etree
    # expected = etree.tostring(etree.fromstring(expected), pretty_print=True)
    actual = utils.render_from_source_file(SELLER, INVOICE).strip()
    assert actual == expected
