from typing import List, Tuple


class BodyBuilder:
    def __init__(self, consumer_name: str):
        self.consumer_name = consumer_name

    def build_actual_body(self, schema: dict, body_sent: dict):
        actual_body = {}
        if schema['type'] == 'object':
            properties = {}
            for property_sent in body_sent.keys():
                if property_sent in schema['properties']:
                    actual_property = self.build_actual_body(schema['properties'][property_sent], body_sent[property_sent])
                    properties[property_sent] = actual_property
            actual_body = {
                'title': schema['title'],
                'type': 'object',
                'consumers': [self.consumer_name],
                'properties': properties,
            }
        elif schema['type'] == 'array':
            actual_body = {
                'title': schema['title'],
                'type': schema['type'],
                'consumers': [self.consumer_name],
                'items': self.build_actual_body(schema['items'], body_sent[0])
            }
        else:
            actual_body = {
                'title': schema['title'],
                'type': schema['type'],
                'consumers': [self.consumer_name],
            }
        return actual_body

    def validate_schema_by_actual_body(self, actual_body: dict, schema: dict, path="") -> Tuple[bool, str]:
        if schema['type'] == actual_body['type']:
            if schema['type'] == 'object':
                print('path: ', path)
                nested_path = f"{path}.{schema['title']}" if path else schema['title']
                for prop in actual_body['properties'].keys():
                    if prop in schema['properties'].keys():
                        (status, msg) = self.validate_schema_by_actual_body(actual_body['properties'][prop], schema['properties'][prop], nested_path)
                        if not status:
                            return status, msg
                    else:
                        print("prop", prop)
                        return False, f"Schema is missing property {nested_path}.{prop}"
            elif schema['type'] == 'array':
                nested_path = f"{path}.{schema['title']}[]" if path else f"{schema['title']}[]"
                return self.validate_schema_by_actual_body(actual_body['items'], schema['items'], nested_path)
        else:
            return False, f"Type of given schema has unexpected type: expected ${actual_body['type']} but got ${schema['type']} instead"
        return True, ""

    def combine_bodies(self, body: dict, *args: List[dict]):
        if len(args) == 0:
            return body
        result_body = {}
        i = j = 0
        body_sorted_keys = list(body.keys()).sort()
        arg_sorted_keys = list(args[0].keys()).sort()
        while i < len(body.keys()) or j < len(args[0].keys()):
            if body[body_sorted_keys[i]] == args[0][arg_sorted_keys[j]]:
                result_body[body_sorted_keys[i]] = self.combine_bodies(
                    body[body_sorted_keys[i]],
                    args[0][arg_sorted_keys[j]]
                )
                i += 1
                j += 1
            elif body[body_sorted_keys[i]] < args[0][arg_sorted_keys[j]]:
                result_body[body_sorted_keys[i]] = body[body_sorted_keys[i]]
                i += 1
            else:
                result_body[arg_sorted_keys[j]] = args[0][arg_sorted_keys[j]]
                j += 1
        return self.combine_bodies(result_body, *args[1:])
