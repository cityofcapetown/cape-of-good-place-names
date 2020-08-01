#!/usr/bin/env python

from __future__ import print_function
import argparse
import csv
from itertools import combinations
import json
import re


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


def remove_comma_etc(mystring):
    return mystring.replace(",", "").replace('"', "").replace(".", "").replace("'", "")


# @profile
def make_clouds(address_filename, common_term_cutoff=3):

    afrigis_filename = "AfriGIS_Suburbs_Towns_List.csv"
    afrigis_suburbs = set()
    afrigis_towns = set()
    afrigis_town_to_suburb = {}
    afrigis_suburb_to_town = {}
    suburb_names = set()
    for row in csv.DictReader(open(afrigis_filename), delimiter="\t"):
        if " " in row["SUBURB"]:
            suburb_names.add(row["SUBURB"].upper())
        if " " in row["TOWN"]:
            suburb_names.add(row["TOWN"].upper())
        suburb = row["SUBURB"].strip().upper().replace(" ", "-")
        town = row["TOWN"].strip().upper().replace(" ", "-")
        afrigis_suburbs.add(suburb)
        afrigis_towns.add(town)
        afrigis_town_to_suburb[town] = suburb
        afrigis_suburb_to_town[suburb] = town

    street_types = set()
    street_types_filename = "street_types.txt"
    with open(street_types_filename) as input_file:
        for line in input_file:
            line = line.upper().strip("\n")
            if line != "" and line not in street_types:
                street_types.add(line)

    suburb_names_filename = "all_suburbs_words.txt"
    with open(suburb_names_filename) as input_file:
        for line in input_file:
            line = line.upper().strip("\n")
            name = remove_comma_etc(line)
            suburb_names.add(name)

    suburb_names_with_spaces = [ s.strip() for s in list(suburb_names) if ' ' in s ]
    sinjani_suburbs = set()
    sinjani_filename = "sinjani_suburbs.txt"
    with open(sinjani_filename) as input_file:
        for line in input_file:
            line.upper().strip()
            ref_sub = remove_comma_etc(line)
            (ref_sub_sub, ref_sub_main) = ref_sub.split("\t")
            ref_sub_sub = ref_sub_sub.strip().replace(" ", "-")
            ref_sub_main = ref_sub_main.strip().replace(" ", "-")
            ref_sub_pair = (ref_sub_main, ref_sub_sub)
            if ref_sub_pair not in sinjani_suburbs:
                sinjani_suburbs.add(ref_sub_pair)

    reader = csv.DictReader(open(address_filename), delimiter="\t")

    address_synonyms = dict([ l.strip().split(', ') for l in open('synonyms.csv')])

    tok_pair_counter = Counter()
    postal_code_to_address = {}
    pmi_addresses = []
    re_no = re.compile(
        r"(STR\. *\d+ *\D\s)|(STR\. *\d+\s)|(\d+-\d+)|(^\D\.\d+)|(\s\D\d+)|(^\D-\d+)|(\s\D-\d+)|(\d+\s\D\s)|(^\D\d+)|(^\D\s\d+)|(\s\d+\D\s)|(\s\d+\s\D\s)|(^\d+\s\D\s)|(^\d+\D\s)|(\s\d+\s)|(^\d+ )"
    )
    street_name_re = re.compile(
        r"\w+\s+(%s)\W" % ("|".join([t.strip().upper() for t in street_types]))
    )
    street_type_re = re.compile(r"\W({})\W".format("|".join([t.strip().upper() for t in street_types])))
    address_row_ids_seen = set()
    count = 0
    no_postcode = 0
    for row in reader:
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
        pmi_address_string_all = (
            pmi_address_string_all.strip()
            .upper()
            .replace(",", "")
            .replace("NONE", "")
            .replace("NULL", "")
        )
        # capture common area names with a number.
        # commented out because in practice it seems too generic
        # pmi_address_string_all = re.sub(
        #     r"((?P<name>SITE|SECTION|PHASE|ZONE|EXT)\s+(?P<num>\d+))",
        #     r"\g<name>-\g<num>",
        #     pmi_address_string_all,
        # )
        # squash the spaces to a single space
        for term in address_synonyms:
            if term in pmi_address_string_all:
                pmi_address_string_all = pmi_address_string_all.replace(term, address_synonyms[term])
        pmi_address_string_all = re.sub(r"\s+", " ", pmi_address_string_all)
        pmi_address_string_all = street_name_re.sub("", pmi_address_string_all)
        # pmi_address_string_all = re.sub(r'(?P<name>\w+\s+(EST|ESTATE))', r'\g<name>-ESTATE', pmi_address_string_all)
        pmi_address_string_all = re.sub(r"(EST|ESTATE)", "", pmi_address_string_all)
        pmi_street_type = ""

        # NOTE: This section commented out because it was finding bogus
        # substring matches.

        # street_types is sorted from longest to shortest first to ensure that
        # 'STR' is not removed leaving 'EET' behind
        # print(pmi_address_string_all)

        # for street_type in sorted(street_types, key=lambda x: len(x), reverse=True):
        #     if street_type in pmi_address_string_all:
        #         print("matched", street_type)
        #         pmi_address_string = pmi_address_string_all.replace(street_type, " ")
        #         break
        # else:
        #     # yes you can use else on a loop - it runs if the break doesn't run
        #     pmi_address_string = pmi_address_string_all
        pmi_address_string = pmi_address_string_all

        # print(pmi_address_string_all)
        pmi_address_words = pmi_address_string.split()
        numbers_match = re_no.search(pmi_address_string)
        if numbers_match is not None:
            pmi_street_number = numbers_match.group()
            pmi_street_number = pmi_street_number.strip().strip("NO")
            pmi_address_string = pmi_address_string.replace(pmi_street_number, "")
        else:
            pmi_street_number = ""

        pmi_address_string = re.sub(r"\s+", " ", pmi_address_string)
        pmi_id = "FAKEID"  # just to deal with the fact that my data doesn't have pmi_id
        count += 1
        postal_code_to_address[pmi_postcode] = postal_code_to_address.get(
            pmi_postcode, []
        ) + [pmi_address_string]
        # print(postal_code_to_address[pmi_postcode])
        pmi_addresses.append(
            [
                address_row_id,
                pmi_id,
                pmi_street_number,
                pmi_street_type,
                pmi_address_string_all,
                pmi_address_string,
                pmi_address_words,
                pmi_postcode,
            ]
        )

    # count how many times we don't see a postcode in the data
    print("No postcode:", no_postcode)
    excluded_words = [
        r"H/V",
        "BOX",
        "PRIVATE",
        "BAG",
        "COURT",
        "PARK",
        r"C/O",
        r"P/A",
        "CITY",
        r"W/S",
        r"S/CAMP",
        "MNR",
        "AND",
        "POSBUS",
        "ROOM",
        r"P/SAK",
        "PRIVAATSAK",
        "UNKNOWN",
        "2ND",
        "3RD",
        "4TH",
        "5TH",
        "6TH",
        "7TH",
        "8TH",
        "9TH",
        "FLAT",
        "UNIT",
        "SIR",
        "PRINCE",
        "PRINCESS",
        "NEW",
        "GLEN",
        "UIT",
        "HILL",
        "VILLAGE",
        "HOTEL",
        "SUN",
        "BEACH",
        "UPPER",
        "LOWER",
        "HEIGHTS",
        "RIDGE",
        "GRAND",
        "OFFICE",
        "CAPE",
        "THE",
        "HANS",
        "FLATS",
        "BAY",
        "MAIN",
        "SITE",  # from SITE to PHASE these are "generic names" are often ambiguous
        "SECTION",
        "PHASE",
        "ZONE",
        "EXT",
        "PHASE",
        "ONE",
        "TWO",
        "THREE",
        "FOUR",
        "FIVE",
        "SIX",
        "SEVEN",
        "EIGHT",
        "NINE",
        "LOC",
        "BLOCK",
        "CHARLES", # the following from noticing spurious words creeping into term list
        "OAKS",
        "MILITARY",
        "HOSPITAL",
        "VIA",
        "EDWARD",
        "ZONE-1",  # part of Langa but could cause confusion
        "ZONE-3",
        "ZONE-4",
        "ZONE-5",
        "ZONE6",
        "ZONE-6",
        "ZONE-7",
        "ZONE-8",
        "ZONE9",
        "ZONE-9",
        "ZONE09",
        "ZONE-10",
        "SITE-5", # ambiguous term - applies to both Dunoon and Masiphumelele
        "HOSTEL",
        "PELICAN",
        "TOWN",  # typically orphan bit of TOWN TWO, KHAYELITSA
        "CRESENT",
        "NEPTUNE",
        "CASTLE",
        "DURA",
        "EVERITE",
        "EXT4", # part of Mfuleni but again ambiguous
        "EXT6",
        "EXT8",
        "EXT12",
        "EXT-13",
        "PHASE3",
        "PHASE-9",
        "MARTHINUS",
        "SCHALKWYK",
        "WINNIE",
        "MANDELA",
        "HILLSIDE",
        "PROTEA",
        "",
    ]
    excluded_words.extend([street_type.strip() for street_type in street_types])
    excluded_words = set(excluded_words)

    afrikaans_street_endings = ["STRAAT", "STR", "LAAN", "WEG", "PAD", "RYLAAN"]
    number_re = re.compile("^\d+$")
    clean_sentences = []
    sentence_strings = []
    all_not_unique = []
    all_words = []
    sentence_string_final = ""
    term_counts_per_postcode = {}
    count = 0
    term_counts = {}
    for (postcode, addresses) in postal_code_to_address.items():
        term_counts_per_postcode[postcode] = Counter()
        tokens_for_postcode = []
        for sentence in addresses:
            sentence = re.sub(r"\s+", " ", sentence)
            sentence = remove_comma_etc(sentence)
            # using a list comprehension here instead of a loop due to advice from
            # https://towardsdatascience.com/speeding-up-python-code-fast-filtering-and-slow-loops-8e11a09a9c2f
            # still - this is one of the slowest pieces of the code
            for name in [
                name for name in suburb_names_with_spaces if name in sentence
            ]:
                name_dash = name.replace(" ", "-")
                sentence = sentence.replace(name, name_dash)
            # for name in suburb_names:
            #     if name in sentence:
            #         name_dash = name.replace(" ", "-")
            #         sentence = sentence.replace(name, name_dash)

            sentence_tok = sentence.split(" ")
            good_tokens = [
                tok
                for tok in sentence_tok
                if len(tok) > 2
                and tok not in excluded_words
                and tok not in street_types
                # creates a list where tok occurs once for each time that tok
                # ends with a string that is in afrikaans_street_endings
                and len([tok for w in afrikaans_street_endings if tok.endswith(w)]) == 0
                and not number_re.match(tok)
            ]
            token_pairs = combinations(sorted(set(good_tokens)), 2)
            # this is also a slow line due to the vast number of times it gets called
            [tok_pair_counter.add(pair) for pair in token_pairs]
            for tok in good_tokens:
                term_counts[tok] = term_counts.get(tok, 0) + 1
                term_counts_per_postcode[postcode].add(tok)
                all_not_unique.append(tok)
            clean_sentences.append(sentence_tok)

            sentence_string = " ".join(sentence_tok)
            count += 1

        # 10 most common terms for each postcode
        most_common_terms = set(
            [t[0] for t in term_counts_per_postcode[postcode].most_common(10)]
        )
        towns_seen = set()
        for suburb in most_common_terms.intersection(afrigis_suburbs):
            towns_seen.add(afrigis_suburb_to_town[suburb])
        # print(postcode, most_common_terms.intersection(afrigis_suburbs))
        # print(postcode, most_common_terms)
        # if len(towns_seen) > 1 and 'CAPE-TOWN' not in towns_seen:
        #     print(postcode, 'DISCORDANT:', list(towns_seen))
        # elif len(towns_seen) == 0:
        #     towns_seen = most_common_terms.intersection(afrigis_towns)
        #     if len(towns_seen) == 0:
        #         print(postcode, 'UNKNOWN:', most_common_terms)
        #     else:
        #         print('KNOWN1', towns_seen, postcode)
        # else:
        #     print('KNOWN2', towns_seen, postcode)

    postcode_to_suburb = {}
    postcode_to_town = {}
    term_to_postcode = {}
    most_common_terms_all_postcodes = {}
    for postcode in postal_code_to_address:
        # TODO: don't hard core this very arbitrary parameter
        top_terms = int(0.10 * len(term_counts_per_postcode[postcode].most_common()))
        most_common_term_counts = term_counts_per_postcode[postcode].most_common(
            top_terms
        )
        terms_to_use = []
        kw = False
        for (term, count) in most_common_term_counts:
            # if term == 'KENWYN':
            #     kw = True
            #     print(postcode, count, term_counts[term], term_counts_per_postcode[postcode].most_common(10))
            # some very arbitrary parameters here. TODO: make these part of function signature
            if term_counts[term] < 4:
                continue
            if len(most_common_term_counts) > 5 and count < 5:
                continue
            if count < 0.1 * term_counts[term]:
                # print('SUSPICIOUS:', term, count, term_counts[term], postcode, [t[0] for t in term_counts_per_postcode[postcode].most_common()])
                continue
            elif term == "CAPE-TOWN" and not postcode.startswith("8"):
                # assume all Cape Town central postcodes start with '8'
                continue
            terms_to_use.append(term)
            most_common_terms_all_postcodes[term] = count
        store_terms = False
        if len(set(terms_to_use).intersection(afrigis_suburbs)) > 0:
            store_terms = True
            postcode_to_suburb[postcode] = list(
                set(terms_to_use).intersection(afrigis_suburbs)
            )
        elif len(set(terms_to_use).intersection(afrigis_towns)) == 1:
            store_terms = True
            postcode_to_suburb[postcode] = list(
                set(terms_to_use).intersection(afrigis_towns)
            )
        # if 'KENWYN' in terms_to_use:
        #     print('Kewyn:', store_terms, most_common_term_counts, set(terms_to_use).intersection(afrigis_suburbs), set(terms_to_use).intersection(afrigis_towns))
        if store_terms:
            # only store terms if there is a link from postcode to an AfriGIS place
            for term in terms_to_use:
                term_to_postcode[term] = postcode
        # print(postcode, len(term_counts_per_postcode[postcode]))
    all_words = list(set(all_not_unique))
    # 100 most common pairs of tokens seen together in an address
    # print(tok_pair_counter.most_common(100))
    freq_cutoff = 0.1
    tok_frequency_cutoff = 5
    # try and find the token pairs where the frequency of the token pair
    # is common and each member of the token pair is commonly associated with
    # the other member of the pair
    keys_to_keep = set(
        [
            k
            for (k, v) in tok_pair_counter.counts.items()
            if v > tok_frequency_cutoff and v > (freq_cutoff * term_counts[k[0]])
            and v > (freq_cutoff * term_counts[k[1]])
        ]
    )

    data = {
        "term_to_postcode": term_to_postcode,
        "postcode_to_suburb": postcode_to_suburb,
        "postcode_to_town": postcode_to_town,
        "most_common_terms_all_postcodes": most_common_terms_all_postcodes,
        "token_pairs": dict(
            zip(
                [str(k) for k in tok_pair_counter.counts.keys() if k in keys_to_keep],
                [v for (k, v) in tok_pair_counter.counts.items() if k in keys_to_keep],
            )
        ),
    }
    json.dump(data, open("data.json", "w"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("address_filename", default="address_test_set_pvh.txt")
    args = parser.parse_args()
    make_clouds(args.address_filename)
