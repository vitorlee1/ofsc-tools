import logging, json, pprint
import argparse
import time
import pandas as pd 
import numpy as np

def init_script():
    #TODO Add option to start from an intermediate step
    # Parse arguments
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", type=int, help="Verbosity Level 0,1,2,3 (default is 1)",  choices = { 0, 1, 2, 3}, default = 1)
    parser.add_argument("--output", type=str, help="output file to be used (default is routing_output.csv) ", default = "routing_output.csv")
    parser.add_argument("--initial_stage",  type=int, help="Starting stage (choices are 1 (Filter), 2 (Enrich), 3 (Slice), 4 (Aggregate)", choices = {1,2,3,4}, default=1)
    parser.add_argument("--final_stage", type=int, help="Final stage (choices are 1 (Filter), 2 (Enrich), 3 (Slice), 4 (Aggregate)", choices = {1,2,3,4}, default=4)
    parser.add_argument("input_file",  nargs="+", help="CSV files to be processed")
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
    
    global autoRouted
    global nonTouched
    global filteredByType
    global anomalies
    autoRouted = 0
    nonTouched = 0
    filteredByType = 0 
    anomalies = 0

def show_header(activities):
    pd.set_option('display.max_columns', None)
    print(activities.head)

def load_activities():
    initialRecords = 0
    types = {"autoRoutedToDate": pd.StringDtype(), "firstManualOperation": pd.StringDtype()}

    logger.info("STEP 0: read input files")
    is_first = True
    for file in args.input_file:
        logger.info("... reading {}".format(file))
        if not is_first:
            temp_activities = pd.read_csv(file, dtype=types)
            activities = pd.concat([activities, temp_activities], axis=0)
        else:
            activities = pd.read_csv(file, dtype=types)
            is_first =False
    initialRecords = len(activities)
    logger.info("...Field Map: {}".format(activities.columns.values))
    logger.info("...Total activities: {}".format(initialRecords))
    activities["autoRoutedToDate"] = activities["autoRoutedToDate"].fillna(value = "")
    activities["firstManualOperation"] = activities["firstManualOperation"].fillna(value = "")
    return activities

def filter_activities(activities):
    # TODO: Set status as a category
    logger.info("STEP 1: filter records")
    filtered_activities = activities[((activities["status"]=="completed") | (activities["status"]=="notdone")) & (activities["workZone"].notnull())]

    totalActivities = len(filtered_activities)
    logger.info("...Total valid activities: {} ({} filtered by type)".format(totalActivities, filteredByType))
    return filtered_activities


def calculate_routing_class(row):
    try:
        if row["autoRoutedToDate"]!="":
            if row["firstManualOperation"]!="":
                return "Modified"
            else:
                return "Auto"
        else:
            if row["firstManualOperation"]!="":
                return "Preassigned"
            else:
                return "Anomaly"
    except (AttributeError, TypeError) as e:
        print("Error: {} ()".format(row, e))
        raise


def expand_activities(activities):
    logger.info("STEP 2: enrich records")
    activities["routingGroup"]  = activities.apply(calculate_routing_class, axis=1)
    activities["date"] = pd.to_datetime(activities["date"])
    activities["week"] = activities["date"].dt.week
    return activities


def slice_activities(activities):
    logger.info ("STEP 3: slice columns")
    selected_columns = ['week', 'apptNumber', 'activityType', 'workZone','timeSlot', 'travelTime', 'routingGroup']
    return activities[selected_columns]
    
def aggregate_data(activities):
    logger.info ("STEP 4: aggregate and pivot")
    dataset = activities.groupby(['week', 'routingGroup']).aggregate({ 'apptNumber': 'size'}).reset_index()
    # Pivot to create Routing Categories table
    dataset = pd.pivot_table(dataset, index="week", columns = "routingGroup", values="apptNumber", aggfunc=np.sum, fill_value=0)    
    return dataset

init_script()
dataset = load_activities()
stage = 1
if (stage >= args.initial_stage and stage <=args.final_stage):
    dataset = filter_activities(dataset)           # Remove unwanted records
else:
    logger.warning("Skippping STAGE 1 (Filtering)")
stage = 2
if (stage >= args.initial_stage and stage <=args.final_stage):
    dataset = expand_activities(dataset)  # Add extra columns
else:
    logger.warning("Skippping STAGE 2 (Enrichment)")
stage = 3
if (stage >= args.initial_stage and stage <=args.final_stage):
    dataset = slice_activities(dataset)     # Reduce the number of columns
else:
    logger.warning("Skippping STAGE 3 (Slicing)")
stage = 4
if (stage >= args.initial_stage and stage <=args.final_stage):
    dataset = aggregate_data(dataset)          # Aggregate and pivot data
else:
    logger.warning("Skippping STAGE 4 (Aggregation)")
dataset.to_csv(args.output)







