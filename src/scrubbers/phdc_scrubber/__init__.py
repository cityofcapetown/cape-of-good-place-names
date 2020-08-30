# Data files
STREET_TYPES_FILENAME = "street_types.txt"

STREET_NAME_LOOKUP_FILENAME = "street_name_dict.txt"
HERE_PLACE_LOOKUP_FILENAME = "HERE_StreetNameSuburbDictionary.txt"

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

STREET_NO_REGEX_PATTERN = (
    '(STR\. *\d+ *\D\s)|'
    '(STR\. *\d+\s)|'
    '(\d+-\d+)|'
    '(^\D\.\d+)|'
    '(\s\D\d+)|'
    '(^\D-\d+)|'
    '(\s\D-\d+)|'
    '(\d+\s\D\s)|'
    '(^\D\d+)|'
    '(^\D\s\d+)|'
    '(\s\d+\D\s)|'
    '(\s\d+\s\D\s)|'
    '(^\d+\s\D\s)|'
    '(^\d+\D\s)|'
    '(\s\d+\s)|'
    '(^\d+ )'
)