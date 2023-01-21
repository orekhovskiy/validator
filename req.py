# import requests
# import pathlib
# import json
# import pickle
#
# if __name__ == '__main__':
#     r = requests.get('https://en.wikipedia.org/w/api.php?action=parse&page=Pet_door&format=json')
#     d=r.__dict__
#     # with open('res.json', 'wb') as f:
#     #     pickle.dump(r.content, f)
#     with open('req.json', 'wb') as f:
#         def get_json(obj):
#             return json.loads(
#                 json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
#             )
#         print(get_json(r.request))


import requests
import json
import jsonpickle
url = 'http://localhost:8001/recipe/1'

response = requests.get(url)
r = {}
for i in response.__dict__:
    r.update({i: jsonpickle.encode(response.__dict__[i])})
with open('res.json', 'w') as f:
    f.write(json.dumps(r))

r = {}
for i in response.request.__dict__:
    r.update({i: jsonpickle.encode(response.request.__dict__[i])})

with open('req.json', 'w') as f:
    f.write(json.dumps(r))
