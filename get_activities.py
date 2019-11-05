from config import Config
import logging, json, pprint
import argparse
import time
import csv

from ofsc.core import OFSC, FULL_RESPONSE, JSON_RESPONSE

def init_script():
    # Parse arguments
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", type=int, choices = { 0, 1, 2, 3}, default = 1)
    parser.add_argument("--limit", type=int,  default = 10)
    parser.add_argument("--offset", type=int,  default = 0)
    parser.add_argument("--root", type=str, required=True)
    parser.add_argument("--dateFrom", type=str, required=True)
    parser.add_argument("--dateTo", type=str, required=True)
    parser.add_argument("--output", type=str, default = "output.csv")
    args = parser.parse_args()

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

def connectivity_test():
    logger.info("TEST 000: connectivity")
    response = instance.get_subscriptions(response_type=FULL_RESPONSE)
    logger.debug(pprint.pformat(response.text))
    logger.info("{}...Elapsed Time: {}".format(response.status_code, response.elapsed))
    return response.elapsed

def get_activities(root, initial_offset, limit, date_from, date_to):
    items = []
    logger.info("003: Retrieve all activities - include non-scheduled")
    hasMore = True
    offset = initial_offset
    while hasMore:
        request_params = {
            "dateFrom": date_from,
            "dateTo": date_to,
            "resources": root,
            "includeChildren": "all",
            #"includeNonScheduled": "true",
            #"q":"stateProvince=='MEX.'",
            "fields":"activityId,date,apptNumber,"+
                      "recordType,status,activityType,workZone,timeSlot,"+
                      "slaWindowStart,slaWindowEnd,serviceWindowStart,serviceWindowEnd,timeOfBooking,"+
                      "country_code,duration,travelTime,longitude,latitude,"+
                      "startTime",

            "offset" : offset,
            "limit": limit}
        response = instance.get_activities(response_type=FULL_RESPONSE, params=request_params)
        logger.debug(pprint.pformat(response.json()))
        logger.info("...{} Elapsed Time: {}".format(response.status_code,response.elapsed))
        response_body = response.json()
        if 'items' in response_body.keys():
            response_count = len(response_body['items'])
            items.extend(response_body['items'])
        else:
            response_count = 0
        if 'hasMore' in response_body.keys():
            hasMore = response_body['hasMore']
            logger.info("...Has More: {}  Offset: {} ".format(response_body['hasMore'], offset ))
            print ("{},{},{}".format(offset, response_count, response.elapsed))
        else:
            hasMore = False
            logger.info("...Offset: {} Limit: {}".format(offset, response_body['limit']))
            print ("{},{},{}".format(offset, response_count, response.elapsed))
        offset = offset + response_count
    return items

def write_csv(items, filename):
    csv_columns = items[0].keys()
    try:
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in items:
                writer.writerow(data)
    except IOError:
        print("I/O error")

init_script()
write_csv(get_activities(args.root, args.offset, args.limit, date_from=args.dateFrom, date_to=args.dateTo), filename = args.output)
