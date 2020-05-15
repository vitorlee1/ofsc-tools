import requests
import base64
import json
import argparse

TEXT_RESPONSE=1
FULL_RESPONSE=2
JSON_RESPONSE=3


parser = argparse.ArgumentParser()
parser.add_argument("--output_json", type=str, default="result.json")
parser.add_argument("--output_csv", type=str, default="result.csv")
parser.add_argument("--instance", type=str, required=True)
parser.add_argument("--clientID", type=str, required=True)
parser.add_argument("--secret", type=str, required=True)
parser.add_argument("--parent_resource", type=str, required=True)
parser.add_argument("--expand", type=str, default="")
parser.add_argument("--fields", type=str,  default="resourceId,resourceType,parentResourceId,status")
args = parser.parse_args()




headers ={}
clientID = args.clientID
companyName = args.instance
resource_id=args.parent_resource
secret=args.secret
fields=args.fields
expand=args.expand
# Calculate Authorization
mypass = base64.b64encode(bytes(clientID+"@"+companyName+":"+secret, 'utf-8'))
headers["Authorization"] = "Basic "+mypass.decode('utf-8')
if expand == '' :
    params = {
        'offset' : '0' ,
        'fields' : fields
    }
else :
    params = {
        'offset' : '0' ,
        'fields' : fields,
        'expand' : expand
    }
response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/resources/'+str(resource_id)+'/descendants', headers=headers, params=params)

response_json=response.json()
total_results=response_json['totalResults']
offset=response_json['offset']
final_items_list=response_json['items']


while offset + 100 < total_results :
    print('Still pending resources Total Results : {} - Offset : {} - List size {}'.format(total_results, offset, len(final_items_list) ))
    offset=offset+100
    params['offset'] = offset
    response = requests.get('https://api.etadirect.com/rest/ofscCore/v1/resources/'+str(resource_id)+'/descendants', headers=headers, params=params)
    response_json=response.json()
    total_results=response_json['totalResults']
    items=response_json['items']
    final_items_list.extend(items)
    offset=response_json['offset']


print('NO  pending resources Total Results : {} - Offset : {}- List size {}'.format(total_results, offset, len(final_items_list)))
result_json = { 'items' :  final_items_list }
newJson= json.dumps(result_json,  indent=2, separators=(',', ': '))
with open(args.output_json, 'w') as json_file:
        json_file.write(newJson)
json_file.close()
csv_file = open(args.output_csv, 'w')
csv_file.write(fields+','+expand+'\n')
fieldsArray = fields.split(",")
expandArray = expand.split(",")


for item in final_items_list:
    line=''
    for field in fieldsArray:
        line=line+str(item[field])+','
    for expandName in expandArray:
        if expandName != '':
            if 'items' in item[expandName]:
                expandList=item[expandName]['items']
                lineExpand=''
                for expanditem in expandList:
                    lineExpand=lineExpand+str(expanditem['workSkill'])+'#'
                if ( lineExpand != '' ) :
                    line=line+lineExpand+','
    csv_file.write(line+"\n")
csv_file.close()
