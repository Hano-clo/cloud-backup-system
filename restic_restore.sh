#!/bin/bash

LOCK_FILE="/tmp/cloud_backup.lock"

(
    flock -n 9 || {
        echo "Backup or restore already running. Skipping restore."
        exit 2
    }

    RESTIC_REPO="rclone:gdrive:CloudBackup/restic-repo"
    RESTORE_PATH="/home/hano/cloud-backup/restore_web"
    PASSWORD_FILE="/home/hano/.restic_password"

    echo "Starting Restic restore..."

    rm -rf "$RESTORE_PATH"
    mkdir -p "$RESTORE_PATH"

    restic -r "$RESTIC_REPO" \
        --password-file "$PASSWORD_FILE" \
        restore latest \
        --target "$RESTORE_PATH"

    if [ $? -eq 0 ]; then
        echo "Restore completed successfully."
    else
        echo "Restore failed."
        exit 1
    fi

) 9>"$LOCK_FILE"
