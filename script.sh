#!/bin/bash

export FLASK_APP=application.py
export FLASK_DEBUG=1
export DATABASE_URL="postgres://fajexobpqhvhxu:fcef71d1b5ed61537f4be01478ca5322864425cfe1d2f070208b2a697bb814d2@ec2-54-246-89-234.eu-west-1.compute.amazonaws.com:5432/d6ck7fhc7qo75t"

flask run
