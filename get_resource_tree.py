import json, csv
import argparse, pprint, logging
from config import Config
from ofsc.core import OFSC, FULL_RESPONSE, JSON_RESPONSE

parser = argparse.ArgumentParser()

def init_script():
    # Parse arguments
    global args
    parser.add_argument("--verbose", type=int, choices = { 0, 1, 2, 3}, default = 1)
    parser.add_argument("--output_json", type=str, default="result.json")
    parser.add_argument("--output_csv", type=str, default="result.csv")
    # parser.add_argument("--instance", type=str, required=True)
    # parser.add_argument("--clientID", type=str, required=True)
    # parser.add_argument("--secret", type=str, required=True)
    parser.add_argument("--parent_resource", type=str, required=True)
    parser.add_argument("--fields", type=str,  default=None)
    args = parser.parse_args()

    global pp
    pp = pprint.PrettyPrinter(indent=4)

    # create logger
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info("Starting execution: {}".format(args.verbose))
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(40 - 10*int(args.verbose))
    logger.info("Log level is {}".format(args.verbose))

    global instance
    instance = OFSC(clientID=Config.OFSC_CLIENT_ID, secret=Config.OFSC_CLIENT_SECRET, companyName=Config.OFSC_COMPANY)
    logger.info("Creating instance connection for {} {}".format(Config.OFSC_COMPANY, Config.OFSC_CLIENT_ID))




init_script()
fields=args.fields
response = instance.get_resource_descendants(args.parent_resource, offset=0, resourceFields=fields, response_type=JSON_RESPONSE)
logger.debug(pp.pformat(response))
total_results=response['totalResults']
offset=response['offset']
final_items_list=response['items']


while offset + 100 < total_results :
    logger.info('Still pending resources Total Results : {} - Offset : {} - List size {}'.format(total_results, offset, len(final_items_list) ))
    offset=offset+100
    response_json = instance.get_resource_descendants(args.parent_resource, offset=offset, resourceFields=fields, response_type=JSON_RESPONSE)
    logger.debug(pp.pformat(response))
    total_results=response_json['totalResults']
    items=response_json['items']
    final_items_list.extend(items)
    offset=response_json['offset']


logger.info('NO  pending resources Total Results : {} - Offset : {}- List size {}'.format(total_results, offset, len(final_items_list)))
result_json = { 'items' :  final_items_list }
newJson= json.dumps(result_json,  indent=2, separators=(',', ': '))
with open(args.output_json, 'w') as json_file:
        json_file.write(newJson)
json_file.close()

outputFile = open(args.output_csv, 'w')
fieldList = final_items_list[0]
del fieldList["workSkills"]
del fieldList["workZones"]
del fieldList["workSchedules"]
del fieldList["inventories"]
del fieldList["links"]
del fieldList["users"]
output = csv.DictWriter(outputFile, fieldList.keys(), extrasaction='ignore')
output.writeheader()
for item in final_items_list:
    output.writerow(item)
outputFile.close()
