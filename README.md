
# swc-platform-assignment
This repository is based on the Platform assignment outlined in ASSIGNMENT.md.

## Pre-requirements
- python
- python-venv
- Docker

## Getting start

### Set the AWS credential
```
$ export AWS_ACCESS_KEY_ID="<YOUR_AWS_ACCESS_KEY_ID>"
$ export AWS_SECRET_ACCESS_KEY="<YOUR_AWS_SECRET_ACCESS_KEY>"
```

### Run the CDK project
```
$ python3 -m venv .venv
```
```
$ source .venv/bin/activate
```
```
$ pip install -r requirements.txt
```
```
$ cdk deploy --all
```

### Test
```
$ pytest tests/test_lambda_values.py
```

## Screenshots
Relevant screenshots related to the infrastructure setup can be found in the /assets/screenshots directory.
