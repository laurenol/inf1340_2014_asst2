#!/usr/bin/env python3

""" Module to test papers.py  """

__author__ = 'Susan Sim'
__email__ = "ses@drsusansim.org"

__status__ = "Prototype"

# imports one per line
import pytest
from papers import decide

def test_basic():
    assert decide("test_returning_citizen.json", "watchlist.json", "countries.json") == ["Accept", "Accept"]
    #assert decide("test_watchlist.json", "watchlist.json", "countries.json") == ["Secondary"]
    assert decide("test_quarantine.json", "watchlist.json", "countries.json") == ["Quarantine", "Quarantine", "Accept", "Accept"]

def test_quarantine():
    assert decide("test_quarantine.json", "watchlist.json", "countries.json") == ["Quarantine", "Quarantine", "Accept",
                                                                                  "Accept"]

def test_watchlist():
    assert decide("test_watchlist.json", "watchlist.json", "countries.json") == ["Secondary", "Secondary"]

def test_completeness():
    assert decide("test_completeness.json", "watchlist.json", "countries.json") == ["Reject" , "Reject" , "Reject",
                                                                                    "Accept"]
def test_have_visa():
    assert decide("test_have_visa.json", "watchlist.json", "countries.json") == ["Reject", "Accept", "Reject", "Accept"]

def test_visa_date():
    assert decide("test_visa_date.json", "watchlist.json", "countries.json") == ["Reject", "Reject"]

def test_passport_format():
    assert decide("test_passport_format.json", "watchlist.json", "countries.json") == ["Reject", "Reject"]

def test_date_format():
    assert decide("test_date_format.json", "watchlist.json", "countries.json") == ["Reject", "Reject"]

def test_files():
   with pytest.raises(FileNotFoundError):

        decide("test_returning_citizen.json", "", "countries.json")

# add functions for other tests

