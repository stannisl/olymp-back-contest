#!/usr/bin/env bash
python3 -m flask db upgrade
python3 -m flask run --host=0.0.0.0 --port=$SERVER_PORT