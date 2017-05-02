import pytest
import datetime
import uuid
import json
import string
from random import randint, choice
from dateutil.parser import parse as date_parser
from pytest_mock import mocker
from emburse.client import Client, Account


@pytest.fixture(scope='module')
def emburse_client():
    return Client(auth_token='Testing123')


@pytest.fixture(scope='module')
def account_dict():
    return {
        "id": "64745919-0caf-4e6b-8e63-17e7a0d1035e",
        "url": "https://api.emburse.com/v1/accounts/64745919-0caf-4e6b-8e63-17e7a0d1035e.",
        "name": "Emburse Account for Acme Inc.",
        "number": "880307390512",
        "ledger_balance": 1258.43,
        "available_balance": 872.35,
        "created_at": "2015-09-12T17:05:03.058556Z"
    }


@pytest.fixture(scope='module')
def account_list():
    accounts = []
    while len(accounts) < 10:
        acc_id = str(uuid.uuid4())
        acc_num = []
        while len(acc_num) < 12:
            acc_num.append(str(randint(0, 9)))
        accounts.append(
            {
                "id": acc_id,
                "url": "https://api.emburse.com/v1/accounts/{0}".format(acc_id),
                "name": "The {0}-Team".format(choice(string.ascii_uppercase)),
                "number": "".join(acc_num),
                "ledger_balance": float('{0}.{1}'.format(randint(100, 999), randint(10, 99))),
                "available_balance": float('{0}.{1}'.format(randint(10, 99), randint(10, 99))),
                "created_at": datetime.datetime.utcnow().isoformat()
            }
        )
    return accounts


def test_account_details(mocker, emburse_client, account_dict):
    account = emburse_client.Account
    assert isinstance(account, Account)
    account.id = account_dict.get('id')
    mocker.patch.object(account, 'make_request')
    account.make_request.return_value = json.dumps(account_dict)
    account = account.refresh()
    assert isinstance(account, Account)
    assert isinstance(account.created_at, datetime.datetime)
    for key, value in account_dict.items():
        assert hasattr(account, key)
        if key == 'created_at':
            assert getattr(account, key) == date_parser(value)
        else:
            assert getattr(account, key) == value


def test_account_list(mocker, emburse_client, account_list):
    account = emburse_client.Account
    assert isinstance(account, Account)
    mocker.patch.object(account, 'make_request')
    account.make_request.return_value = json.dumps({'accounts': account_list})
    accounts = account.list()
    assert isinstance(accounts, list)
    assert len(accounts) == 10
    acc_ids = [x.get('id') for x in account_list]
    acc_names = [x.get('name') for x in account_list]
    for acc in accounts:
        assert isinstance(acc, Account)
        assert acc.id in acc_ids
        assert isinstance(acc.created_at, datetime.datetime)
        assert acc.name in acc_names
