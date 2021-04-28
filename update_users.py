#!python3
import csv
import ofsc
from ofsc import OFSC, FULL_RESPONSE, JSON_RESPONSE
import argparse, pprint, logging
from config import Config
import json

allowedFieldList =  ['login', 'status', 'language', 'languageISO', 'timeFormat', 'dateFormat', 'longDateFormat', 
                     'timeZoneDiff', 'timeZone', 'timeZoneIANA', 'createdTime', 'lastLoginTime', 'lastPasswordChangeTime', 
                     'organizationalUnit', 'lastUpdatedTime', 'weekStart', 'userType', 'name', 'resources', 'resourceInternalIds', 
                     'passwordTemporary', 'showPlaceholderId', 'selfAssignment']
def init_script():
    # Parse arguments
    global args
    parser = argparse.ArgumentParser(description="Extract resource tree form OFSC instance")
    parser.add_argument("input", type=str, help="Input for CSV format")
    parser.add_argument("--test", action='store_true', help="Do not commit the changes in the instance")
    parser.add_argument("--verbose", type=int, choices = { 0, 1, 2, 3}, default = 1, help = "Additional messages. 0 is None, 3 is detailed debug")
    args = parser.parse_args()

    global pp
    pp = pprint.PrettyPrinter(indent=4)

    # create logger
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logLevel = args.verbose
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if (args.test and logLevel < 2):
        logLevel = 2
        logger.warning("Test Mode: setting minimum verbose level to 2")

    logger.info("Starting execution: {}".format(logLevel))

    logger.setLevel(40 - 10*int(logLevel))
    logger.info("Log level is {}".format(logLevel))

    global instance
    instance = OFSC(clientID=Config.OFSC_CLIENT_ID, secret=Config.OFSC_CLIENT_SECRET, companyName=Config.OFSC_COMPANY)
    logger.info("Creating instance connection for {} {}".format(Config.OFSC_COMPANY, Config.OFSC_CLIENT_ID))


def clean_object(obj, fieldArray):
    for field in fieldArray:
        del obj[field]
    return obj

init_script()
logger.info( "* Allowed Fields: {}".format(allowedFieldList))
updateFields = []
extraFields = []
with open(args.input) as csvfile:
    reader = csv.DictReader(csvfile)
    haveFields= False

    for row in reader:
        logger.debug(pp.pformat(row))
        if not haveFields:
            logger.info( "* Fields submitted for update: {}".format(reader.fieldnames))
            haveFields=True
            for field in row.keys():
                if field in allowedFieldList:
                    logger.debug("{} OK".format(field))
                else:
                    extraFields.append(field)
                    logger.debug("{} KO".format(field))
            if extraFields:
                logger.warning("* Fields to discard: {}".format(extraFields))
        clean_row = clean_object(row, extraFields)
        logger.debug(pp.pformat(clean_row))  
        if not args.test:     
            raw_response = instance.update_user(clean_row["login"], json.dumps(clean_row), response_type=FULL_RESPONSE)
            if raw_response.status_code == 200:
                logger.debug(pp.pformat(raw_response.json()))
                logger.info("... Updated: {}".format(clean_row["login"]))
            else:
                logger.warning("...  Failed update: {} \n[ REASON {}]: ".format(clean_row["login"], raw_response.text))

