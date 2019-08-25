FROM python:3
MAINTAINER Jarred Vardy <jarred.vardy@gmail.com>

WORKDIR /DockerVolumeBackup

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD [ "python3", "./src/main.py" ]