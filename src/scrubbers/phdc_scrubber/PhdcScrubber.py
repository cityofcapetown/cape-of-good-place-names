# Adapted from code received from Assoc. Prof. Nicki Tiffen, Centre for Infectious Disease, UCT
# 11 August, 2020

# The clever bits are likely hers, while the Mistakes are likely ours

from __future__ import print_function

# import necessary modules
import datetime
import pypyodbc
import os
import re
import gzip

if __name__ == "__main__":
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
    print(
        'match_reason\taddress_row_id\tpmi_id\tinput_address\tfinal_streetnumber\tfinal_streetname\tfinal_streettype\tfinal_suburb\tfinal_town\tfinal_postcode\tscore\tfinal_single_address',
        file=outfile)

    duds_outfile = open(dud_addresses_filename, "a")
    print('match_reason\taddress_row_id\tpmi_id\tinput_address', file=duds_outfile)

    # _____________________________________________________________________

    # create list of street types
    street_types_filename = "street_types.txt"
    street_types = []
    street_types_file = open(street_types_filename, 'r')
    for line in street_types_file:
        line = line.upper()
        line = line.strip()
        if line not in street_types:
            street_types.append(line)
    street_types_file.close()

    # ------------------------------------------------------------------
    # create reference dictionaries

    address_dict = {}
    dict_filename1 = "street_name_dict.txt"
    dict_filename2 = "HERE_StreetNameSuburbDictionary.txt"

    dict_file = open(dict_filename1)
    lines = dict_file.readlines()
    print(len(lines), " lines in address dict 1")

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
            if dict_postcode not in address_dict:
                address_dict[dict_postcode] = []
            address_dict[dict_postcode].append(dict_list)
    dict_file.close()

    dict_file = open(dict_filename2)
    lines = dict_file.readlines()
    print(len(lines), " lines in address dict 2")

    for line in lines[1:]:
        line = line.upper()
        line = line.strip()
        line = line.split('\t')
        # print('line',line)
        dict_street_name = line[0]
        dict_street_name = dict_street_name.strip()
        dict_street_type = line[1]
        dict_street_type = dict_street_type.strip()
        ##    if dict_street_type not in street_types:
        ##        street_types.append(dict_street_type)
        dict_suburb = line[2]
        dict_suburb = dict_suburb.strip()
        dict_town = line[3]
        dict_town = dict_town.strip()
        dict_municipality = line[4]
        dict_municipality = dict_municipality.strip()
        dict_list = [dict_street_name, dict_street_type, dict_suburb, dict_town, dict_municipality]
        if dict_suburb != '':
            if dict_suburb not in address_dict:
                address_dict[dict_suburb] = []
            address_dict[dict_suburb].append(dict_list)
        if dict_town != '':
            if dict_town not in address_dict:
                address_dict[dict_town] = []
            address_dict[dict_town].append(dict_list)

    dict_file.close()

    # _______________________________________________________________________
    # make a list of lists for  all addresses pulled in -
    # connect to mssql server pypyodbc and pull in actual addresses

    pmi_addresses = []

    # max address_row_id for 26/10/2016 is 524751803
    # min address_row_id for 26/10/2016 is 505468273

    connection_string = "DSN=biod01_patient"
    connection = pypyodbc.connect(connection_string)
    SQL = """SELECT DISTINCT [address_row_id]
          ,[pmi_id]
          ,[AddressLine1]
          ,[AddressLine2]
          ,[AddressLine3]
          ,[AddressLine4]
          ,[postal_code]
          ,[province]
          FROM [Patient].[dbo].[pmi_address]
          where convert (date, date_added_to_table) = (SELECT CONVERT (date, SYSDATETIME()));"""

    cursor = connection.cursor()
    cursor.execute(SQL)
    n = 0
    row = cursor.fetchone()
    while row is not None:
        # print('1:',row)
        address_row_id = row[0]

        if address_row_id in already_processed:
            print('already processed', address_row_id)
        else:
            row_id = row[0]
            pmi_id = row[1]
            pmi_postcode = row[6]
            if pmi_postcode is not None:
                pmi_postcode = pmi_postcode.strip()
            pmi_address_string_all = str(row[2]) + ' ' + str(row[3]) + ' ' + str(row[4]) + ' ' + str(row[5])
            # print('as pulled from database, pmi_address_string_all is', pmi_address_string_all)
            pmi_street_type = ''
            for street_type in street_types:
                if street_type in pmi_address_string_all:
                    # print(street_type, 'in ', pmi_address_string)
                    pmi_street_type = street_type
                    pmi_address_string = pmi_address_string_all.replace(street_type, " ")
                    break
                    # print('after RE removed this is pmi_address_string', pmi_address_string)
                else:
                    pmi_address_string = pmi_address_string_all
            pmi_address_string = pmi_address_string.upper()
            pmi_address_words = pmi_address_string.split(" ")
            # print('after processing',pmi_address_string)

            re_no = re.compile(
                '(STR\. *\d+ *\D\s)|(STR\. *\d+\s)|(\d+-\d+)|(^\D\.\d+)|(\s\D\d+)|(^\D-\d+)|(\s\D-\d+)|(\d+\s\D\s)|(^\D\d+)|(^\D\s\d+)|(\s\d+\D\s)|(\s\d+\s\D\s)|(^\d+\s\D\s)|(^\d+\D\s)|(\s\d+\s)|(^\d+ )')
            found_numbers = re_no.search(pmi_address_string)
            if found_numbers is not None:
                pmi_street_number = found_numbers.group()
                pmi_street_number = pmi_street_number.strip()
                pmi_street_number = pmi_street_number.strip("NO")
                # print(pmi_street_number)
            else:
                pmi_street_number = ""

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
        #    print(pmi_address)
        address_row_id = pmi_address[0]
        pmi_id = pmi_address[1]
        pmi_street_number = pmi_address[2]
        pmi_street_type = pmi_address[3]
        pmi_address_string_all = pmi_address[4]
        pmi_address_string = pmi_address[5]
        pmi_address_words = pmi_address[6]
        len_address_words = len(pmi_address_words)
        pmi_postcode = pmi_address[7]
        # print(pmi_address_string_all)

        if address_row_id not in clean_scored_addresses:
            # print('STORED STRING: no_match\t'+ str(address_row_id)+ '\t' + str(pmi_id) + '\t' + pmi_address_string_all)
            clean_scored_addresses[address_row_id] = [0, 'no_match\t' + str(address_row_id) + '\t' + str(
                pmi_id) + '\t' + pmi_address_string_all]

        for key in address_dict:
            # postcode match
            if key == pmi_postcode:
                #            print('postcode match')
                dict_records = address_dict[key]
                for dict_record in dict_records:
                    score = 2
                    final_streetnumber = ''
                    final_streetname = ''
                    final_street_type = ''
                    final_suburb = ''
                    final_town = ''
                    final_postcode = ''
                    dict_streetname = dict_record[0]
                    dict_suburb = dict_record[2]
                    dict_town = dict_record[3]
                    if dict_streetname in pmi_address_words[:3]:
                        #                    print('\tstreetname match')
                        final_streetnumber = pmi_street_number
                        final_streetname = dict_streetname
                        final_street_type = pmi_street_type
                        final_suburb = dict_suburb
                        final_town = dict_town
                        final_postcode = key
                        score = score + 1
                        if final_suburb in pmi_address_words[len_address_words - 3:]:
                            #                        print('\tsuburb match')
                            score = score + 1
                        if final_town in pmi_address_words[len_address_words - 3:]:
                            #                        print('\ttown match')
                            score = score + 1
                        # postcode match, street match
                        # print(clean_scored_addresses[address_row_id])
                        if score > clean_scored_addresses[address_row_id][0]:
                            clean_scored_addresses[address_row_id] = [score, 'postcode_match\t' + str(
                                address_row_id) + "\t" + str(pmi_id) + "\t" + pmi_address_string_all \
                                                                      + "\t" + final_streetnumber + "\t" + final_streetname + "\t" + final_street_type + "\t" + final_suburb + "\t" + \
                                                                      final_town + "\t" + str(
                                final_postcode) + "\t" + str(score) + "\t" + \
                                                                      final_streetnumber + " " + final_streetname + " " + final_suburb + " " + final_town + " " + str(
                                final_postcode)]

            # suburb or town name match one word
            if key != pmi_postcode and key in pmi_address_words[len_address_words - 4: len_address_words]:
                dict_records = address_dict[key]
                #            print('suburb match')

                # print('key is', key, 'and pmi_address_words are', pmi_address_words)
                for dict_record in dict_records:
                    score = 1
                    final_streetnumber = ''
                    final_streetname = ''
                    final_street_type = ''
                    final_suburb = ''
                    final_town = ''
                    final_postcode = ''
                    dict_streetname = dict_record[0]
                    dict_suburb = dict_record[2]
                    dict_town = dict_record[3]
                    if dict_streetname in pmi_address_words[:3]:
                        score = score + 1
                        #                    print('\tstreetname_match')
                        final_streetnumber = pmi_street_number
                        final_streetname = dict_streetname
                        final_street_type = pmi_street_type
                        final_suburb = dict_suburb
                        final_town = dict_town
                        final_postcode = ''
                        if final_suburb in pmi_address_words[len_address_words - 3:]:
                            score = score + 1
                        if final_town in pmi_address_words[len_address_words - 3:]:
                            score = score + 1
                        # postcode match, street match.
                        if score > clean_scored_addresses[address_row_id][0]:
                            clean_scored_addresses[address_row_id] = [score, 'suburb_or_town_words_match\t' + str(
                                address_row_id) + "\t" + str(pmi_id) + "\t" + pmi_address_string_all + "\t" + \
                                                                      final_streetnumber + "\t" + final_streetname + "\t" + final_street_type + "\t" + final_suburb + "\t" + final_town + "\t" + str(
                                final_postcode) + "\t" + str(score)
                                                                      + "\t" + final_streetnumber + " " + final_streetname + " " + final_suburb + " " + final_town + " " + str(
                                final_postcode)]
                            # suburb or town name match string
            if key != pmi_postcode and key not in pmi_address_words[:3] and key in pmi_address_string:
                dict_records = address_dict[key]
                for dict_record in dict_records:
                    score = 0
                    final_streetnumber = ''
                    final_streetname = ''
                    final_street_type = ''
                    final_suburb = ''
                    final_town = ''
                    final_postcode = ''
                    dict_streetname = dict_record[0]
                    dict_suburb = dict_record[2]
                    dict_town = dict_record[3]
                    if dict_streetname in pmi_address_string:
                        score = score + 0.5
                        final_streetnumber = pmi_street_number
                        final_streetname = dict_streetname
                        final_street_type = pmi_street_type
                        final_suburb = dict_suburb
                        final_town = dict_town
                        final_postcode = ''
                        if final_suburb in pmi_address_words[len_address_words - 3:]:
                            score = score + 1
                        if final_town in pmi_address_words[len_address_words - 3:]:
                            score = score + 1
                        # postcode match, street match.
                        if score > clean_scored_addresses[address_row_id][0]:
                            clean_scored_addresses[address_row_id] = [score, 'suburb_or_town_string_match\t' + str(
                                address_row_id) + "\t" + str(pmi_id) + "\t" + pmi_address_string_all + "\t" + \
                                                                      final_streetnumber + "\t" + final_streetname + "\t" + final_street_type + "\t" + final_suburb + "\t" + final_town + "\t" + str(
                                final_postcode) + "\t" + str(score) \
                                                                      + "\t" + final_streetnumber + " " + final_streetname + " " + final_suburb + " " + final_town + " " + str(
                                final_postcode)]

    for address_row_id in clean_scored_addresses:

        score = float(clean_scored_addresses[address_row_id][0])
        print_string = clean_scored_addresses[address_row_id][1]
        # print(score)
        if score == 0:
            print(print_string, file=duds_outfile)
        if score > 1:
            print(print_string, file=outfile)

    outfile.close()
    outfile = open(outfile_name, "r")

    addresses = outfile.readlines()
    for final_address in addresses:
        final_address = final_address.split('\t')
    #    geocode_address = final_address[]
    #    print(final_address)

    # TIDY UP
    cursor.close()
    connection.close()
    scrub_time = datetime.datetime.now()
    outfile.close()
    duds_outfile.close()
    # address_file.close()
    print("Scrubbing complete, took ", scrub_time - start_time, " to do ", n, " rows.")

    # ________________________________________________________________________

    #