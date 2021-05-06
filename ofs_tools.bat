REM
REM Maps current directory to /out in the container
REM
REM Example of use:
REM .\ofs_tools.bat get_users.py --verbose 2 --output /out/users.csv
REM .\ofs_tools.bat update_users.py --verbose 2 /out/modified_users.csv
REM .\ofs_tools.bat get_resource_tree.py --verbose 2 --parent SUNRISE --output_csv /out/my_resources.csv
REM
REM Maps current directory to /out in the container
REM so setting the output to /out/file.csv generates file.csv in the current directory

REM
REM local file env.secret must contain credentials to access the environment with this format :
REM OFSC_CLIENT_ID=cliente_id
REM OFSC_CLIENT_SECRET=client_secret
REM OFSC_COMPANY=company
REM OFSC_ROOT=root_bucket
REM
REM Template:
REM

set mypath=%cd%
docker rm ofsc_tools
docker run -i -v %mypath%:/out --env-file env.secret --name ofsc_tools ofsusers/ofsc_tools %*

