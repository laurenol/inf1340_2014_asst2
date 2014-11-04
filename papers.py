#!/usr/bin/env python3

""" Computer-based immigration office for Kanadia"""

__author__ = 'Susan Sim'
__email__ = "ses@drsusansim.org"

__copyright__ = "2014 Susan Sim"
__license__ = "MIT License"

__status__ = "Prototype"

# imports one per line
import re
import datetime
import json


def decide(input_file, watchlist_file, countries_file):
    """
    Decides whether a traveller's entry into Kanadia should be accepted

    :param input_file: The name of a JSON formatted file that contains cases to decide
    :param watchlist_file: The name of a JSON formatted file that contains names and passport numbers on a watchlist
    :param countries_file: The name of a JSON formatted file that contains country data, such as whether
        an entry or transit visa is required, and whether there is currently a medical advisory
    :return: List of strings. Possible values of strings are: "Accept", "Reject", "Secondary", and "Quarantine"
    """

    with open("test_returning_citizen.json","r") as file_reader:
        input_file_contents = file_reader.read()

    json_input_contents = json.loads(input_file_contents)

    with open("countries.json", "r") as file_reader:
        countries_file_contents = file_reader.read()

    countries_contents_json = json.loads(countries_file_contents)

    for entries in json_input_contents:
        country_check = entries.get("from").get("country")

        if countries_contents_json[country_check].get("medical_advisory") != "":
            return["Quarantine"]

        else:
            if(entries.get("via") != None):
                via_country = entries.get("via").get("country")

                if countries_contents_json[via_country].get("medical_advisory") != "":
                    return["Quarantine"]

    #CHECK FOR COMPLETENESS
    #for entry in json_input_contents:
    #    valid = True

    #    for locations in entry.get("home"):
    #         if entry.get("home")[locations] == "":
    #            valid = False
    #    for places in entry.get("from"):
    #         if entry.get("from")[places] == "":
    #            valid = False
    #    for key in entry:
    #         if entry[key] == "":
    #            valid = False

        #if valid == False:
        ##   return["Reject"]

    with open(watchlist_file, "r") as file_reader:
        watchlist_file_contents = file_reader.read()

    watchlist_contents_json = json.loads(watchlist_file_contents)

    for entries in json_input_contents:
        passport_check = entries.get("passport")
        first_name_check = entries.get("first_name")
        last_name_check = entries.get("last_name")

        for person in watchlist_contents_json:
            if person.get("passport") == passport_check.upper():
                return["Secondary"]

            elif person.get("first_name") == first_name_check.upper()\
                    and person.get("last_name") == last_name_check.upper():
                return["Secondary"]

    return ["Reject"]


def valid_passport_format(passport_number):
    """
    Checks whether a passport number is five sets of five alpha-number characters separated by dashes
    :param passport_number: alpha-numeric string
    :return: Boolean; True if the format is valid, False otherwise
    """
    passport_format = re.compile('.{5}-.{5}-.{5}-.{5}-.{5}')


    if passport_format.match(passport_number):
        return True
    else:
        return False


def valid_date_format(date_string):
    """
    Checks whether a date has the format YYYY-mm-dd in numbers
    :param date_string: date to be checked
    :return: Boolean True if the format is valid, False otherwise
    """
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
