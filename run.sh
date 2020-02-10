#!/bin/bash
export FLASK_APP=server
export FLASK_ENV=development
pip install -e .
flask run