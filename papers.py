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


        home_country = entries.get("home").get("country")

        if home_country == "KAN":
            must_accept = True

        #Checking Completeness
        #Medical Check
        #Check for valid visas
        #Watchlist Check
        passport_check = entries.get("passport")
        first_name_check = entries.get("first_name")
        last_name_check = entries.get("last_name")

        if check_quarantine(entries, countries_contents_json):
            must_quarantine = True
        elif check_record_completeness(entries):
            must_reject = True
        elif valid_visa_check(entries, countries_contents_json):
            must_reject = True
        elif watchlist_check(passport_check,first_name_check,last_name_check,watchlist_contents_json):
            must_secondary = True
        else:
            must_accept = True

        if must_quarantine:
            decisions.append("Quarantine")
        elif must_reject:
            decisions.append("Reject")
        elif must_secondary:
            decisions.append("Secondary")
        else:
            decisions.append("Accept")

    return decisions

def watchlist_check(passport, first_name, last_name, watchlist_contents):
    """

    :param passport:
    :param first_name:
    :param last_name:
    :param watchlist_contents:
    :return: return true if on list, false if not
    """
    for person in watchlist_contents:
        if person.get("passport") == passport.upper():
            return True

        elif person.get("first_name") == first_name.upper()\
            and person.get("last_name") == last_name.upper():

            return True

    return False


def valid_visa_check(entry, countries_contents):
    """

    :param entry:
    :param countries_contents:
    :return: return true if needs to be rejected, false otherwise
    """
    entry_reason = entry.get("entry_reason")
    home_country = entry.get("home").get("country")

    if entry_reason == "visit" or entry_reason == "transit":

        if entry_reason == "visit" and countries_contents[home_country].get("visitor_visa_required") == "1":
            if entry.get("visa") is None:
                return True
            else:
                end_date = entry.get("visa").get("date")
                if valid_date_format(end_date):
                    if not valid_date_check(end_date):
                        return True
                else:
                    return["Reject"]

        if entry_reason =="transit" and countries_contents[home_country].get("transit_visa_required")== "1":
            if entry.get("visa") is None :
                return True
            else:
                if valid_date_format(entry.get("visa").get("date")):
                    end_date = entry.get("visa").get("date")

                    if not valid_date_check(end_date):
                        return True
                else:
                    return True
    return False


def check_quarantine(entry, countries_contents):
    """

    :param from_country:
    :param via_country:
    :param countries_contents:
    :return:
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
    """

    :param entry:
    :return: returns true if reject, false if passed
    """
    valid = True

    if not valid_passport_format(entry.get("passport")):
        valid = False

    for locations in entry.get("home"):
        if entry.get("home")[locations] == "":
            valid = False
    for places in entry.get("from"):
        if entry.get("from")[places] == "":
            valid = False
    for key in entry:
        if entry[key] == "":
            valid = False

    if valid is False:
        return True

    return False

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


