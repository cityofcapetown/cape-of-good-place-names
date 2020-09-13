from contextlib import contextmanager
import io
import pprint
import logging
import os
import sys
import tempfile
import unittest

import phdc_scrubber
from phdc_scrubber import PhdcScrubber


@contextmanager
def _get_named_tempfile(tempfilename) -> (tempfile.TemporaryDirectory, io.TextIOBase):
    with tempfile.TemporaryDirectory() as tempdir:
        tempfile_path = os.path.join(tempdir, tempfilename)
        with open(tempfile_path, "w") as named_tempfile:
            yield tempdir, named_tempfile


@contextmanager
def _get_named_tempfiles(tempfilename1, tempfilename2) -> (tempfile.TemporaryDirectory, io.TextIOBase, io.TextIOBase):
    with tempfile.TemporaryDirectory() as tempdir:
        tempfile_path1 = os.path.join(tempdir, tempfilename1)
        tempfile_path2 = os.path.join(tempdir, tempfilename2)
        with open(tempfile_path1, "w") as named_tempfile1, open(tempfile_path2, "w") as named_tempfile2:
            yield tempdir, named_tempfile1, named_tempfile2


@contextmanager
def _get_all_named_tempfiles(tempfilename1, tempfilename2, tempfilename3) -> (tempfile.TemporaryDirectory,
                                                                              io.TextIOBase,
                                                                              io.TextIOBase,
                                                                              io.TextIOBase):
    with tempfile.TemporaryDirectory() as tempdir:
        tempfile_path1 = os.path.join(tempdir, tempfilename1)
        tempfile_path2 = os.path.join(tempdir, tempfilename2)
        tempfile_path3 = os.path.join(tempdir, tempfilename3)
        with open(tempfile_path1, "w") as named_tempfile1, \
                open(tempfile_path2, "w") as named_tempfile2, \
                open(tempfile_path3, "w") as named_tempfile3:
            yield tempdir, named_tempfile1, named_tempfile2, named_tempfile3


