from typing import List
from jsonschema.validators import RefResolver
from openapi_core import Spec, openapi_request_validator, openapi_response_validator
from openapi_core.contrib.requests import RequestsOpenAPIRequest, RequestsOpenAPIResponse
from dataclasses import dataclass


@dataclass
class ClientContractDataClass:
    consumer: str
    req: RequestsOpenAPIRequest
    res: RequestsOpenAPIResponse


@dataclass
class LocalContractDataClass:
    title: str
    version: str
    endpoint: str
    req_path_params: dict
    req_method: str
    req_query_params: dict
    req_body: dict
    res_status: str
    res_data: dict


class ContractValidator:
    def validate_contract(self, contract: ClientContractDataClass, spec: Spec) \
            -> LocalContractDataClass:
        validation_req_result = openapi_request_validator.validate(spec, contract.req)
        validation_req_result.raise_for_errors()
        validation_res_result = openapi_response_validator.validate(spec, contract.req, contract.res)
        validation_res_result.raise_for_errors()

        status = str(contract.res.response.status_code)
        endpoint = self.get_endpoint(contract.req.path, spec.getkey('paths').keys())
        req_method = contract.req.method

        ref_resolver = RefResolver.from_schema(spec)
        req_object_schema = spec.getkey('paths')[endpoint][req_method]["requestBody"]["content"]["application/json"]["schema"] \
            if 'requestBody' in spec.getkey('paths')[endpoint][req_method].keys() \
            else {}
        if '$ref' in req_object_schema.keys():
            _, req_object_schema = ref_resolver.resolve(req_object_schema['$ref'])
        res_object_schema = \
            spec.getkey('paths')[endpoint][req_method]['responses'][status]['content']["application/json"]["schema"]
        if '$ref' in res_object_schema.keys():
            _, res_object_schema = ref_resolver.resolve(res_object_schema['$ref'])

        req_body = self.get_body(req_object_schema, validation_req_result.body, contract.consumer)
        res_data = self.get_body(res_object_schema, validation_res_result.data, contract.consumer)

        return LocalContractDataClass(
            title=spec.getkey('info')['title'],
            version=spec.getkey('info')['version'],
            endpoint=endpoint,
            req_path_params=validation_req_result.parameters.path,
            req_method=req_method,
            req_query_params=validation_req_result.parameters.query,
            req_body=req_body,
            res_status=status,
            res_data=res_data,
        )

    def validate_path(self, contract_path: str, spec_path: str) -> bool:
        contract_path_parts = contract_path.split('/')
        spec_path_parts = spec_path.split('/')
        if len(spec_path_parts) != len(contract_path_parts):
            return False
        for i in range(len(spec_path_parts)):
            if contract_path_parts[i] != spec_path_parts[i]:
                if spec_path_parts[i][0] == '{' and spec_path_parts[i][-1] == '}':
                    pass
                else:
                    return False
        return True

    def get_endpoint(self, contract_path, spec_paths: List[str]):
        for path in spec_paths:
            if self.validate_path(contract_path, path):
                return path
        raise Exception(f'No path match found for given spec paths:{spec_paths} and contract_path: {contract_path}')

    def get_body(self, schema: dict, body_sent: dict, consumer_name: str):
        if not schema and not body_sent:
            return {}
        if schema['type'] == 'object':
            properties = {}
            for property_sent in body_sent.keys():
                if property_sent in schema['properties']:
                    actual_property = self.get_body(schema['properties'][property_sent], body_sent[property_sent], consumer_name)
                    properties[property_sent] = actual_property
            actual_body = {
                'title': schema['title'],
                'type': 'object',
                'consumers': [consumer_name],
                'properties': properties,
            }
        elif schema['type'] == 'array':
            actual_body = {
                'title': schema['title'],
                'type': schema['type'],
                'consumers': [consumer_name],
                'items': self.get_body(schema['items'], body_sent[0], consumer_name)
            }
        else:
            actual_body = {
                'title': schema['title'],
                'type': schema['type'],
                'consumers': [consumer_name],
            }
        return actual_body
