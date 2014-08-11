# take a backup of Database using pg_dump
# replace the postgres with Database username and the dbname with the Database name
# save it to a tar file
export PGPUSER="kikar"
export PGPASSWORD="kikar"
pg_dump --username=kikar -h localhost kikar > $(date "+%Y%m%d-db-backup")
gzip $(date "+%Y%m%d-db-backup")
# upload the DB backup to Dropbox
python upload_backup_to_dropbox.py
rm $(date --date="yesterday" "+%Y%m%d-db-backup.gz")

#To resotre run this command with <newdbname> and <filename> supplemented.
# <filename> must be accessible
# <newdbname> must be entirely empty
# pg_restore --dbname=<newdbname> --verbose <filename>.tar