class TestPhdcScrubber(unittest.TestCase):
    def test_create_street_type_list(self):
        test_street_types = ["blah", "foo", "bar", "foo"]
        # Setting up test data
        with _get_named_tempfile(phdc_scrubber.STREET_TYPES_FILENAME) as (datafiledir, temp_street_file):
            for street_type in test_street_types:
                temp_street_file.write(street_type + "\n")
            temp_street_file.flush()

            # Calling the func
            street_types = PhdcScrubber.create_street_types_list(datafiledir)
            logging.debug(f"street_types={pprint.pformat(street_types)}")

            # Testing the results
            self.assertEqual(3, len(street_types), "Length of street types is what is expected!")

            self.assertSetEqual({"BLAH", "FOO", "BAR"}, set(street_types), "Mismatch in street type list")

    def test_address_reference(self):
        sample_street_types = ["AVE", "RD", "ST"]
        sample_street_names = [
            "Street Name	Street Type	Postal Code	Suburb	Town	Local Municipality",
            "10th	Ave	1234	Clam Bay Central	Dassie Bay	Dassie Town",
            "11th	Ave	1234	Handboulder	WhaleTown	Dassie Town",
            "Eve	Rd	9012	Lowearth	Flowerbay	Pilchard Cove",
            "Eve	St	3456	Amsterdam North	Red Ups	Peninsula City"
        ]
        sample_here_place_lookup = [
            "Street Name	Street Type	Suburb	Town	Local Municipality",
            "Apple	Close	Siphoville	Siphoville	Siphoville Local Municipality",
            "Girl Silver	Street	Siphoville	Siphoville	Siphoville Local Municipality",
            "Tent	Street	Mouseplek	Catenberg	Peninsula City Metropolitan Municipality",
            "Tenthill	Drive	Running out of ideas	3 Tree Place	Peninsula City Metropolitan Municipality",
        ]

        with _get_named_tempfiles(phdc_scrubber.STREET_NAME_LOOKUP_FILENAME,
                                  phdc_scrubber.HERE_PLACE_LOOKUP_FILENAME) as (
                datafiledir, temp_street_name_file, temp_here_name_file):

            for street_name in sample_street_names:
                temp_street_name_file.write(street_name + "\n")
                temp_street_name_file.flush()
            for here_place in sample_here_place_lookup:
                temp_here_name_file.write(here_place + "\n")
                temp_here_name_file.flush()

            address_lookup_dict = PhdcScrubber.create_address_reference(datafiledir, sample_street_types)

            self.assertDictEqual({'1234': [['10TH', 'AVE', 'CLAM BAY CENTRAL', 'DASSIE BAY', 'DASSIE TOWN'],
                                           ['11TH', 'AVE', 'HANDBOULDER', 'WHALETOWN', 'DASSIE TOWN']],
                                  '9012': [['EVE', 'RD', 'LOWEARTH', 'FLOWERBAY', 'PILCHARD COVE']],
                                  '3456': [['EVE', 'ST', 'AMSTERDAM NORTH', 'RED UPS', 'PENINSULA CITY']],
                                  'SIPHOVILLE': [
                                      ['APPLE', 'CLOSE', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY'],
                                      ['GIRL SILVER', 'STREET', 'SIPHOVILLE', 'SIPHOVILLE',
                                       'SIPHOVILLE LOCAL MUNICIPALITY'],
                                  ],
                                  'MOUSEPLEK': [
                                      ['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG',
                                       'PENINSULA CITY METROPOLITAN MUNICIPALITY']],
                                  'CATENBERG': [['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG',
                                                 'PENINSULA CITY METROPOLITAN MUNICIPALITY']],
                                  'RUNNING OUT OF IDEAS': [
                                      ['TENTHILL', 'DRIVE', 'RUNNING OUT OF IDEAS', '3 TREE PLACE',
                                       'PENINSULA CITY METROPOLITAN MUNICIPALITY']],
                                  '3 TREE PLACE': [
                                      ['TENTHILL', 'DRIVE', 'RUNNING OUT OF IDEAS', '3 TREE PLACE',
                                       'PENINSULA CITY METROPOLITAN MUNICIPALITY']]},
                                 address_lookup_dict,
                                 "Mismatch in address reference")

    def test_get_street_info(self):
        sample_addresses_pairs = [
            ("100 10th Ave 1234 Clam Bay Central Dassie Bay Dassie Town",
             ('AVE', '100', '100 10TH AVE 1234 CLAM BAY CENTRAL DASSIE BAY DASSIE TOWN')),
            ("12 Apple Close Siphoville Siphoville Siphoville Local Municipality",
             ('', '12', '12 APPLE CLOSE SIPHOVILLE SIPHOVILLE SIPHOVILLE LOCAL MUNICIPALITY')),
            # SHOULD THIS PASS?
            ("Block 56 Tent Street Mouseplek Catenberg Peninsula City",
             ('ST', '56', 'BLOCK 56 TENT STREET MOUSEPLEK CATENBERG PENINSULA CITY')),
        ]
        sample_street_types = ["AVE", "RD", "ST"]

        for sample_address, expected_info in sample_addresses_pairs:
            address_info = PhdcScrubber.get_street_info(sample_address, sample_street_types)
            self.assertTupleEqual(expected_info, address_info, "Mismatch in extracted address info")

    def test_get_matches(self):
        sample_addresses = [
            ("100 10th Ave 1234 Clam Bay Central Dassie Bay Dassie Town", '1234', [
                ('postcode_match', [
                    ['10TH', 'AVE', 'CLAM BAY CENTRAL', 'DASSIE BAY', 'DASSIE TOWN'],
                    ['11TH', 'AVE', 'HANDBOULDER', 'WHALETOWN', 'DASSIE TOWN']
                ], 2),
                ('suburb_or_town_string_match', [
                    ['10TH', 'AVE', 'CLAM BAY CENTRAL', 'DASSIE BAY', 'DASSIE TOWN'],
                    ['11TH', 'AVE', 'HANDBOULDER', 'WHALETOWN', 'DASSIE TOWN']
                ], 0)
            ]),
            ("12 Apple Close Siphoville Siphoville Siphoville Local Municipality", '', [
                ('suburb_or_town_words_match', [
                    ['APPLE', 'CLOSE', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY'],
                    ['GIRL SILVER', 'STREET', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY']
                ], 1),
                ('suburb_or_town_words_match', [
                    ['APPLE', 'CLOSE', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY'],
                    ['GIRL SILVER', 'STREET', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY']
                ], 1),
                ('suburb_or_town_string_match', [
                    ['APPLE', 'CLOSE', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY'],
                    ['GIRL SILVER', 'STREET', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY']
                ], 0)]),
            ("Block 56 Tent Street Mouseplek Catenberg Peninsula City", '', [
                ('suburb_or_town_words_match', [
                    ['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG', 'PENINSULA CITY METROPOLITAN MUNICIPALITY']
                ], 1),
                ('suburb_or_town_words_match', [
                    ['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG', 'PENINSULA CITY METROPOLITAN MUNICIPALITY']
                ], 1),
                ('suburb_or_town_string_match', [
                    ['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG', 'PENINSULA CITY METROPOLITAN MUNICIPALITY']
                ], 0),
                ('suburb_or_town_string_match', [
                    ['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG', 'PENINSULA CITY METROPOLITAN MUNICIPALITY']
                ], 0)]),
        ]

        sample_address_dict = {'1234': [['10TH', 'AVE', 'CLAM BAY CENTRAL', 'DASSIE BAY', 'DASSIE TOWN'],
                                        ['11TH', 'AVE', 'HANDBOULDER', 'WHALETOWN', 'DASSIE TOWN']],
                               '9012': [['EVE', 'RD', 'LOWEARTH', 'FLOWERBAY', 'PILCHARD COVE']],
                               '3456': [['EVE', 'ST', 'AMSTERDAM NORTH', 'RED UPS', 'PENINSULA CITY']],
                               'SIPHOVILLE': [
                                   ['APPLE', 'CLOSE', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY'],
                                   ['GIRL SILVER', 'STREET', 'SIPHOVILLE', 'SIPHOVILLE',
                                    'SIPHOVILLE LOCAL MUNICIPALITY'],
                               ],
                               'MOUSEPLEK': [
                                   ['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG',
                                    'PENINSULA CITY METROPOLITAN MUNICIPALITY']],
                               'CATENBERG': [['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG',
                                              'PENINSULA CITY METROPOLITAN MUNICIPALITY']],
                               'RUNNING OUT OF IDEAS': [
                                   ['TENTHILL', 'DRIVE', 'RUNNING OUT OF IDEAS', '3 TREE PLACE',
                                    'PENINSULA CITY METROPOLITAN MUNICIPALITY']],
                               '3 TREE PLACE': [
                                   ['TENTHILL', 'DRIVE', 'RUNNING OUT OF IDEAS', '3 TREE PLACE',
                                    'PENINSULA CITY METROPOLITAN MUNICIPALITY']]}

        for sample_address_string, sample_address_postcode, expected_matches in sample_addresses:
            sample_address_words = sample_address_string.split()
            matches = PhdcScrubber.get_matches(
                sample_address_words, sample_address_string, sample_address_dict, sample_address_postcode
            )
            self.assertListEqual(expected_matches, matches, "Mismatch in match results")

    def test_score_match(self):
        sample_addresses = [
            ("100 10th Ave 1234 Clam Bay Central Dassie Bay Dassie Town", '1234', [
                ('postcode_match', [
                    (['10TH', 'AVE', 'CLAM BAY CENTRAL', 'DASSIE BAY', 'DASSIE TOWN'], 5),
                    (['11TH', 'AVE', 'HANDBOULDER', 'WHALETOWN', 'DASSIE TOWN'], None)
                ], 2,),
                ('suburb_or_town_string_match', [
                    (['10TH', 'AVE', 'CLAM BAY CENTRAL', 'DASSIE BAY', 'DASSIE TOWN'], 3),
                    (['11TH', 'AVE', 'HANDBOULDER', 'WHALETOWN', 'DASSIE TOWN'], None)
                ], 0,)
            ]),
            ("12 Apple Close Siphoville Siphoville Siphoville Local Municipality", '', [
                ('suburb_or_town_words_match', [
                    (['APPLE', 'CLOSE', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY'], 4),
                    (['GIRL SILVER', 'STREET', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY'], None)
                ], 1,),
                ('suburb_or_town_words_match', [
                    (['APPLE', 'CLOSE', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY'], 4),
                    (['GIRL SILVER', 'STREET', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY'], None)
                ], 1,),
                ('suburb_or_town_string_match', [
                    (['APPLE', 'CLOSE', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY'], 3),
                    (['GIRL SILVER', 'STREET', 'SIPHOVILLE', 'SIPHOVILLE', 'SIPHOVILLE LOCAL MUNICIPALITY'], None)
                ], 0,)
            ]),
            ("Block 56 Tent Street Mouseplek Catenberg Peninsula City", '', [
                ('suburb_or_town_words_match', [
                    (['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG', 'PENINSULA CITY METROPOLITAN MUNICIPALITY'], 4)
                ], 1,),
                ('suburb_or_town_words_match', [
                    (['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG', 'PENINSULA CITY METROPOLITAN MUNICIPALITY'], 4)
                ], 1,),
                ('suburb_or_town_string_match', [
                    (['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG', 'PENINSULA CITY METROPOLITAN MUNICIPALITY'], 3)
                ], 0,),
                ('suburb_or_town_string_match', [
                    (['TENT', 'STREET', 'MOUSEPLEK', 'CATENBERG', 'PENINSULA CITY METROPOLITAN MUNICIPALITY'], 3)
                ], 0,)
            ]),
        ]
        sample_street_types = ["AVE", "RD", "ST"]

        for address_string, post_code, match_tuple in sample_addresses:
            for match_type, records_with_score, initial_score in match_tuple:
                street_type, street_number, _ = PhdcScrubber.get_street_info(address_string, sample_street_types)
                address_words = list(map(lambda w: w.upper(), address_string.split()))

                records = list(map(lambda r_w_s: r_w_s[0], records_with_score))
                post_code = post_code if match_type == "postcode_match" else None
                for (score, final_tuple), (_, expected_score) in zip(
                        PhdcScrubber.score_match(initial_score, address_words, records,
                                                 street_number, street_type, post_code),
                        records_with_score):
                    self.assertEqual(expected_score, score,
                                     f"Mismatch in match scoring for '{address_string}' "
                                     f"against '{pprint.pformat(records)}'")

    def test_end_to_end(self):
        sample_street_types = ["AVE", "RD", "ST"]
        sample_street_names = [
            "Street Name	Street Type	Postal Code	Suburb	Town	Local Municipality",
            "10th	Ave	1234	Clam Bay Central	Dassie Bay	Dassie Town",
            "11th	Ave	1234	Handboulder	WhaleTown	Dassie Town",
            "Eve	Rd	9012	Lowearth	Flowerbay	Pilchard Cove",
            "Eve	St	3456	Amsterdam North	Red Ups	Peninsula City"
        ]
        sample_here_place_lookup = [
            "Street Name	Street Type	Suburb	Town	Local Municipality",
            "Apple	Close	Siphoville	Siphoville	Siphoville Local Municipality",
            "Girl Silver	Street	Siphoville	Siphoville	Siphoville Local Municipality",
            "Tent	Street	Mouseplek	Catenberg	Peninsula City Metropolitan Municipality",
            "Tenthill	Drive	Running out of ideas	3 Tree Place	Peninsula City Metropolitan Municipality",
        ]

        test_addresses = (
            ("100 10th Ave 1234 Clam Bay Central Dassie Bay Dassie Town", 1, '100 10TH AVE CLAM BAY CENTRAL DASSIE BAY 1234'),
            ("12 Apple Close Siphoville", 0.8, '12 APPLE  SIPHOVILLE SIPHOVILLE'),
            ("Block 56 Tent Street Mouseplek Catenberg Peninsula City", 0.8, '56 TENT ST MOUSEPLEK CATENBERG'),
            ("123 Ernest Drive Siyabulela 5678", 0.0, '123 ERNEST DRIVE SIYABULELA 5678')
        )

        # Setting up test data
        with _get_all_named_tempfiles(phdc_scrubber.STREET_TYPES_FILENAME,
                                      phdc_scrubber.STREET_NAME_LOOKUP_FILENAME,
                                      phdc_scrubber.HERE_PLACE_LOOKUP_FILENAME) as (datafiledir,
                                                                                    temp_street_file,
                                                                                    temp_street_name_file,
                                                                                    temp_here_name_file):
            for street_type in sample_street_types:
                temp_street_file.write(street_type + "\n")
            temp_street_file.flush()

            for street_name in sample_street_names:
                temp_street_name_file.write(street_name + "\n")
            temp_street_name_file.flush()

            for here_place in sample_here_place_lookup:
                temp_here_name_file.write(here_place + "\n")
            temp_here_name_file.flush()

            scrubber = PhdcScrubber.PhdcScrubber(datafiledir)
            for test_address, expected_confidence, expected_final_address in test_addresses:
                final_address, confidence = scrubber.scrub(test_address)

                self.assertEqual(expected_confidence, confidence,
                                 f"Expected confidence doesn't line up for '{test_address}'")
                self.assertEqual(expected_final_address, final_address, "Final address doesn't line up")


if __name__ == '__main__':
    unittest.main()
