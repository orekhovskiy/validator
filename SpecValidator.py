from typing import List
from jsonschema.validators import RefResolver
from ContractValidator import LocalContractDataClass
from openapi_core import Spec


class SpecValidator:
    def validate_spec(self, spec: Spec, local_contracts: List[LocalContractDataClass]) -> None:
        ref_resolver = RefResolver.from_schema(spec)
        for contract in local_contracts:
            req_object_schema = \
                spec.getkey('paths')[contract.endpoint][contract.req_method]["requestBody"]["content"]["application/json"]["schema"] \
                if 'requestBody' in spec.getkey('paths')[contract.endpoint][contract.req_method].keys() \
                else {}
            res_object_schema = \
                spec.getkey('paths')[contract.endpoint][contract.req_method]['responses'][contract.res_status]['content']["application/json"]["schema"]
            if '$ref' in res_object_schema.keys():
                _, res_object_schema = ref_resolver.resolve(res_object_schema['$ref'])

            self.validate_body_schema_by_actual_body(contract.req_body, req_object_schema)
            self.validate_body_schema_by_actual_body(contract.res_data, res_object_schema)

    def validate_body_schema_by_actual_body(self, actual_body: dict, schema: dict, path="") -> None:
        if not actual_body and not schema:
            return
        if schema['type'] != actual_body['type']:
            raise Exception(f"Type of given schema has unexpected type: expected ${actual_body['type']} but got ${schema['type']} instead")
        if schema['type'] == 'object':
            nested_path = f"{path}.{schema['title']}" if path else schema['title']
            for prop in actual_body['properties'].keys():
                if prop in schema['properties'].keys():
                    self.validate_body_schema_by_actual_body(
                        actual_body['properties'][prop],
                        schema['properties'][prop],
                        nested_path
                    )
                else:
                    raise Exception(f"Schema is missing property {nested_path}.{prop}")
        elif schema['type'] == 'array':
            nested_path = f"{path}.{schema['title']}[]" if path else f"{schema['title']}[]"
            self.validate_body_schema_by_actual_body(
                actual_body['items'],
                schema['items'],
                nested_path
            )
