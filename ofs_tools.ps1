<###
### Maps current directory to /out in the container
###
### Example of use:
### ./ofs_tools.bat get_users.py --verbose 2 --output /out/users.csv
### ./ofs_tools.bat update_users.py --verbose 2 /out/modified_users.csv
### ./ofs_tools.bat get_resource_tree.py --verbose 2 --parent SUNRISE --output_csv /out/my_resources.csv
###
### Maps current directory to /out in the container
### so setting the output to /out/file.csv generates file.csv in the current directory

###
### local file .env.secret must contain credentials to access the environment:
### Template:
##
#>

docker rm ofsc_tools
docker run -i -v ${PWD}:/out --env-file .env.secret --name ofsc_tools ofsusers/ofsc_tools $MyInvocation.Line
