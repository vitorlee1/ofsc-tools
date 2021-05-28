#!python
import pandas as pd
import argparse
import json
import os,glob
import logging
import math



class Configuration(object):

    def __init__(self, dictionary):
        def _traverse(key, element):
            if isinstance(element, dict):
                return key, Configuration(element)
            else:
                return key, element

        objd = dict(_traverse(k, v) for k, v in dictionary.items())
        self.__dict__.update(objd)


def set_company_config(path):
    
    def _merge(a, b, path=None):
        "merges b into a"
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    _merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass # same leaf value
                else: # In case of conflict second wins
                    a[key] = b[key]
            else:
                a[key] = b[key]
        return a

    default_config = {
        "excludedProfiles" : [],
        "excludedOrgUnits" :  [],
        "allowedOrgUnitTypes" : []
    }

    # Load company specific configuration
    config_path = os.path.join(path, "config.json")
    if os.path.exists(config_path):
        print("... loading config: {}".format(config_path)) 
        with open(config_path) as json_file:
            loaded_config = json.load(json_file)
    else:
        print("... creating config: {}".format(config_path)) 
        loaded_config = json.loads("{}")
    new_config = _merge(default_config, loaded_config)
    return Configuration(new_config)

def load_resource_files(path):
    types = {
        "resourceInternalId": pd.Int32Dtype(),
        "parentResourceInternalId" : pd.Int32Dtype()
    }
    pattern = "res_*.csv"
    is_first = True
    for file in glob.glob(os.path.join(path, pattern)):
        if not is_first:
            tmp_resources = pd.read_csv(file, dtype=types).set_index("resourceInternalId")
            resources = pd.concat([tmp_resources, resources], axis = 0)
        else:
            resources = pd.read_csv(file, dtype=types).set_index("resourceInternalId")
            is_first = False
    resources.sort_values(by="resourceInternalId")
    return resources

def init_script():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", type=int, choices = { 0, 1, 2, 3}, default = 1)
    parser.add_argument("--dir", type=str, default = "/out")
    parser.add_argument("--input", type=str, default = "users.csv")
    parser.add_argument("--output", type=str, default = "modified_users.csv")
    parser.add_argument("--exclude_multiple_resources", help = "Don't modify users with multiple resources", action = 'store_true')
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
    logger.info("Options:")
    logger.info(f"- Excluding users with multiple resources: {args.exclude_multiple_resources}")

def isValidOrgUnit(resourceId):
    global resources,config
    try:
        if (resourceId in resources.index.values) and (resources.loc[resourceId]["resourceType"] in config.allowedOrgUnitTypes) and (resourceId not in config.excludedOrgUnits):
            return True
    except:
        logger.error(f'Error in isValidOrgUnit: ({resourceId})')
    return False

def getMainResource(row):
    index=0
    while index < len(row["resourceInternalIds"]):
        if isValidOrgUnit(row["resourceInternalIds"][index]):
            break
        else:
            index = index + 1
    if index < len(row["resourceInternalIds"]):
        return [row["resources"][index],len(row["resources"])]
    else:
        return ["", len(row["resources"])]

def show_stats(data):
    global logger
    logger.info ("    - Users with organizationalUnit != mainResource: {}".format (data[data["organizationalUnit"]!= data["suggestedOrgUnit"]].shape[0]))
    logger.info ("    - Users with organizationalUnit empty: {}".format (data[data["organizationalUnit"].isna()].shape[0]))
    logger.info ("    - Users with more than one resource: {}".format (data[data["resourceCount"]>1].shape[0]))

def markUsers(row):
    global args
    logger.debug("{} - {} ".format(row["organizationalUnit"],type(row["organizationalUnit"])))
    if (args.exclude_multiple_resources and row["resourceCount"] > 1):
        # Don't modify users with multiple resources if flag is on
        return False
    if isinstance(row["organizationalUnit"], str):
        # Don't modify users with existing organizationalUnit
        return False
    elif len(row["suggestedOrgUnit"])>0 and math.isnan(row["organizationalUnit"]):
        # Allow modification when there was no organizationalUnit and there is a suggested OrganizationalUnit
        return True
    else:
        return False
    



init_script()

input_file = os.path.join(args.dir, args.input)
output_file = os.path.join(args.dir, args.output)
config = set_company_config(args.dir)
logger.info(f"Loaded configuration: {json.dumps(config.__dict__, indent=4)}")

extended_output_file = os.path.join(args.dir, "extended_{}".format(args.output))    

logger.info(f"Input file: {input_file}  Output file: {output_file}")

# STEP 0 - Load 

## Read data file
logger.info ("STEP 0 - Loading users")
df = pd.read_csv(input_file)
df["resources"] = df["resources"].apply(eval)
df["resourceInternalIds"] = df["resourceInternalIds"].apply(eval)
resources = load_resource_files(args.dir)

# STEP 1: Filter resources

logger.info ("STEP 1 - Filtering")
logger.info ("...Removing inactive users: {}".format(df[df["status"]!= "active"].shape[0]))
df.drop(df[df['status'] != "active"].index, inplace = True)
logger.info  (f"...Users remaining: {df.shape[0]}")

logger.info("...Removing excluded profiles: {}".format(df[df['userType'].isin(config.excludedProfiles)].shape[0]))
df.drop(df[df['userType'].isin(config.excludedProfiles)].index, inplace=True)
logger.info  (f"...Users remaining: {df.shape[0]}")
df.to_csv("step_1.csv")

# STEP 2 - Modify Organizational Unit

logger.info("STEP 2 - Identifying users to modify")

## Calculate main resource
df[["suggestedOrgUnit", "resourceCount"]] = df.apply(getMainResource, axis=1, result_type='expand')
logger.info(f"...Loaded {df.shape[0]} users... ")
show_stats(df)

## Mark users that can be modified
df["modified"]  = df.apply(markUsers, axis=1)
df.organizationalUnit.fillna(df.suggestedOrgUnit, inplace=True)
logger.info("... Modified: {} users".format(df[df["modified"]].shape[0]))
show_stats(df)

# STEP 3 - Write output

logger.info("STEP 3 - Writing output")
df[df["modified"]][["login", "organizationalUnit"]].to_csv(output_file, index=False)
df[["login", "organizationalUnit", "suggestedOrgUnit", "resources", "resourceCount", "userType", "modified"]].to_csv(extended_output_file, index=False)