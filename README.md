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

get_resource_tree.py [--output_json  FILE_JSON_OUTPUT ] [--output_csv FILE_CSV_OUTPUT]
                    --instance --clientID --secret --parent_resource -- fields
    output_json: json output file ( default is result.json )
    output_csv: csv output file  ( default is result.csv )
    instance:  instance name
    clientID:  client ID
    secret: secret
    parent_resource : external ID of the parent resource
    fields : fields to include on the response ( default is resourceId,resourceType,parentResourceId,status)
```
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

