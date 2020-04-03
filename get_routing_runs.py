#!python

from config import Config
import logging, json, pprint, os.path
import argparse
import time
import csv

from ofsc.core import OFSC, FULL_RESPONSE, JSON_RESPONSE

# Based on Events v1:
routing_events_header_text = "time,user,routingPlan,routingPlanId,result,startType,type,resourceId,routingRunId,targetDate,numberOfDays,routingProfile,routingProfileId,routingRunDuration,activitiesMatched,activitiesRouted,activitiesNotRouted,resourcesMatched,resourcesUsed,averageWorkingTime,averageOverTime,averageTravelTime,averageDownTime"
routing_events_headers = routing_events_header_text.split(",")

def init_script():
    # Parse arguments
    global args
    parser = argparse.ArgumentParser(description="Routing event capture. Uses .env.secret file or .env file for credentials. Will append to output file if it exists.")
    parser.add_argument("--verbose", type=int, choices = { 0, 1, 2, 3}, default = 1)
    parser.add_argument("--subscription", type=str)
    parser.add_argument("--page", type=str, help="initial page")
    parser.add_argument("--since", type=str, help="Format: YYYY-MM-DD HH:MM")
    parser.add_argument("--limit", type=int, default = 9999, help = "limit the number of loops. Default is 9999")
    parser.add_argument("--output", type=str, default = "output-routing.csv", help="Output file. Default is output-routing.csv")
    parser.add_argument("--period", type =int, default=30, help="Time in seconds between event reads. Default is 30")
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

    global subscription,page
    # if the subscrioption data is not provided, create connection
    if not args.subscription:
        data = {
            "events" : ["routingRun"],
            "title"  : "Simple Subscription"
        }
        response = instance.create_subscription(json.dumps(data), FULL_RESPONSE)
        if response.status_code == 200:
            subscription = response.json()["subscriptionId"]
            page = response.json()["nextPage"]
            logger.warning("Created subscription {}".format(subscription))
        else:
            logging.error("ERROR: {}".format(response.json()))
            exit(-1)
    else:
        subscription = args.subscription
        if args.page:
            page = args.page
        else:
            if args.since:
                since = args.since
            else:
                since = "2020-01-01 00:00"
            params = {
                'subscriptionId' : subscription,
                'since' : since
            }
            response = instance.get_events(params, FULL_RESPONSE)
            if response.status_code == 200:
                page = response.json()["nextPage"]
            else:
                logging.error("ERROR: {}".format(response.json()))
                exit(-1)


def collect_routing_events():
    global subscription, page, pp, args
    if os.path.isfile(args.output):
        outputFile = open(args.output, 'a')
        add_headers = False
    else:
        outputFile = open(args.output, 'w')
        add_headers = True
    output = csv.DictWriter(outputFile, routing_events_headers) #create a csv.write

    nextPage = page
    count = 0
    while(count<args.limit):
        logger.debug("Getting events: Page {} ".format(nextPage))
        params = {
            'subscriptionId' : subscription,
            'page' : nextPage
        }
        raw_response = instance.get_events(params)
        response = json.loads(raw_response)
        logger.debug(pp.pformat(response))
        for item in response['items']:
            logger.info(pp.pformat(item['eventType']))
            if item['eventType'] == 'routingRun':
                run = item['routingRunDetails']
                run['time'] = item['time']
                run['user'] = item['user']
                if add_headers:
                    output.writeheader()  # header row
                    add_headers= False
                output.writerow(run)
                logger.info(pp.pformat(item))

        if nextPage == response['nextPage']:
            time.sleep(args.period)
        else:
            nextPage = response['nextPage']
            time.sleep(1)
        count+=1




init_script()
collect_routing_events()
