#!python3
import csv
import ofsc
from ofsc import OFSC, FULL_RESPONSE, JSON_RESPONSE
import argparse, pprint, logging
from config import Config
import json
import pandas as pd

allowedFields =  {'login', 'status', 'language', 'languageISO', 'timeFormat', 'dateFormat', 'longDateFormat', 
                     'timeZoneDiff', 'timeZone', 'timeZoneIANA', 'createdTime', 'lastLoginTime', 'lastPasswordChangeTime', 
                     'organizationalUnit', 'lastUpdatedTime', 'weekStart', 'userType', 'name', 'resources', 'resourceInternalIds', 
                     'passwordTemporary', 'showPlaceholderId', 'selfAssignment'}

mandatoryFields = {'login', 'name', 'userType', 'language', 'timeZone'}
def init_script():
    # Parse arguments
    global args
    parser = argparse.ArgumentParser(description="Create users")
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



def process_row(row):   
    logger.debug(row.to_json())
    if not args.test:     
        raw_response = instance.create_user(row["login"], row.to_json(), response_type=FULL_RESPONSE)
        if raw_response.status_code == 200:
            logger.debug(pp.pformat(raw_response.json()))
            logger.info("... Created: {}".format(row["login"]))
        else:
            logger.warning("...  Failed creation: {} \n[ REASON {}]: ".format(row["login"], raw_response.text))

def clean_object(obj, fieldArray):
    for field in fieldArray:
        del obj[field]
    return obj

init_script()
logger.info( "* Allowed Fields: {}".format(allowedFields))
updateFields = []
extraFields = []
dataset = pd.read_csv(args.input)

# Analyze Headers
submittedFields = set(dataset.columns)
logger.info( f"* Fields submitted for creation: {submittedFields}")
extraFields = submittedFields - allowedFields
logger.info( f"* Fields to discard: {extraFields}")
logger.info( f"* Fields not included: {mandatoryFields - submittedFields}")
if 'resourceInternalIds'in submittedFields:
    dataset['resourceInternalIds'] = dataset['resourceInternalIds'].apply(eval)
    if 'resources' in submittedFields:
        extraFields.add('resources')
else:
    if 'resources' in submittedFields:
        dataset['resources'] = dataset['resources'].apply(eval)
if extraFields:
    logger.warning("* Fields to discard: {}".format(extraFields))
    dataset.drop(columns=extraFields, inplace=True)

# Apply changes
dataset.apply(process_row, axis=1)

