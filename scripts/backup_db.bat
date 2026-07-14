@echo off
setlocal

:: ATS PostgreSQL Backup Script
:: This script creates a daily backup of your ATS database.
:: You can schedule this using Windows Task Scheduler.

set "BACKUP_DIR=%~dp0..\data\backups"
set "TIMESTAMP=%date:~10,4%_%date:~4,2%_%date:~7,2%_%time:~0,2%%time:~3,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "BACKUP_FILE=%BACKUP_DIR%\ats_backup_%TIMESTAMP%.sql"

:: Ensure backup directory exists
if not exist "%BACKUP_DIR%" (
    mkdir "%BACKUP_DIR%"
)

echo Starting ATS Database Backup...
echo Destination: %BACKUP_FILE%

:: Run pg_dump inside the docker container
:: Note: The docker-compose command must be run from the project root.
pushd "%~dp0.."
docker compose exec -T postgres pg_dump -U ats_user ats_development > "%BACKUP_FILE%"
popd

if %errorlevel% equ 0 (
    echo Backup completed successfully!
) else (
    echo Backup failed! Please check docker status.
)

endlocal
