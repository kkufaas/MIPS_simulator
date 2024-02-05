#!/bin/bash

# Install dependencies, run tests, and sum score
python -m pip install -r ../requirements.txt -r ../test-requirements.txt
pytest -rPf
python3 sumresult.py
