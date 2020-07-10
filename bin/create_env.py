#!python
import os
import logging, json, pprint
import argparse
import time
import csv


def init_script():
    # Parse arguments
    global args
    global activity_fields 
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", type=int, choices = { 0, 1, 2, 3}, default = 1)
    parser.add_argument("input_file", type=str)
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


init_script()
env_vars = []
with open(args.input_file) as json_file:
    data = json.load(json_file)
    #Vars stored in data.values
    for var in data["values"]:
        env=""
        if var["key"] == "clientID": 
            env = "OFSC_CLIENT_ID"
        elif var["key"] == "companyName": 
            env = "OFSC_COMPANY"
            companyName = var["value"]
        elif var["key"] == "clientSecret": 
            env = "OFSC_CLIENT_SECRET"
        elif var["key"] == "rootResourceId": 
            env = "OFSC_ROOT"
        if env!="":
            logger.info ("{}={}".format(env, var["value"]))
            env_vars.append ("{}={}\n".format(env, var["value"]))

f = open("{}.env".format(companyName), "w")
for env_var in env_vars:
    f.writelines(env_var)
f.close()