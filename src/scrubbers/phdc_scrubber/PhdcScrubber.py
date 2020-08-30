# Adapted from code received from Assoc. Prof. Nicki Tiffen, Centre for Infectious Disease, UCT
# 11 August, 2020

# The clever bits are likely hers, while the Mistakes are likely ours

# import necessary modules
import datetime
import logging
import os
import re

from phdc_scrubber import STREET_TYPES_FILENAME, STREET_NAME_LOOKUP_FILENAME, HERE_PLACE_LOOKUP_FILENAME
from phdc_scrubber import STREET_NO_REGEX_PATTERN, SQL


def _check_data_file_exists(file_path) -> None:
    """Utility function checking that a datafile exists, and is, in fact, a file"""
    if not os.path.exists(file_path):
        raise RuntimeError(f"'{file_path}' doesn't exist!")
    elif not os.path.isfile(file_path):
        raise RuntimeError(f"'{file_path}' isn't a file!")
    else:
        logging.debug(f"'{file_path}' all set to be read.")


def create_street_types_list(lookup_file_dir) -> list:
    """Reads street type datafile to create a list of street types"""
    street_types_path = os.path.join(lookup_file_dir, STREET_TYPES_FILENAME)
    _check_data_file_exists(street_types_path)

    if not os.path.exists(street_types_path):
        raise RuntimeError(f"'{street_types_path}' doesn't exist! Can't create street types list")

    street_types_set = set([])
    with open(street_types_path) as street_types_file:
        for line in street_types_file:
            street_types_set ^= {
                line.upper().strip()
            }

    return list(street_types_set)


def create_address_reference(lookup_file_dir) -> dict:
    """Reads datafiles in lookup_file_dir to create a reference dir"""
    address_lookup_dict = {}

    # PHDC (?) street name lookup
    phdc_path = os.path.join(lookup_file_dir, STREET_NAME_LOOKUP_FILENAME)
    _check_data_file_exists(phdc_path)

    with open(phdc_path) as dict_file:
        lines = dict_file.readlines()
        logging.debug(f"{len(lines)} lines in address dict 1 ('{STREET_NAME_LOOKUP_FILENAME}')")

        for line in lines[1:]:
            #    print(line)
            line = line.upper()
            line = line.strip()
            line = line.split('\t')

            dict_postcode = line[2]
            dict_postcode = dict_postcode.strip()
            dict_street_name = line[0]
            dict_street_name = dict_street_name.strip()
            dict_street_type = line[1]
            dict_street_type = dict_street_type.strip()

            if dict_street_type not in street_types and dict_street_type != "" and dict_street_type != " ":
                street_types.append(dict_street_type)
            dict_suburb = line[3]
            dict_suburb = dict_suburb.strip()
            dict_town = line[4]
            dict_town = dict_town.strip()
            dict_municipality = line[5]
            dict_municipality = dict_municipality.strip()
            dict_list = [dict_street_name, dict_street_type, dict_suburb, dict_town, dict_municipality]
            if dict_postcode != '':
                if dict_postcode not in address_lookup_dict:
                    address_lookup_dict[dict_postcode] = []
                address_lookup_dict[dict_postcode].append(dict_list)

    # HERE Place lookup
    here_path = os.path.join(lookup_file_dir, HERE_PLACE_LOOKUP_FILENAME)
    _check_data_file_exists(here_path)

    with open(here_path) as dict_file:
        lines = dict_file.readlines()
        logging.debug(f"{len(lines)} lines in address dict 2 ('{HERE_PLACE_LOOKUP_FILENAME}')")

        for line in lines[1:]:
            line = line.upper()
            line = line.strip()
            line = line.split('\t')
            dict_street_name = line[0]
            dict_street_name = dict_street_name.strip()
            dict_street_type = line[1]
            dict_street_type = dict_street_type.strip()
            dict_suburb = line[2]
            dict_suburb = dict_suburb.strip()
            dict_town = line[3]
            dict_town = dict_town.strip()
            dict_municipality = line[4]
            dict_municipality = dict_municipality.strip()
            dict_list = [dict_street_name, dict_street_type, dict_suburb, dict_town, dict_municipality]
            if dict_suburb != '':
                if dict_suburb not in address_lookup_dict:
                    address_lookup_dict[dict_suburb] = []
                address_lookup_dict[dict_suburb].append(dict_list)
            if dict_town != '':
                if dict_town not in address_lookup_dict:
                    address_lookup_dict[dict_town] = []
                address_lookup_dict[dict_town].append(dict_list)

    return address_lookup_dict


STREET_NO_REGEX = re.compile(STREET_NO_REGEX_PATTERN)


