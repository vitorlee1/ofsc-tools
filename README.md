# ofsc-tools

```
get_activities.py [-h] [--verbose {0,1,2,3}] [--limit LIMIT]
                         [--offset OFFSET] --root ROOT --dateFrom DATEFROM
                         --dateTo DATETO [--output OUTPUT]

    offset: start with an offset (default is 0)
    root: ID of the root bucket used
    dateFrom:  starting date (format: yyyy-mm-dd)
    dateTo:  end date (format: yyyy-mm-dd)
    output: CSV file (default is output.csv

```
---
```

get_resource_tree.py [-h] --parent_resource PARENT_RESOURCE
                            [--fields FIELDS] [--output_json OUTPUT_JSON]
                            [--output_csv OUTPUT_CSV] [--verbose {0,1,2,3}]

Extract resource tree form OFSC instance

optional arguments:
  -h, --help            show this help message and exit
  --parent_resource PARENT_RESOURCE
                        Root resource to extract
  --fields FIELDS       Specify fields to extract
  --output_json OUTPUT_JSON
                        Output file for JSON format
  --output_csv OUTPUT_CSV
                        Outputfile for CSV format
  --verbose {0,1,2,3}   Additional messages. 0 is None, 3 is detailed debug```
---
```

get_routing_runs.py [-h] [--verbose {0,1,2,3}]
                           [--subscription SUBSCRIPTION] [--page PAGE]
                           [--since SINCE] [--limit LIMIT] [--output OUTPUT]
                           [--period PERIOD]

Routing event capture. Uses .env.secret file or .env file for credentials.
Will append to output file if it exists.

optional arguments:
  -h, --help            show this help message and exit
  --verbose {0,1,2,3}
  --subscription SUBSCRIPTION
  --page PAGE           initial page
  --since SINCE         Format: YYYY-MM-DD HH:MM
  --limit LIMIT         limit the number of loops. Default is 9999
  --output OUTPUT       Output file. Default is output-routing.csv
  --period PERIOD       Time in seconds between event reads. Default is 30



```
