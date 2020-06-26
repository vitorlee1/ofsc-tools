#!python
import os, sys,json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
import datetime, calendar
import logging, argparse
from calendar import monthrange

# TODO : Check than env vars are set
def init_script():
    #TODO Add option to start from an intermediate step
    # Parse arguments
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", type=int, help="Verbosity Level 0,1,2,3 (default is 1)",  choices = { 0, 1, 2, 3}, default = 1)
    parser.add_argument("--months", type=int, help="Months of info to download (default is last 4)", choices = { 1, 2, 3, 4}, default = 4)
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
# Generate Company Files
os.system("echo =============================================================================")
os.system("echo Generating last {} monthly activity files for company {}".format (args.months, Config.OFSC_COMPANY))
os.system("echo =============================================================================")
current_month = datetime.datetime.now().month
for i in range(current_month-args.months+1,current_month+1):
    dmonth = i
    dyear= 2020
    smonth="{}-{:02}".format(dyear, dmonth)
    start_day=1
    end_day=calendar.monthrange(dyear, dmonth)[1]
    dfrom="{}-{:02}".format(smonth, start_day)
    dto="{}-{:02}".format(smonth, end_day)
    dfile="{}-{}".format(Config.OFSC_COMPANY, smonth)
    os.system("python ../get_activities.py --verbose {} --root={} --dateFrom={} --dateTo={} --output {}.csv --routing --limit 5000".format(args.verbose, Config.OFSC_ROOT, dfrom, dto,dfile))

# Create aggregated table
os.system("echo =============================================================================")
os.system("echo Generating aggregated info")
os.system("echo =============================================================================")
os.system("python aggregate_data.py --verbose {} {}*.csv".format(args.verbose, Config.OFSC_COMPANY))

# Generate report
os.system("echo =============================================================================")
os.system("echo Creating excel report")
os.system("echo =============================================================================")
os.system("python create_report.py --verbose {} --output {}.xlsx".format(args.verbose, Config.OFSC_COMPANY))



