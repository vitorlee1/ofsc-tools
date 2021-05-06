#! /bin/zsh
###
### Maps current directory to /out in the container
###
### Example of use:
### ./ofs_data_science get_users.py --verbose 2 --output /out/users.csv
### ./ofs_data_science update_users.py --verbose 2 /out/modified_users.csv
### ./ofs_data_science get_resource_tree.py --verbose 2 --parent SUNRISE --output_csv /out/my_resources.csv

###
### local file .env.secret must contain credentials to access the environment:
### Template:
### 

docker rm ofsc_data_science
docker run -d -v $PWD/data_science:/home/jovyan/work --env-file .env.secret --name ofsc_data_science -p 10000:10000 jupyter/datascience-notebook start.sh jupyter lab --no-browser --allow-root --no-browser --port 10000
