#!python
import logging, json, pprint as pp, os
import argparse, requests
from dotenv import load_dotenv
from  urllib import parse

POSTMAN_URL = 'https://api.getpostman.com/'

def init_script():
    # Parse arguments
    global args
    global headers
    headers = {}
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", type=int, choices = { 0, 1, 2, 3}, default = 1)
    parser.add_argument("--environment", type=str)
    parser.add_argument("--all", help="Extract all environments", action='store_true')
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

    load_dotenv(os.path.join(os.environ['OFSC_ENV_REPOSITORY'], 'postman.key'))
    key=os.environ.get('POSTMAN_KEY')
    headers["X-API-Key"] = os.environ.get('POSTMAN_KEY')

environment_dict = {}
def get_environments():
    response = requests.get(parse.urljoin(POSTMAN_URL, "environments"), headers=headers)
    environment_list = response.json()
    for env in (environment_list["environments"]):
        environment_dict[env["name"]] =env

def get_environment(uid):
    logger.debug("Getting info for environment {}".format(uid))
    response = requests.get(parse.urljoin(POSTMAN_URL, "environments/{}".format(uid)), headers=headers)
    logger.debug(response.url)
    environment_info = response.json()
    return environment_info


def store_environment(data):
    #Vars stored in data.values
    env_vars=[]
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
    f = open("{}.secret".format(companyName), "w")
    for env_var in env_vars:
        f.writelines(env_var)
    f.close()
    logger.info("Generated {}.secret".format(companyName))


init_script()
get_environments()
if args.environment:
    logger.debug (environment_dict[args.environment])
    logger.debug (environment_dict[args.environment]["uid"])
    info = get_environment(environment_dict[args.environment]["uid"])
    logger.debug (info)
    store_environment(info["environment"])
elif args.all:
    for env in environment_dict.keys():
        try:
            logger.info("Extracting environment {}".format(env))
            info = get_environment(environment_dict[env]["uid"])
            logger.debug (info)
            store_environment(info["environment"])
        except UnboundLocalError as inst:
            logger.warning("{}: {}".format(env, inst))
else:
    logger.warning("No option was provided. See --help")





