#!/usr/bin/env python3

""" Assignment 2, INF1340, Fall 2014. Papers, Please.

This module contains nine functions. The main function is decide and utilizes the other eight functions to review
documents provided by travelers and directives from the ministry to control the flow of people entering Kanadia.

The function receives three files: the input_file, watchlist_file, and countries_file. If one of these files is not
present, a "FileNotFoundError" is raised.

A traveller can receive a decision of "Accept", "Reject", "Secondary", or "Quarantine".

Example:
    $ python papers.py
"""

__author__ = "Lauren Olar and Christopher Piche"
__email__ = "lauren.olar@mail.utoronto.ca and christopher.piche@mail.utoronto.ca"

__copyright__ = "2014 Lauren Olar and Christopher Piche"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line

import re
import datetime
import json


def decide(input_file, watchlist_file, countries_file):
    """Decides whether a traveller's entry into Kanadia should be accepted.

    :param input_file: The name of a JSON formatted file that contains cases to decide
    :param watchlist_file: The name of a JSON formatted file that contains names and passport numbers on a watchlist
    :param countries_file: The name of a JSON formatted file that contains country data, such as whether
        an entry or transit visa is required, and whether there is currently a medical advisory
    :return: List of strings. Possible values of strings are: "Accept", "Reject", "Secondary", and "Quarantine"
    """

    #Opening the three aforementioned files to get data for review and loading their contents.
    with open(input_file, "r") as file_reader:
        input_file_contents = file_reader.read()

    json_input_contents = json.loads(input_file_contents)

    with open(watchlist_file, "r") as file_reader:
        watchlist_file_contents = file_reader.read()

    watchlist_contents_json = json.loads(watchlist_file_contents)

    with open(countries_file, "r") as file_reader:
        countries_file_contents = file_reader.read()

    countries_contents_json = json.loads(countries_file_contents)

    #Instantiate list that will return the results.
    decisions = []

    for entries in json_input_contents:

        #Getting values to be passed to functions.
        home_country = entries.get("home").get("country")
        passport_check = entries.get("passport")
        first_name_check = entries.get("first_name")
        last_name_check = entries.get("last_name")

        if check_quarantine(entries, countries_contents_json):
            decisions.append("Quarantine")

        elif check_record_completeness(entries):
            decisions.append("Reject")

        elif valid_visa_check(entries, countries_contents_json) and home_country != "KAN":
            decisions.append("Reject")

        elif watchlist_check(passport_check, first_name_check, last_name_check, watchlist_contents_json):
            decisions.append("Secondary")

        elif kanadia_check(entries):
            decisions.append("Accept")

        else:
            decisions.append("Accept")

    return decisions

#Most functions that follow could have been collapsed into the decide function. However,
#for readability and understandability, and use of functions by other modules or functions, the functions below are
#separated as appears.


def kanadia_check(entry):
    """Checks if returning person is Kanadian citizen.

    :param entry: record of person under review, in dictionary format
    :return: Boolean; True if accepted, False if otherwise
    """

    if entry.get("home").get("country") == "KAN" and entry.get("entry_reason") == "returning":
        return True

    return False


def watchlist_check(passport, first_name, last_name, watchlist_contents):
    """Checks passport and, or, combination of first_name and last_name to determine if person is on watchlist.

    :param passport: string of five sets of five alpha-numeric characters separated by dashes
    :param first_name: string of citizen's first name
    :param last_name: string of citizen's last name
    :param watchlist_contents: dictionary of JSON file contents containing people on the watchlist
    :return: Boolean; True if on watchlist, False if otherwise
    """

    for person in watchlist_contents:
        #Corrects passport alpha characters to be all upper case
        if person.get("passport") == passport.upper():
            return True

        #Corrects first_name and last_name alpha characters to be all upper case
        elif person.get("first_name") == first_name.upper()\
                and person.get("last_name") == last_name.upper():
            return True

    return False


