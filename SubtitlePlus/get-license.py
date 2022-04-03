import json
with open("in-toto1.bom", 'r') as fp:
    # json.loads(fp.read())
    data = json.load(fp)

licenses = set()
# _ = [[licenses.add(x['license']['name']) for x in y['licenses']] for y in data['components']]
for y in data['components']:
    # print(y)
    try:
        y['licenses']
    except:
        continue
    for x in y['licenses']:
        # print(x)
        licenses.add(x['expression'])
print(licenses)