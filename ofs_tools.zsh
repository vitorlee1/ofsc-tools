#! /bin/zsh
###
### Maps current directory to /out in the container
###
### Example of use (preloaded scripts):
### ./ofs_tools get_users.py --verbose 2 --output /out/users.csv
### ./ofs_tools update_users.py --verbose 2 /out/modified_users.csv
### ./ofs_tools get_resource_tree.py --verbose 2 --parent SUNRISE --output_csv /out/my_resources.csv
### ./ofs_tools /out/hello.py (runs a script in the current directory)

###
### local file .env.secret must contain credentials to access the environment:
### Template:
### 

docker rm ofsc_tools
docker run -i -v $PWD:/out --env-file .env.secret --name ofsc_tools ofsusers/ofsc_tools $*
