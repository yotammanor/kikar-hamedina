sudo pip install -r ../requirements/vps.txt
python manage.py migrate contenttypes 0001 --fake
python manage.py migrate contenttypes
python manage.py migrate --fake
sudo -u postgres psql -c "ALTER USER kikar WITH SUPERUSER"