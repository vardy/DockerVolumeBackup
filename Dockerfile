FROM python:3

LABEL "com.github.actions.name"="DockerVolumeBackup"
LABEL "com.github.actions.description"="Automatically back up Docker volumes to S3 object storage."
LABEL "com.github.actions.icon"="mic"
LABEL "com.github.actions.color"="purple"

LABEL "repository"="https://github.com/vardy/DockerVolumeBackup/"
LABEL "homepage"="https://github.com/vardy/DockerVolumeBackup/"
LABEL "maintainer"="Jarred Vardy <jarred.vardy@gmail.com>"

WORKDIR /DockerVolumeBackup

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD [ "python3", "./src/main.py" ]