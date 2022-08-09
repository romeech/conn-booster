# conn-booster
A utility to fill a CloudBlue Connect instance with auto-generated data.

## Installation
```
git clone git@github.com:romeech/conn-booster.git

cd conn-booster

virtualenv venv

source venv/bin/activate

pip install -r requirements.txt 
```

## Examples
Submit several purchase requests:

```python connboost.py -a https://connect.local/public/v1 -t "ApiKey ..." purchase```