def get_street_info(address_string_all, street_types_lookup) -> tuple:
    """Extracting various info from address string - street type and number, and returns newly formatted string"""
    # Street Type
    temp_street_type = ''
    temp_address_string = address_string_all
    for street_type in street_types_lookup:
        if street_type in address_string_all:
            logging.debug(f"'{street_type}' in '{address_string_all}'")
            temp_street_type = street_type
            temp_address_string = address_string_all.replace(street_type, " ")
            break

    temp_address_string = temp_address_string.upper()

    # Street Number
    found_numbers = STREET_NO_REGEX.search(temp_address_string)
    if found_numbers is not None:
        temp_street_number = found_numbers.group()
        temp_street_number = temp_street_number.strip()
        temp_street_number = temp_street_number.strip("NO")
    else:
        temp_street_number = ""

    return temp_street_type, temp_street_number, temp_address_string


def get_matches(address_words, address_string, address_lookup, postcode=None) -> list:
    """Returns a tuple of match information for an address string against the address lookup dict"""
    # Evaluating matches
    postcode_match = postcode in address_lookup
    suburb_town_match = any([
        (word in address_lookup)
        for word in address_words[-4:]
    ])

    # all possible sequential substrings
    address_substrings_set = set([
        address_string[i:i+j]
        for i in range(len(address_string) - 1)
        for j in range(1, len(address_string))
    ])
    logging.debug(f"There are '{len(address_substrings_set)}' possible substrings")
    suburb_town_overlaps = [
        (word in address_lookup)
        for word in address_substrings_set
    ]
    logging.debug(f"There are '{sum(suburb_town_overlaps)}' overlaps with the address dict")

    address_matches = []  # Expected members (match_type, relevant records from address_dict, initial_score)
    if postcode_match:
        address_matches += [
            ('postcode_match', address_lookup[pmi_postcode], 2)
        ]
    if suburb_town_match:
        address_matches += [
            ('suburb_or_town_words_match', address_lookup[word], 1)
            for word in pmi_address_words[-4:]
            if word in address_lookup
        ]
    if any(suburb_town_overlaps):
        address_matches += [
            ('suburb_or_town_string_match', address_lookup[word], 0)
            for word in address_substrings_set
            if word in address_lookup
        ]
    logging.debug(f"There are '{len(address_matches)}' possible matches")

    return address_matches


def score_match(initial_score, address_words, relevant_records, street_number, street_type, postcode_override=None) -> tuple:
    """Generate a score and final address for a particular address string"""
    for dict_record in relevant_records:
        score = initial_score

        dict_streetname = dict_record[0]
        dict_suburb = dict_record[2]
        dict_town = dict_record[3]
        if dict_streetname in address_words[:3]:
            logging.debug('\tstreetname match')
            final_streetnumber = street_number
            final_streetname = dict_streetname
            final_street_type = street_type
            final_suburb = dict_suburb
            final_town = dict_town
            final_postcode = postcode_override if postcode_override else ''
            score += 1
            if final_suburb in address_words[-3:]:
                logging.debug('\tsuburb match')
                score += + 1
            if final_town in address_words[-3:]:
                logging.debug('\ttown match')
                score += 1

            yield score, (final_streetnumber, final_streetname, final_street_type,
                          final_suburb, final_town, final_postcode)


def generate_match_string(match_type, final_tuple, address_row_id, address_id, address_string_all) -> str:
    """Utility function for formatting a final result from the scrubber"""
    (
        final_streetnumber, final_streetname, final_street_type,
        final_suburb, final_town, final_postcode
    ) = final_tuple

    return (f'{match_type}'
            f'\t{str(address_row_id)}\t{str(address_id)}\t{address_string_all}\t'
            f'{final_streetnumber}\t{final_streetname}\t{final_street_type}\t'
            f'{final_suburb}\t{final_town}\t{str(final_postcode)}\t'
            f'{str(score)}\t'
            f'{final_streetnumber} {final_streetname} {final_suburb} {final_town} {str(final_postcode)}')


