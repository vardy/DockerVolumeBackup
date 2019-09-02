# DockerVolumeBackup

## Docker Image

Find the image in GitHub's package registry: https://github.com/vardy/DockerVolumeBackup/packages    
Image: `docker.pkg.github.com/vardy/dockervolumebackup/docker-volume-backup:{VERSION}`    
Edit the image name to include the desired version.

## Configuration

The host directory `/var/lib/docker/volumes/` must be mounted to the container directory `/HostVolumeData`.    
This is where DockerVolumeBackup looks for volume data.

**Provide the service with the following environment variables:**
```
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
```

You can find the exact names of the volumes to backup by listing your volumes with `docker volume ls`.

**Using in docker-compose:**

```yml
backup:
  image: docker.pkg.github.com/vardy/dockervolumebackup/docker-volume-backup:{VERSION}
  env_file:
   - .env
  volumes:
   - /var/lib/docker/volumes/:/HostVolumeData
```

## Deployment:

[GitHub Package Registry documentation](https://help.github.com/en/articles/configuring-docker-for-use-with-github-package-registry)

```
$ docker login -u {user} -p {token}
$ docker build -t docker.pkg.github.com/vardy/dockervolumebackup/docker-volume-backup:{VERSION} .
```

Replace version with latest release version.

## Todo:    
 - Add old backup cleanup
 - Check all S3 actions for success (returns true)
 - Upload image to DockerHub
 - Clean up s3 library and main file procedures
 - Pass about filestreams as file objects instead of temporary files