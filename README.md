# cape-of-good-place-names
Service developed as a shared initiative between the Western Cape Provincial and City of Cape Town

## Getting Started
`ToDo`

## Development
This service is defined using an [OpenAPI](https://swagger.io/specification/) specification, the service's specification
 file is [here](docs/cogpn-spec.yaml).

### Client Code 
This means that client code for interacting with the service can be generated from the specification for most languages. 

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