if __name__ == "__main__":
    import pypyodbc

    # Logging setup
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s-%(module)s.%(funcName)s [%(levelname)s]: %(message)s')

    # ________________________________________________________________________
    # ADDRESS SCRUBBING COMPONENT

    # time how long it takes
    start_time = datetime.datetime.now()
    # ________________________________________________________________________
    # set the working directory
    add_dir = r"C:\geocoding_docs"
    os.chdir(add_dir)
    # ________________________________________________________________________
    # delete the existing geocoded  results file
    try:
        os.remove("geocoded_new_addresses.txt")
    except OSError:
        pass

    try:
        os.remove("geocoded_new_addresses.txt.xml")
    except OSError:
        pass

    try:
        os.remove("output_new_addresses.txt.xml")
    except OSError:
        pass

    try:
        os.remove("output_unmatched_addresses.txt")
    except OSError:
        pass
    # ________________________________________________________________________

    # specify input and output files

    dud_addresses_filename = "output_unmatched_addresses.txt"
    outfile_name = "output_new_addresses.txt"
    outfile = open(outfile_name, "a")
    outfile.close()

    # create a list of already processed address ids (address_row_id)

    already_processed = []
    outfile = open(outfile_name, "r")
    for line in outfile:
        line = line.strip()
        line = line.split('\t')
        # print(line)
        pmi_history_done = line[1].strip()
        if pmi_history_done not in already_processed:
            already_processed.append(pmi_history_done)
    outfile.close()

    # open files for printing results
    outfile = open(outfile_name, "a")
    outfile.write(
        'match_reason\t'
        'address_row_id\tpmi_id\tinput_address\t'
        'final_streetnumber\tfinal_streetname\tfinal_streettype\tfinal_suburb\tfinal_town\tfinal_postcode\t'
        'score\t'
        'final_single_address',
    )

    duds_outfile = open(dud_addresses_filename, "a")
    duds_outfile.write('match_reason\taddress_row_id\tpmi_id\tinput_address')
    # _____________________________________________________________________

    # create list of street types
    street_types = create_street_types_list(add_dir)

    # ------------------------------------------------------------------
    # create reference dictionaries

    address_dict = create_address_reference(add_dir)
    # _______________________________________________________________________
    # make a list of lists for  all addresses pulled in -
    # connect to mssql server pypyodbc and pull in actual addresses

    pmi_addresses = []

    # max address_row_id for 26/10/2016 is 524751803
    # min address_row_id for 26/10/2016 is 505468273

    connection_string = "DSN=biod01_patient"
    connection = pypyodbc.connect(connection_string)

    cursor = connection.cursor()
    cursor.execute(SQL)
    n = 0
    row = cursor.fetchone()
    while row is not None:
        # print('1:',row)
        address_row_id = row[0]

        if address_row_id in already_processed:
            logging.debug(f'already processed {address_row_id}')
        else:
            row_id = row[0]
            pmi_id = row[1]
            pmi_postcode = row[6]
            if pmi_postcode is not None:
                pmi_postcode = pmi_postcode.strip()
            pmi_address_string_all = str(row[2]) + ' ' + str(row[3]) + ' ' + str(row[4]) + ' ' + str(row[5])
            # print('as pulled from database, pmi_address_string_all is', pmi_address_string_all)

            pmi_street_type, pmi_street_number, pmi_address_string = get_street_info(pmi_address_string_all, street_types)
            pmi_address_words = pmi_address_string.split(" ")

            pmi_addresses.append(
                [address_row_id, pmi_id, pmi_street_number, pmi_street_type, pmi_address_string_all, pmi_address_string,
                 pmi_address_words, pmi_postcode])
            n = n + 1
            row = cursor.fetchone()
    # ________________________________________________________________________
    # Compare addresses from patient database to dictionaries
    # address_row_id, pmi_id, pmi_street_number, pmi_street_type, pmi_address_string_all, pmi_address_string, pmi_address_words, pmi_postcode

    clean_scored_addresses = {}

    for pmi_address in pmi_addresses:
        (
            address_row_id, pmi_id, pmi_street_number, pmi_street_type,
            pmi_address_string_all, pmi_address_string, pmi_address_words,
            pmi_postcode
        ) = pmi_address

        len_address_words = len(pmi_address_words)
        logging.debug(pmi_address_string_all)

        # default, no match
        if address_row_id not in clean_scored_addresses:
            logging.debug(f'STORED STRING: no_match\t{str(address_row_id)}\t{str(pmi_id)}\t{pmi_address_string_all}')
            clean_scored_addresses[address_row_id] = [
                0, f'no_match\t{str(address_row_id)}\t{str(pmi_id)}\t{pmi_address_string_all}'
            ]

        # Getting the different match types
        matches = get_matches(pmi_address_words, pmi_address_string, address_dict, pmi_postcode)
        # Scoring the different match types
        for (match_type, records, initial_score) in matches:
            for score, final_tuple in score_match(initial_score,
                                                  pmi_address_words, records,
                                                  pmi_street_number, pmi_street_type,
                                                  pmi_postcode if match_type == 'postcode_match' else None):
                if score > clean_scored_addresses[address_row_id][0]:
                    clean_scored_addresses[address_row_id] = [
                        score,
                        generate_match_string(match_type,
                                              final_tuple,
                                              address_row_id, pmi_id, pmi_address_string_all)
                    ]

    for address_row_id in clean_scored_addresses:
        score = float(clean_scored_addresses[address_row_id][0])
        print_string = clean_scored_addresses[address_row_id][1]

        if score == 0:
            duds_outfile.write(print_string)
        elif score >= 1:
            outfile.write(print_string)

    outfile.close()

    with open(outfile_name, "r") as outfile:
        for final_address in outfile:
            logging.debug(final_address)

    # TIDY UP
    cursor.close()
    connection.close()
    scrub_time = datetime.datetime.now()
    outfile.close()
    duds_outfile.close()
    # address_file.close()
    logging.info(f"Scrubbing complete, took '{scrub_time - start_time}' to do '{n}' rows.")

    # ________________________________________________________________________

    #
