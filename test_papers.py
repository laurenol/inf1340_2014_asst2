#!/usr/bin/env python3

""" Module to test papers.py """

__author__ = "Lauren Olar and Christopher Piche"
__email__ = "lauren.olar@mail.utoronto.ca and christopher.piche@mail.utoronto.ca"

__copyright__ = "2014 Lauren Olar and Christopher Piche"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line

import pytest
from papers import decide


def test_basic():
    """
    Test people whose home country is Kanadia to ensure correct prioritizing of results returned
    """

    assert decide("test_returning_citizen.json", "watchlist.json", "countries.json") == ["Accept", "Accept"]
    assert decide("test_quarantine_over_accept.json", "watchlist.json", "countries.json") == \
                                                                                ["Quarantine", "Quarantine"]
    assert decide("test_reject_over_accept.json", "watchlist.json", "countries.json") == ["Reject"]
    assert decide("test_secondary_over_accept.json", "watchlist.json", "countries.json") == ["Secondary"]


def test_quarantine():
    """
    Test to verify that people coming from, or via, countries with medical advisories are quarantined.
    """
    assert decide("test_quarantine.json", "watchlist.json", "countries.json") == ["Quarantine", "Quarantine", "Accept",
                                                                                  "Accept"]


def test_watchlist():
    """
    Test to verify that function correctly processes people on watchlist
    """
    assert decide("test_watchlist.json", "watchlist.json", "countries.json") == ["Secondary", "Secondary"]


def test_completeness():
    """
    Test to verify that people's entries are complete, including all required information
    """
    assert decide("test_completeness.json", "watchlist.json", "countries.json") == ["Reject", "Reject", "Reject",
                                                                                    "Accept"]


def test_have_visa():
    """
    Test to verify that, where visa required, person has said visa
    """
    assert decide("test_have_visa.json", "watchlist.json", "countries.json") == ["Reject", "Accept", "Reject", "Accept"]


def test_visa_date():
    """
    Test to verify validity of visa
    """
    assert decide("test_visa_date.json", "watchlist.json", "countries.json") == ["Reject", "Reject"]


def test_passport_format():
    """
    Test to verify that people with incorrect passport formats will be rejected
    """
    assert decide("test_passport_format.json", "watchlist.json", "countries.json") == ["Reject", "Reject"]


def test_date_format():
    """
    Test to verify that people with visa having invalid date formats are rejected, as they should be.
    """
    assert decide("test_date_format.json", "watchlist.json", "countries.json") == ["Reject", "Reject"]


def test_files():
    """
    Test to ensure appropriate error is raised if require files are not passed
    """
    with pytest.raises(FileNotFoundError):

        decide("test_returning_citizen.json", "", "countries.json")