#!/bin/bash

if [ -z "$1" ]; then
  PORT=8000
else
  PORT=$1
fi

python manage.py runserver $PORT