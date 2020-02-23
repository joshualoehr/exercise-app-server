#!/bin/bash
export JWT_PRIVATE_KEY=$(cat ~/.ssh/liftjl_rsa)
export JWT_PUBLIC_KEY=$(cat ~/.ssh/liftjl_rsa.pub)

python3 manage.py create_db
python3 manage.py db init
python3 manage.py db migrate
python3 manage.py db upgrade
flask run --host 0.0.0.0