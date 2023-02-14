# Lululemon Coding Challenge
# Alex Kozak
# June 27th, 2022
#
# Additional packages needed:
#   requests

import csv
from dataclasses import dataclass
import dataclasses
import json
import requests
import string


input_csv = "./input.csv"
output_json = "./output.json"

api_key = "<API_KEY_HERE>"
positionstack_url = "http://api.positionstack.com/v1/forward"


@dataclass(init=False)
class Store_Address:
    # The intended output fields in the correct order. geopoint is a little strange, as it could be its own dataclass, but for the sake of time, (and ease of output dumping) it was left as a generic dict.
    street_address: string
    locality: string
    region: string
    country: string
    geopoint: dict

    def __init__(self, **kwargs):
        try:
            # for all fields directly matching with the output of the positionstack url.
            names = set([field.name for field in dataclasses.fields(self)])
            for key, value in kwargs.items():
                if key in names:
                    setattr(self, key, value)

            # for compound fields, and fields with different names than expected.
            self.street_address = "{} {}".format(kwargs["number"], kwargs["street"])
            self.geopoint = {"lat": kwargs["latitude"], "long": kwargs["longitude"]}
        except:
            pass


def execute_address_search(input_filename):
    # Parse out the addresses from the input CSV file and get the api results.
    search_results = {}
    with open(input_filename) as csv_input:
        # Using the DictReader to account for the first line labels of the input.
        # IDEALLY there would be error checking here, as there could be improper data input, but for the purposes of this challenge, I'm assuming correct data.
        input_reader = csv.DictReader(csv_input)
        for input_row in input_reader:
            # Error check this as well, since it is using hard coded strings for dictionary access, AND assuming there are results from the API.
            # The only way I was able to break the API was by putting single character addresses, which would throw an exception. Should be addressed.
            search_results[input_row["Store"]] = requests.get(
                positionstack_url,
                params={
                    "access_key": api_key,
                    "query": input_row["Address"],
                    "limit": 1,
                },
            ).json()["data"][0]
    return search_results


def processs_raw_search(search_results):
    # The filtering of extraneous inputs was done using a dataclass, and running any processing through the __init__ function
    return {
        store_number: Store_Address(**search_results[store_number])
        for store_number in search_results
    }


def dump_address_class(store_addresses):
    # Creating the string that we want to dump to the output, with the dataclass being formatted in the same way as the intended output.
    return json.dumps(
        {
            store_number: dataclasses.asdict(store_address)
            for store_number, store_address in store_addresses.items()
        },
        indent=4,
    )


def dump_to_output(output_file, data):
    # Realistically this is a bit of a moot function, but it serves to make the main section more readable.
    with open(output_file, "w") as dump_file:
        dump_file.write(data)


if __name__ == "__main__":
    search_results = execute_address_search(input_csv)
    processed_results = processs_raw_search(search_results)
    generated_data = dump_address_class(processed_results)
    dump_to_output(output_json, generated_data)

    # Or if you're feeling like making it a one liner...
    # dump_to_output(output_json, dump_address_class(processs_raw_search(execute_address_search(input_csv))))
