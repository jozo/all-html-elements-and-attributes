FROM python:3.9-slim

# the code is copied into the container just to make the pip install command work
# then it will be replaced by the volume defined in our docker-compose.yml
COPY ./ /code

WORKDIR /code

RUN pip install -r requirements.txt