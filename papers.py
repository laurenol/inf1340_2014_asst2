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

    with open(input_file,"r") as file_reader:
        input_file_contents = file_reader.read()

    json_input_contents = json.loads(input_file_contents)

    with open(watchlist_file, "r") as file_reader:
        watchlist_file_contents = file_reader.read()

    watchlist_contents_json = json.loads(watchlist_file_contents)
    with open(countries_file, "r") as file_reader:
        countries_file_contents = file_reader.read()

    countries_contents_json = json.loads(countries_file_contents)

    decisions = []


    for entries in json_input_contents:
        must_quarantine = False
        must_secondary = False
        must_reject = False
        must_accept = False

        from_country = entries.get("from").get("country")
        home_country = entries.get("home").get("country")

        #Checking Completeness
        valid = True

        if(not valid_passport_format(entries.get("passport"))):
            valid = False

        for locations in entries.get("home"):
             if entries.get("home")[locations] == "":
                valid = False
        for places in entries.get("from"):
             if entries.get("from")[places] == "":
                valid = False
        for key in entries:
             if entries[key] == "":
                valid = False

        if valid == False:
           must_reject = True

        #Medical Check


        if countries_contents_json[from_country].get("medical_advisory") != "":
            must_quarantine = True

        else:
            if(entries.get("via") != None):
                via_country = entries.get("via").get("country")

                if countries_contents_json[via_country].get("medical_advisory") != "":
                    must_quarantine = True



        if home_country == "KAN":
            must_accept = True

        #Check for valid visas
        entry_reason = entries.get("entry_reason")

        if entry_reason == "visit" or entry_reason == "transit":
            home_country = entries.get("home").get("country")

            if entry_reason == "visit" and countries_contents_json[home_country].get("visitor_visa_required") == "1":
                if(entries.get("visa") == None):
                    must_reject = True
                else:
                    end_date = entries.get("visa").get("date")
                    if valid_date_format(end_date):
                        if not valid_date_check(end_date):
                            must_reject = True
                    else:
                        return["Reject"]

            if entry_reason =="transit" and countries_contents_json[home_country].get("transit_visa_required")== "1":
                if(entries.get("visa") == None):
                    must_reject = True
                else:
                    if valid_date_format(entries.get("visa").get("date")):
                        end_date = entries.get("visa").get("date")

                        if not valid_date_check(end_date):
                            must_reject = True
                    else:
                        must_reject = True

        #Watchlist Check
        passport_check = entries.get("passport")
        first_name_check = entries.get("first_name")
        last_name_check = entries.get("last_name")

        for person in watchlist_contents_json:
            if person.get("passport") == passport_check.upper():
                must_secondary = True

            elif person.get("first_name") == first_name_check.upper()\
                    and person.get("last_name") == last_name_check.upper():
                must_secondary = True

        if must_quarantine:
            decisions.append("Quarantine")
        elif must_reject:
            decisions.append("Reject")
        elif must_secondary:
            decisions.append("Secondary")
        else:
            decisions.append("Accept")

    return decisions




def valid_date_check(issue_date):
    """
    Checks to see if the visa is valid (<2 years old)
    :param issue_date: the date the visa was issued to the person
    :return: Boolean: True if valid, false if not
    """

    start_date = datetime.datetime.today()
    issue_date = datetime.datetime.strptime(issue_date, '%Y-%m-%d')
    difference = start_date - issue_date
    difference_in_years = difference.days/365.2425

    if difference_in_years >= 2:
        return False

    return True

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
