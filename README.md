# DockerVolumeBackup

Todo:    
 - Add system for how long to keep old backups
 - Add options for verbosity (file upload progress in stdout) (logging levels)
 - Check all S3 actions for success (returns true)
 - Document setup process
 - Upload image to DockerHub
 - Is it safe to terminate at any point in the process? (use atexit?)
 - Add 'snapshot' and 'backup' prefixes to backups and snapshots
 - 'Cleanup' and 'Compress' functionality that checks whether there are no new 
 changes in a backup and compresses if there are none