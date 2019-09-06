# DockerVolumeBackup

[![Version](https://img.shields.io/github/v/tag/vardy/dockervolumebackup?label=version&style=flat-square)](https://github.com/vardy/DockerVolumeBackup/packages) [![Docker Pulls](https://img.shields.io/docker/pulls/pants1/docker-volume-backup?style=flat-square)](https://hub.docker.com/r/pants1/docker-volume-backup/) [![Docker Build](https://img.shields.io/docker/cloud/build/pants1/docker-volume-backup?style=flat-square)](https://hub.docker.com/r/pants1/docker-volume-backup/builds) [![License](https://img.shields.io/github/license/vardy/dockervolumebackup?style=flat-square)](https://github.com/vardy/DockerVolumeBackup/blob/master/LICENSE)

## Docker Image

On Docker Hub: https://hub.docker.com/r/pants1/docker-volume-backup
Image: `pants1/docker-volume-backup`    

## Configuration

The host directory `/var/lib/docker/volumes/` must be mounted to the container directory `/HostVolumeData`.    
This is where DockerVolumeBackup looks for volume data.

**Provide the service with the following environment variables:**
```Properties
# S3 Credentials
S3_Endpoint=https://example.com/
S3_Region=us-east
S3_Access_Key=abc
S3_Secret_Key=123
S3_Bucket_Name=bucky
S3_Directory_Name=backups

# List of volumes to backup, separated
# by commas
Volumes_To_Backup=db,web,api

# Interval for taking a backup snapshot (every x hours)
# Interval for which snapshot to keep permanently (every x snapshots)
# In this example, every 24 hours a permanent backup is saved,
# whilst every two hours a snapshot is overwritten.
snapshot_interval=2
backup_interval=12
backup_on_startup=yes

# Set what severity of log message to print to shell
Log_Level=INFO

# Disables the app
Disabled=no
```

You can find the exact names of the volumes to backup by listing your volumes with `docker volume ls`.

**Using in docker-compose:**

```yml
backup:
  image: pants1/docker-volume-backup
  env_file:
   - .env
  volumes:
   - /var/lib/docker/volumes/:/HostVolumeData
```

## Todo:    
 - Add testing
 - Add old backup cleanup
 - Clean up S3 library and main file procedures

## License

This project is licensed under the [GNU GPLv3](https://www.gnu.org/licenses/gpl.html).    
This license is copy-left and conducive to free, open-source software.

Project license: https://github.com/vardy/DockerVolumeBackup/blob/master/LICENSE  
License details: https://choosealicense.com/licenses/gpl-3.0/#