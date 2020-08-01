#!/usr/bin/env python

from __future__ import print_function, division
import argparse
import csv
from functools import reduce
import json
from operator import and_
import re
import sys

from afrigis_to_tree import afrigis_to_tree

# find a town
# find suburbs within that town
# then look for suburb
# exclude all suburbs that are also towns
# if starting with suburb - look for postcode to tie break
# look in address for possible misspellings of words known to be associated with postcode


class Counter:
    def __init__(self):
        self.counts = {}

    def add(self, thing):
        self.counts[thing] = self.counts.get(thing, 0) + 1

    def most_common(self, n=0):
        items = sorted(self.counts.keys(), key=lambda x: self.counts[x], reverse=True)
        if n == 0:
            return [(item, self.counts[item]) for item in items]
        else:
            return [(item, self.counts[item]) for item in items[:n]]

    def __len__(self):
        return len(self.counts)

    def __repr__(self):
        return (
            "Counter("
            + ", ".join("(%s: %s)" % (t[0], t[1]) for t in self.most_common())
            + ")"
        )


class AfriGISData:
    def __init__(self, filename):
        self.suburbs = set()
        self.towns = set()
        self.town_to_suburb = {}
        self.suburb_to_town = {}
        self.duplicate_suburbs = {}
        self.suburb_to_id = {}
        self.suburb_to_sub_cde = {}
        self.suburbs_in_town = {}
        self.suburb_to_postcode = {}
        suburb_names = set()
        suburbs_that_are_towns = []
        for row in csv.DictReader(open(filename), delimiter="\t"):
            # if ' ' in row['SUBURB']:
            #     suburb_names.add(row['SUBURB'].upper())
            # if ' ' in row['TOWN']:
            #     suburb_names.add(row['TOWN'].upper())
            suburb = row["SUBURB"].strip().upper().replace(" ", "-")
            town = row["TOWN"].strip().upper().replace(" ", "-")
            ag_id = row["AG_SUB_ID"]
            ag_sub_cde = row["AG_SUB_CDE"]
            postcode = row["STRCODE"] if row["STRCODE"].strip() != "" else None
            if suburb == town:
                suburbs_that_are_towns.append(suburb)
                continue
            if suburb in self.suburbs:
                self.duplicate_suburbs[suburb] = self.duplicate_suburbs.get(
                    suburb, [suburb, self.suburb_to_town[suburb]]
                ) + [town]
            self.suburbs.add(suburb)
            self.towns.add(town)
            self.town_to_suburb[town] = suburb
            self.suburb_to_town[suburb] = town
            self.suburb_to_id[suburb] = ag_id
            self.suburb_to_sub_cde[suburb] = ag_sub_cde
            suburbs_in_town = self.suburbs_in_town.get(town, set())
            suburbs_in_town.add(suburb)
            self.suburbs_in_town[town] = suburbs_in_town
            self.suburb_to_postcode[suburb] = postcode

        # for suburb in suburbs_that_are_towns:
        #     if suburb not in self.towns:
        #         print(suburb)


def remove_comma_etc(mystring):
    return mystring.replace(",", "").replace('"', "").replace(".", "").replace("'", "")


