import json
from munch import DefaultMunch
import jsonpickle
from openapi_core import Spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.validation.response import openapi_response_validator
from openapi_core.contrib.requests import RequestsOpenAPIResponse
from jsonschema.validators import RefResolver
from BodyBuilder import BodyBuilder


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
        print("response: ", response)
        for i in response.keys():
            response.update({i: jsonpickle.decode(response[i])})
        response.content = response._content
        print(response.content)

    spec = Spec.create(spec_dict)
    print("spec paths: ", spec.getkey('paths').keys())
    print("spec items: ", spec.keys())
    print("spec info: ", spec.getkey('info').keys())
    print("spec comps: ", spec.getkey('components'))

    openapi_request = RequestsOpenAPIRequest(request)

    print("req path: ", openapi_request.path)

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
    print("res url: ", openapi_response.response.url)
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
    builder = BodyBuilder('test')
    actual_body = builder.build_actual_body(object_schema, validated_data)
    print(actual_body)

    with open('openapi2.json', 'r') as spec_file:
        spec_dict2 = json.load(spec_file)
    spec2 = Spec.create(spec_dict2)
    ref_resolver2 = RefResolver.from_schema(spec2)
    url2, object_schema2 = ref_resolver2.resolve('#/components/schemas/Recipe')
    print('obj schema 2: ', object_schema2)

    print(builder.validate_schema_by_actual_body(actual_body, object_schema2))

