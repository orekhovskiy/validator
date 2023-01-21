import json
import yaml
from munch import DefaultMunch
import jsonpickle
from openapi_core import Spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.validation.response import openapi_response_validator
from openapi_core.contrib.requests import RequestsOpenAPIResponse
import base64
from jsonschema.validators import RefResolver


if __name__ == '__main__':

    with open('openapi.json', 'r') as spec_file:
        spec_dict = json.load(spec_file)
    with open('req.json', 'r') as req_file:
        req_str = req_file.read()
        request = DefaultMunch.fromDict(jsonpickle.decode(req_str))
        for i in request.keys():
            request.update({i: jsonpickle.decode(request[i])})
    with open('res.json', 'r') as res_file:
        res_str = res_file.read()
        response = DefaultMunch.fromDict(jsonpickle.decode(res_str))
        for i in response.keys():
            response.update({i: jsonpickle.decode(response[i])})
        response.content = response._content

    spec = Spec.create(spec_dict)
    openapi_request = RequestsOpenAPIRequest(request)
    result = openapi_request_validator.validate(spec, openapi_request)

    # raise errors if request invalid
    result.raise_for_errors()

    # get list of errors
    errors = result.errors

    # get parameters object with path, query, cookies and headers parameters
    validated_params = result.parameters
    # or specific location parameters
    validated_path_params = result.parameters.path

    # get body
    validated_body = result.body

    print('validated params', validated_params)
    print('validated path params', validated_path_params)
    print('validated body', validated_body)

    # response = contract.http_interactions[0].response
    openapi_response = RequestsOpenAPIResponse(response)
    result = openapi_response_validator.validate(spec, openapi_request, openapi_response)
    # raise errors if response invalid
    result.raise_for_errors()

    # get list of errors
    errors_response = result.errors
    # get headers
    validated_headers = result.headers
    # get data
    validated_data = result.data
    print('validated headers', validated_headers)
    print('validated data', validated_data)

    ref_resolver = RefResolver.from_schema(spec)
    url, object_schema = ref_resolver.resolve('#/components/schemas/Recipe')

    def build_actual_body(schema: dict, body_sent: dict):
        actual_body = {}
        for property_sent in body_sent.keys():

