# ofsc-tools

```
get_activities.py [-h] [--verbose {0,1,2,3}] [--limit LIMIT]
                         [--offset OFFSET] --root ROOT --dateFrom DATEFROM
                         --dateTo DATETO [--output OUTPUT]

    offset: start with an offset (default is 0)

    root: ID of the root bucket used

    dateFrom:  starting date (format: yyyy-mm-dd)

    dateTo:  end date (format: yyyy-mm-dd)

    output: CSV file (default is output.csv)


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
