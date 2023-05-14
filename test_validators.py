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
from ContractValidator import ClientContractDataClass, ContractValidator
from SpecValidator import SpecValidator

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
    openapi_response = RequestsOpenAPIResponse(response)
    contract = ClientContractDataClass(
        consumer='test',
        req=openapi_request,
        res=openapi_response,
    )
    contract_validator = ContractValidator()
    spec_validator = SpecValidator()
    localContract = contract_validator.validate_contract(contract, spec)
    print(localContract)
    spec_validator.validate_spec(spec, [localContract])
