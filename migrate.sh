if [ -n "$1" ]; then
    python manage.py makemigrations $1
    python manage.py migrate $1
else
    python manage.py makemigrations
    python manage.py migrate
fi