def valid_visa_check(entry, countries_contents):
    """Checks, if necessary, based on travel and visit entry, whether person has visa and whether valid.

    :param entry: record of person under review, in dictionary format
    :param countries_contents: the name of a JSON formatted file that contains country data such as whether a transit
    or visit visa is required
    :return: Boolean; True if visa is not valid or not found, False if otherwise
    """

    entry_reason = entry.get("entry_reason")
    home_country = entry.get("home").get("country")

    if entry_reason == "visit" or entry_reason == "transit":

        if entry_reason == "visit" and countries_contents[home_country].get("visitor_visa_required") == "1":
            #Check that citizen has visa and it is a valid format, as required
            if entry.get("visa") is None or not valid_visa_format(entry.get("visa").get("code")):
                return True
            else:
                end_date = entry.get("visa").get("date")
                if valid_date_format(end_date):
                    if not valid_date_check(end_date):
                        return True
                else:
                    return True

        if entry_reason == "transit" and countries_contents[home_country].get("transit_visa_required") == "1":
            if entry.get("visa") is None or not valid_visa_format(entry.get("visa").get("code")):
                return True
            else:
                end_date = entry.get("visa").get("date")
                if valid_date_format(end_date):
                    if not valid_date_check(end_date):
                        return True
                else:
                    return True
    return False


def valid_visa_format(visa_check):
    """
    Checks to see if the persons visa has the valid format of two sets of 5 alpha-numeric characters separated by
    dashes.

    :param visa_check: alpha-numeric string
    :return: Boolean; True if valid format, False if otherwise
    """

    visa_format = re.compile('^\w{5}-\w{5}$')

    if visa_format.match(visa_check):
        return True
    else:
        return False


def check_quarantine(entry, countries_contents):
    """Checks to see if person is entering from, or travelling via, a country with a medical advisory.

    :param entry: record of person under review, in dictionary format
    :param countries_contents: the name of a JSON formatted file that contains country data such as whether there is
    currently a medical advisory
    :return: Boolean; True if there is a medical advisory, False if otherwise
    """

    from_country = entry.get("from").get("country")

    if countries_contents[from_country].get("medical_advisory") != "":
        return True

    else:
        if entry.get("via") is not None:
            via_country = entry.get("via").get("country")
            if countries_contents[via_country].get("medical_advisory") != "":
                return True

    return False


def check_record_completeness(entry):
    """Checks the completeness of person's required information.

    :param entry: record of person under review, in dictionary format
    :return: Boolean; True if incomplete information, False if otherwise
    """

    if not valid_passport_format(entry.get("passport")):
        return True

    for locations in entry.get("home"):
        if entry.get("home")[locations] == "":
            return True
    for places in entry.get("from"):
        if entry.get("from")[places] == "":
            return True
    for key in entry:
        if entry[key] == "":
            return True

    return False


def valid_date_check(issue_date):
    """Checks to see if the visa is valid, less than two years old.

    :param issue_date: string of the date the visa was issued to the person
    :return: Boolean; True if the format is valid, False if otherwise
    """

    start_date = datetime.datetime.today()
    issue_date = datetime.datetime.strptime(issue_date, '%Y-%m-%d')
    difference = start_date - issue_date
    difference_in_years = difference.days/365.2425

    if difference_in_years >= 2:
        return False

    return True


def valid_passport_format(passport_number):
    """Checks whether a passport number is five sets of five alpha-numeric characters separated by dashes.

    :param passport_number: alpha-numeric string
    :return: Boolean; True if format is valid, False if otherwise
    """

    passport_format = re.compile('^\w{5}-\w{5}-\w{5}-\w{5}-\w{5}$')

    if passport_format.match(passport_number):
        return True
    else:
        return False


def valid_date_format(date_string):
    """Checks whether a date has the format YYYY-mm-dd in numbers.

    :param date_string: date to be checked
    :return: Boolean; True if format is valid, False if otherwise
    """

    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True

    except ValueError:
        return False