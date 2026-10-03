# Cloud Backup System

A secure automated cloud backup system that transfers files from a Windows client to an Ubuntu backup server, creates encrypted backups using Restic, and stores them on Google Drive.

The system also provides a web-based Flask dashboard for managing backups, restoring files, viewing backup history, and monitoring backup operations.
## System Architecture

The Cloud Backup System consists of a Windows client, an Ubuntu backup server, Restic for encrypted backup management, Google Drive for cloud storage, and a Flask-based web dashboard.

```text
Windows Client
      |
      | SCP
      v
Ubuntu Backup Server
      |
      +-- Flask Dashboard
      +-- MySQL Database
      +-- Restic
      +-- Cron Scheduler
      |
      | rclone
      v
Google Drive
```

### Data Flow

1. Files are created or updated on the Windows client.
2. Windows Task Scheduler automatically transfers the files to the Ubuntu backup server using SCP.
3. Restic creates encrypted and deduplicated backup snapshots.
4. rclone provides access to the Google Drive storage.
5. Cron automatically runs the backup process at scheduled intervals.
6. The Flask dashboard allows administrators to perform backups, restore data, and view backup history.
7. MySQL stores application users and backup operation logs.
## Technologies Used

- **Windows Client** — source files and automated file transfer
- **Ubuntu Server** — backup server and system management
- **Python** — application and automation scripting
- **Flask** — web dashboard and backend
- **MySQL** — user accounts and backup operation logs
- **Restic** — encrypted, deduplicated backup and restore
- **rclone** — connection between Restic and Google Drive
- **Google Drive** — cloud backup storage
- **Cron** — scheduled backup automation
- **SCP / SSH** — secure file transfer and remote administration
- **HTML / CSS / JavaScript** — dashboard interface
