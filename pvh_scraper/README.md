### Geocoding from imprecise addresses

There are two main scripts in this repository. The [addresses_to_clouds.py](addresses_to_clouds.py)
script builds "wordclouds" from a test set of addresses. These try and associate keywords with postal codes and thus locations (drawn from the AfriGIS data file).
In addition to the input file of addresses it relies on [AfriGIS_Suburbs_Towns_List.csv](https://github.com/pvanheus/wc_geocoder/blob/master/AfriGIS_Suburbs_Towns_List.csv) (a tab-separated file,
despite being called .csv), [all_suburbs_words.txt](all_suburbs_words.txt) and 
[street_types.txt](street_types.txt), all have to be in the same directory of the script.

The output is a file [data.json](data.json).

The second script, [assign_geocode_to_address.py](assign_geocode_to_address.py), takes input in a tab seperated file,
with at least the columns `address_row_id`, `AddressLine1`, `AddressLine2`, `AddressLine3`, `AddressLine4` and `postal_code` (column names must be in the first row of the file).
It extracts the address and using the files from the addresses_to_clouds.py script tries to associated the address with a AfriGIS suburb. The output is a copy
of the input with new columns added showing the predicted suburb and city/town, the method used to make the decision, and some diagnostic data.

To run assign_geocode_to_address.py, pass it the name of the file with addresses that you want to geocode, formatted
with headers as mentioned above:

```bash
python assign_geocode_to_address.py input_file.tsv
```

Where `input_file.tsv` is the name of your input file. The output gets written to two files,
`annotated.tsv` for addresses that could be unambiguously resolved and a file called
`problem_annotated.tsv` for addresses where the script found problems.

The suburb names are all coverted to uppercase and spaces in suburb names (e.g. Fish Hoek) are replaced with hyphens (e.g. FISH-HOEK).

The code should work on all versions of Python.

### Missing data

The `AfriGIS_Suburbs_Towns_List.csv` is derived from proprietary data and is not included. Also `address_test_set_pvh.txt` and `test_addresses.txt` are restricted datasets and only the header line is included in this repository.

#### assign_geocode_to_address.py

```bash
$ python assign_geocode_to_address.py --help
usage: assign_geocode_to_address.py [-h] [--row ROW] [--output_filename OUTPUT_FILENAME] [--afrigis_filename AFRIGIS_FILENAME]
                                    [--data_json_filename DATA_JSON_FILENAME] [--suburb_names_filename SUBURB_NAMES_FILENAME]
                                    [--street_types_filename STREET_TYPES_FILENAME]
                                    address_filename

positional arguments:
  address_filename

optional arguments:
  -h, --help            show this help message and exit
  --row ROW             Only process this row
  --output_filename OUTPUT_FILENAME
                        Name of file to write output to
  --afrigis_filename AFRIGIS_FILENAME
                        AfriGIS towns and suburbs filename
  --data_json_filename DATA_JSON_FILENAME
                        File containing prediction data (produced by addresses_to_clouds.py)
  --suburb_names_filename SUBURB_NAMES_FILENAME
                        File containing words commonly associated with suburbs
  --street_types_filename STREET_TYPES_FILENAME
                        File containing words typically associated with street names
```