import jsonschema
from jsonschema import Draft7Validator, draft7_format_checker

# Define the first JSON schema
schema1 = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "email"]
}

# Define the second JSON schema
schema2 = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
        "phone": {"type": "string"}
    },
    "required": ["name", "email", "phone"]
}


if __name__ == '__main__':
    try:
        jsonschema.validate(instance=schema2, schema=schema1)
        print("schema2 has all properties from schema1")
    except jsonschema.exceptions.ValidationError as e:
        print(e)