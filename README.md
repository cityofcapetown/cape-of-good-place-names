# cape-of-good-place-names
Service developed as a shared initiative between the Western Cape Provincial and City of Cape Town

## Getting Started
The [cogpn-process-address script](bin/cogpn-process-address.py) script provides a minimalist example of using the 
service in-situ.

script help text:
```
usage: cogpn-process-address.py [-h] -a ADDRESS -u USERNAME -p PASSWORD [-x PROXY] [-xu PROXY_USERNAME] [-xp PROXY_PASSWORD] [-s SERVER] [-sc SCRUBBER] [-gc GEOCODER] [-v] [-o OUTPUT]

Utility script for processing an address using the Cape of Good Place Names service

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        Address to process (default: None)
  -u USERNAME, --username USERNAME
                        Username to use for Cape of Good Place Name Service (default: None)
  -p PASSWORD, --password PASSWORD
                        Password to use for Cape of Good Place Name Service (default: None)
  -x PROXY, --proxy PROXY
                        Internet proxy address (default: None)
  -xu PROXY_USERNAME, --proxy-username PROXY_USERNAME
                        Internet proxy username (default: None)
  -xp PROXY_PASSWORD, --proxy-password PROXY_PASSWORD
                        Internet proxy password (default: None)
  -s SERVER, --server SERVER
                        Cape of Good Place Name Service server name to use (default: https://api-dev.cape-of-good-place-names.xyz)
  -sc SCRUBBER, --scrubber SCRUBBER
                        ID of scrubber result to use (default: PhdcScrubber)
  -gc GEOCODER, --geocoder GEOCODER
                        ID of geocoder result to use (default: CombinedGeocoders)
  -v, --verbose         Verbosity flag (default: False)
  -o OUTPUT, --output OUTPUT
                        Output file (default: /dev/stdout)
```
*NB* Only the `ADDRESS`, `USERNAME` and `PASSWORD` arguments are required.
e.g.
```
$ python3 bin/cogpn-process-address.py --address "Civic Centre, Hertzog Blvd, Foreshore, Cape Town, 8001" \
                                       --username <REDACTED> \
                                       --password <REDACTED>
2020-09-13 13:48:53,275-cogpn-process-address [INFO]: Scrub[ing]...
2020-09-13 13:48:55,155-cogpn-process-address [INFO]: ...Scrub[ed]
2020-09-13 13:48:55,155-cogpn-process-address [INFO]: Geocod[ing]...
2020-09-13 13:48:56,356-cogpn-process-address [INFO]: ...Geocod[ed]
{"features": [{"geometry": {"coordinates": [18.429321515724716, -33.92070341399093], "type": "Point"}, "properties": {"geocoders": ["CCT", "Google"]}, "type": "Feature"}], "type": "FeatureCollection"}
```

## Development
This service is defined using an [OpenAPI](https://swagger.io/specification/) specification, the service's specification
 file is [here](docs/cogpn-spec.yaml).

### Client Code 
This means that client code for interacting with the service can be generated from the specification for most languages.

#### Python Client
A python client has been generated and checked into the source repo [src/clients/python](src/clients/python). It will 
get updated when/if [the API spec](docs/cogpn-spec.yaml) gets updated.

Installing from this repo:
1. Install the requirements: `pip3 install -r /local/src/clients/python/requirements.txt`
2. Install the package itself: `python3 install /local/src/clients/python/setup.py`

The [cogpn-process-address script](bin/cogpn-process-address.py) assumes that it has been installed.

#### Implementing the client in a new language
* list the languages available:
    ```bash
    docker run -v ${PWD}:/local openapitools/openapi-generator-cli list
    ```
* list the options for the language in question:
    ```bash
    docker run -v ${PWD}:/local openapitools/openapi-generator-cli config-help -g <generator name, e.g. "python">
    ```
* Use the `generate` command to generate the package in the language of your choice, against the spec, e.g.
    ```bash
    docker run -v ${PWD}:/local openapitools/openapi-generator-cli generate -i "/local/docs/cogpn-spec.yaml" \
                                                                            -g "python" \
                                                                            -c "/local/docs/cogpn-spec-python-client-config.json" \
                                                                            -o "/local/src/clients/python"
    ```

### Server Code
The basis for the server implementation is also generated from the specification. This should be done infrequently, as/
when the API specification changes.

1. Validate the OpenAPI spec using the IBM OpenAPI validator: `lint-openapi docs/cogpn-spec.yaml`
2. Generate the server implementation in `/src` using Swagger codegen: 
    ```bash
    docker run -v ${PWD}:/local swaggerapi/swagger-codegen-cli-v3 generate -i "/local/docs/cogpn-spec.yaml" \
                                                                           -c "/local/docs/cogpn-spec-config.json" \
                                                                           -l "python-flask" \
                                                                           -o "/local/src/server"
    ```
3. Fix permission issues: `sudo chown ${USER}:${USER} -R src`

The server's generated README will be [here](src/server/README.md)