def match_it(
    address_filename,
    output_filename,
    problem_output_filename,
    afrigis_filename,
    data_json_filename,
    suburb_names_filename,
    street_types_filename,
    synonyms_filename,
    excluded_places_filename,
    row_wanted=None,
):
    fieldnames = None
    with open(address_filename) as input_file:
        line = next(input_file)
        fields = line.strip().split("\t")
        missing_fields = []
        default_fieldnames = [
            "address_row_id",
            "AddressLine1",
            "AddressLine2",
            "AddressLine3",
            "AddressLine4",
            "postal_code",
        ]
        for fieldname in default_fieldnames:
            if fieldname not in fields:
                missing_fields.append(fieldname)
        if len(missing_fields) > 0:
            print(
                "WARNING: fields missing from header line: %s. Line was:\n%s"
                % (" ".join(missing_fields), line),
                file=sys.stderr,
            )
            fieldnames = default_fieldnames

    address_synonyms = dict(
        [(r[0].strip(), r[1].strip()) for r in csv.reader(open(synonyms_filename))]
    )

    afrigis = AfriGISData(afrigis_filename)

    excluded_places = [
        (r[0].strip(), r[1].strip()) for r in csv.reader(open(excluded_places_filename))
    ]
    afrigis_tree = afrigis_to_tree(
        open(afrigis_filename), transform=True, exclude=excluded_places
    )
    cape_town_node = afrigis_tree.find_node_by_name("CAPE-TOWN")
    assert len(cape_town_node) == 1
    cape_town_node = cape_town_node[0]

    data = json.load(open(data_json_filename))
    term_to_postcode = data["term_to_postcode"]
    postcode_to_suburb = data["postcode_to_suburb"]
    postcode_to_town = data["postcode_to_town"]

    # start with suburbs and town names known togrep  afrigis
    suburb_names = set(
        [name.strip().replace("-", " ") for name in (afrigis.suburbs | afrigis.towns)]
    )
    with open(suburb_names_filename) as input_file:
        for line in input_file:
            line = line.upper().strip("\n")
            name = remove_comma_etc(line)
            suburb_names.add(name)

    suburb_names_with_spaces = [
        suburb_name.strip() for suburb_name in suburb_names if " " in suburb_name
    ]

    street_types = set()
    with open(street_types_filename) as input_file:
        for line in input_file:
            line = line.upper().strip("\n")
            if line != "" and line not in street_types:
                street_types.add(line)
    street_name_re = re.compile(
        r"\w+\s+(%s)\W"
        % (
            "|".join(
                [t.strip().upper() for t in sorted(street_types, key=len, reverse=True)]
            )
        )
    )

    terms_with_dashes = [
        term for term in data["most_common_terms_all_postcodes"] if "-" in term
    ]

    if fieldnames is not None:
        reader = csv.DictReader(
            open(address_filename), delimiter="\t", fieldnames=fieldnames
        )
        next(reader)  # discard first line
    else:
        reader = csv.DictReader(open(address_filename), delimiter="\t")

    postal_code_re = re.compile(r"\d{4}")
    postal_code_to_address = {}
    pmi_addresses = []
    # re_no = re.compile(r'(STR\. *\d+ *\D\s)|(STR\. *\d+\s)|(\d+-\d+)|(^\D\.\d+)|(\s\D\d+)|(^\D-\d+)|(\s\D-\d+)|(\d+\s\D\s)|(^\D\d+)|(^\D\s\d+)|(\s\d+\D\s)|(\s\d+\s\D\s)|(^\d+\s\D\s)|(^\d+\D\s)|(\s\d+\s)|(^\d+ )')
    address_row_ids_seen = set()
    count = 0
    no_postcode = 0
    input_fieldnames = [fieldname for fieldname in default_fieldnames if fieldname in reader.fieldnames]
    extra_fieldnames = [
            "suburb",
            "town",
            "ag_sub_id",
            "ag_sub_cde",
            "afrigis_match",
            "ambiguous_match",
            "probably_in_ct",
            "postcode_resolved",
            "inconsistent_postcode",
            "supporting_terms",
            "postcodes",
            "ambiguous_terms",
    ]
    writer = csv.DictWriter(
        open(output_filename, "w"),
        fieldnames=input_fieldnames + extra_fieldnames,
        delimiter="\t",
    )
    writer.writeheader()

    problem_writer = csv.DictWriter(
        open(problem_output_filename, "w"),
        fieldnames=input_fieldnames + extra_fieldnames,
        delimiter="\t"
    )
    problem_writer.writeheader()

    matches_term = 0
    for (i, row) in enumerate(reader):
        if row_wanted and i != (row_wanted - 2):
            continue
        output_row = {}
        for fieldname in input_fieldnames:
            output_row[fieldname] = row[fieldname]
        address_row_id = row["address_row_id"]
        pmi_postcode = row["postal_code"]
        address1 = row["AddressLine1"]
        address2 = row["AddressLine2"]
        address3 = row["AddressLine3"]
        address4 = row["AddressLine4"]
        if address_row_id in address_row_ids_seen:
            continue
        address_row_ids_seen.add(address_row_id)
        if pmi_postcode is None:
            pmi_postcode = ""
            no_postcode += 1
        else:
            pmi_postcode = pmi_postcode.strip()

        pmi_address_string_all = " ".join([address1, address2, address3, address4])
        if pmi_postcode == "":
            postcode_match = postal_code_re.search(pmi_address_string_all)
            if postcode_match is not None:
                pmi_postcode = postcode_match.group()

        pmi_address_string_all = (
            pmi_address_string_all.strip()
            .upper()
            .replace(",", " ")
            .replace("NONE", "")
            .replace("NULL", "")
            .replace('"', "")
            .replace(".", "")
            .replace("'", "")
        )
        # seen_brown = False
        # if 'BROWN' in pmi_address_string_all:
        #     print(pmi_address_string_all)
        #     seen_brown = True
        for term in sorted(address_synonyms, key=len, reverse=True):
            # if seen_brown and 'BROWN' in term:
            #     print('T:', term, term in pmi_address_string_all)
            if term in pmi_address_string_all:
                pmi_address_string_all = pmi_address_string_all.replace(
                    term, address_synonyms[term]
                )
                # print("R:", pmi_address_string_all)

        # capture common area names with a number
        # NOTE: this is not used at present in the "training" code
        # because these names (like "PHASE 2") turned out to be too generic
        # but it is retained here because this might be useful info in
        # understanding an address
        pmi_address_string_all = re.sub(
            r"((?P<name>SITE|SECTION|PHASE|ZONE|EXT)\s+(?P<num>\d+))",
            r"\g<name>-\g<num>",
            pmi_address_string_all,
        )
        # squash the spaces to a single space
        pmi_address_string_all = re.sub(r"\s+", " ", pmi_address_string_all)
        # print(pmi_address_string  _all)
        pmi_address_string_all = street_name_re.sub("", pmi_address_string_all)
        # print(pmi_address_string_all)

        # print(pmi_address_string_all)
        for term in [t for t in terms_with_dashes if t in pmi_address_string_all]:
            term_space = term.replace("-", " ")
            pmi_address_string_all = pmi_address_string_all.replace(term_space, term)

        for name in [
            name.strip()
            for name in suburb_names_with_spaces
            if name in pmi_address_string_all
        ]:
            name_dash = name.replace(" ", "-")
            pmi_address_string_all = pmi_address_string_all.replace(name, name_dash)
        # output_row["raw"] = pmi_address_string_all
        pmi_address_words = [
            word
            for word in pmi_address_string_all.split()
            if not re.match(r"\d+", word)
        ]
        # numbers_match = re_no.search(pmi_address_string_all)
        # if numbers_match is not None:
        #     pmi_street_number = numbers_match.group()
        #     pmi_street_number = pmi_street_number.strip().strip('NO')
        #     pmi_address_string = pmi_address_string.replace(pmi_street_number, '')
        # else:
        #     pmi_street_number = ''

        votes = Counter()
        match = False
        match_count = 0
        match_terms = set()
        afrigis_match = False
        afrigis_terms = set()
        postcode_resolved = True
        ambiguous_afrigis_match = False
        ambiguous_afrigis_terms = set()
        postcodes_seen = set()
        for word in pmi_address_words:
            # TODO: deal with contractiory addresses like RAVENSMEAD, BELHAR
            # these should be seen as similar to ambiguous addresses
            if word in data["most_common_terms_all_postcodes"]:
                postcode = data["term_to_postcode"].get(word)
                if postcode is not None:
                    postcodes_seen.add(postcode)
                afrigis_nodes = afrigis_tree.find_node_by_name(word)
                if len(afrigis_nodes) > 0:
                    afrigis_match = True
                    if len(afrigis_nodes) > 1:
                        ambiguous_afrigis_match = True
                        ambiguous_afrigis_terms.add(word)
                    else:
                        afrigis_terms.add(word)
                match = True
                match_terms.add(word)
                match_count += 1
            if word in afrigis.towns:
                pass

        if match:
            matches_term += 1
            probably_in_ct = False
            ct_part_of_town = None
            ct_suburb = None
            ct_sub_id = None
            ct_sub_cde = None
            postcode_resolved = False
            node_by_postcode = None
            if pmi_postcode != "" and pmi_postcode not in postcodes_seen:
                inconsistent_postcode = True
                output_row["inconsistent_postcode"] = "Yes"
            else:
                inconsistent_postcode = False
                output_row["inconsistent_postcode"] = "No"

            if ambiguous_afrigis_match:
                output_row["postcode_resolved"] = "No"
                if pmi_postcode != "" and pmi_postcode in data["postcode_to_suburb"]:
                    # if we found a postcode try and use this
                    # to associate this ambiguous term with a suburb
                    terms_for_postcode = set(
                        data["postcode_to_suburb"].get(pmi_postcode)
                    )
                    for term in ambiguous_afrigis_terms:
                        if term in terms_for_postcode:
                            nodes = afrigis_tree.find_node_by_name(term)
                            for node in nodes:
                                # only use postcode to resolve suburbs
                                if not node.is_town and node.postcode == pmi_postcode:
                                    output_row["postcode_resolved"] = "No"
                                    postcode_resolved = True
                                    node_by_postcode = node
                                    break
                elif "CAPE-TOWN" in pmi_address_words:
                    probably_in_ct = True
                    for word in ambiguous_afrigis_terms:
                        # look at each word and see if it matches a place in CT
                        for node in afrigis_tree.find_node_by_name(word):
                            node_in_ct = afrigis_tree.is_ancestor(cape_town_node, node)
                            # print(node_in_ct, node.name, cape_town_node.name)
                            if node_in_ct:
                                # ok at least one version of this term is a Cape Town area
                                # so we take the parent (i.e. "town") of that node as
                                # the town to use.
                                # WARNING: this does not deal with contradictions
                                # e.g. if an address has two place names that are in
                                # Cape Town but different parts of Cape Town
                                ct_part_of_town = node.parent.name
                                ct_suburb = node.name
                                ct_sub_id = node.ag_sub_id
                                ct_sub_cde = node.ag_sub_cde
                                break
                        else:
                            # got to end of loop and none of the versions of this term
                            # are in Cape Town
                            probably_in_ct = False
                            break

            output_row["supporting_terms"] = ", ".join(match_terms)
            output_row["postcodes"] = ", ".join(postcodes_seen)
            if not afrigis_match:
                output_row["afrigis_match"] = "No"
                if pmi_postcode != "" and pmi_postcode in data["postcode_to_suburb"]:
                    output_row["postcodes"] = pmi_postcode
                    output_row["supporting_terms"] = data["postcode_to_suburb"]
            else:
                output_row["afrigis_match"] = "Yes"
                if ambiguous_afrigis_match:
                    output_row["ambiguous_match"] = "Yes"
                    if postcode_resolved:
                        output_row["town"] = node_by_postcode.parent.name
                        output_row["suburb"] = node_by_postcode.name
                        output_row["ag_sub_id"] = node.ag_sub_id
                        output_row["ag_sub_cde"] = node.ag_sub_cde
                    if probably_in_ct:
                        output_row["probably_in_ct"] = "Yes"
                        output_row["town"] = ct_part_of_town
                        output_row["suburb"] = ct_suburb
                        output_row["ag_sub_id"] = ct_sub_id
                        output_row["ag_sub_cde"] = ct_sub_cde
                    else:
                        output_row["probably_in_ct"] = "No"
                        for word in ambiguous_afrigis_terms:
                            output_row["ambiguous_terms"] = "|".join(
                                ",".join((node.name, node.parent.name))
                                for node in afrigis_tree.find_node_by_name(word)
                            )
                else:
                    output_row["ambiguous_match"] = "No"
                    term = list(afrigis_terms)[0]
                    nodes = afrigis_tree.find_node_by_name(term)
                    assert len(nodes) == 1
                    node = nodes[0]
                    if node.is_town:
                        town = node.name
                        if node.ag_sub_id is not None:
                            # this only happens when a name is both a town and a suburb
                            suburb = node.name
                        else:
                            suburb = ""
                        sub_id = node.ag_sub_id if node.ag_sub_id is not None else ""
                        sub_cde = node.ag_sub_cde if node.ag_sub_cde is not None else ""
                    else:
                        town = node.parent.name
                        suburb = node.name
                        sub_id = node.ag_sub_id
                        sub_cde = node.ag_sub_cde
                    output_row["town"] = town
                    output_row["suburb"] = suburb
                    output_row["ag_sub_id"] = sub_id
                    output_row["ag_sub_cde"] = sub_cde

            # split output into "clean match" output and problem output
            if afrigis_match and not ambiguous_afrigis_match:
                writer.writerow(output_row)
            else:
                problem_writer.writerow(output_row)
            # for term in match_terms:
            #     print(
            #     match_count,
            #     afrigis_match,
            #     ambiguous_afrigis_match,
            #     probably_in_ct,
            #     postcodes_seen,
            #     match_terms,
            #     pmi_address_string_all,
            # )
        else:
            print("UNKNOWN", pmi_address_words)

        # choose only the word in the address that has the most matches against a data source
        # best_match = -1
        # match = None
        # for (word, count) in votes.most_common():
        #     output = find_best_match(
        #         word,
        #         pmi_address_words,
        #         pmi_postcode,
        #         afrigis,
        #         term_to_postcode,
        #         postcode_to_suburb,
        #         postcode_to_town,
        #     )
        #     if "score" in output and output["score"] > best_match:
        #         best_match = output["score"]
        #         match = output
    print(matches_term)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--row", type=int, help="Only process this row")
    parser.add_argument(
        "--output_filename",
        help="Name of file to write output to",
        default="annotated.tsv",
    )
    parser.add_argument(
        "--problem_output_filename",
        help="Name of fle to write output where there are problems (e.g. ambiguous resolution) to",
        default="problem_annotated.tsv"
    )
    parser.add_argument(
        "--afrigis_filename",
        default="AfriGIS_Suburbs_Towns_List.csv",
        help="AfriGIS towns and suburbs filename",
    )
    parser.add_argument(
        "--data_json_filename",
        default="data.json",
        help="File containing prediction data (produced by addresses_to_clouds.py)",
    )
    parser.add_argument(
        "--suburb_names_filename",
        default="all_suburbs_words.txt",
        help="File containing words commonly associated with suburbs",
    )
    parser.add_argument(
        "--street_types_filename",
        default="street_types.txt",
        help="File containing words typically associated with street names",
    )
    parser.add_argument(
        "--synonyms_filename",
        default="synonyms.csv",
        help="File containing synonyms to replace in addresses",
    )
    parser.add_argument(
        "--excluded_places_filename",
        default="excluded_places.csv",
        help="File containing place names (suburb, town) to exclude",
    )
    parser.add_argument("address_filename")
    args = parser.parse_args()
    match_it(
        args.address_filename,
        args.output_filename,
        args.problem_output_filename,
        args.afrigis_filename,
        args.data_json_filename,
        args.suburb_names_filename,
        args.street_types_filename,
        args.synonyms_filename,
        args.excluded_places_filename,
        args.row,
    )
