#!/bin/bash

LOCK_FILE="/tmp/cloud_backup.lock"

(
    flock -n 9 || {
        echo "Backup already running. Skipping this run."
        exit 0
    }

    RESTIC_REPO="rclone:gdrive:CloudBackup/restic-repo"
    BACKUP_SOURCE="/home/hano/cloud-backup/client_files"
    PASSWORD_FILE="/home/hano/.restic_password"

    echo "Starting Restic backup..."

    restic -r "$RESTIC_REPO" \
        --password-file "$PASSWORD_FILE" \
        backup "$BACKUP_SOURCE"

    if [ $? -eq 0 ]; then
        echo "Backup completed successfully."
    else
        echo "Backup failed."
        exit 1
    fi

) 9>"$LOCK_FILE"
