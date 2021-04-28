#!python
import csv
import ofsc
from ofsc import OFSC, FULL_RESPONSE, JSON_RESPONSE
import argparse, pprint, logging
from config import Config

def init_script():
    # Parse arguments
    global args
    parser = argparse.ArgumentParser(description="Extract resource tree form OFSC instance")
    parser.add_argument("--output_csv", type=str, default="result.csv" ,help="Outputfile for CSV format")
    parser.add_argument("--verbose", type=int, choices = { 0, 1, 2, 3}, default = 1, help = "Additional messages. 0 is None, 3 is detailed debug")
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
response = instance.get_users( offset=0, response_type=JSON_RESPONSE)
logger.debug(pp.pformat(response))
total_results=response['totalResults']
offset=response['offset']
final_items_list=response['items']


while offset + 100 < total_results :
    logger.info('Still pending users Total Results : {} - Offset : {} - List size {}'.format(total_results, offset, len(final_items_list) ))
    offset=offset+100
    response_json = instance.get_users(offset=offset, response_type=JSON_RESPONSE)
    logger.debug(pp.pformat(response))
    total_results=response_json['totalResults']
    items=response_json['items']
    final_items_list.extend(items)
    offset=response_json['offset']

outputFile = open(args.output_csv, 'w')
fieldList = final_items_list[0]
del fieldList["links"]
del fieldList["collaborationGroups"]
output = csv.DictWriter(outputFile, fieldList.keys(), quoting=csv.QUOTE_NONNUMERIC, extrasaction='ignore')
output.writeheader()
for item in final_items_list:
    output.writerow(item)
outputFile.close()
