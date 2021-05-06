FROM python:3.8-slim
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY config.py .
COPY get_users.py .
COPY update_users.py .
COPY get_activities.py .
COPY get_resource_tree.py .
COPY fix_users_ou.py .
ENTRYPOINT ["python3"] 

