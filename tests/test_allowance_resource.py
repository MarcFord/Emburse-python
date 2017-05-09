import pytest
import datetime
import uuid
from dateutil.parser import parse as date_parser
from random import randint, choice
from pytest_mock import mocker
from emburse.client import Client, Allowance


@pytest.fixture(scope='module')
def emburse_client():
    return Client(auth_token='Testing123')


@pytest.fixture(scope='module')
def allowance_dict():
    return {
        "id": "22f6fe8f-ff91-473c-86ef-a6e8480508bb",
        "url": "https://api.emburse.com/v1/allowances/22f6fe8f-ff91-473c-86ef-a6e8480508bb",
        "interval": "weekly",
        "amount": 500.0,
        "usage_limit": 'null',
        "transaction_limit": 150.0,
        "daily_limit": 'null',
        "end_time": "2016-08-28T00:00:00Z",
        "scope": [6],
        "balance": 437.27,
        "uses_remaining": 'null',
        "created_at": "2016-08-20T00:24:46.609518Z"
    }


@pytest.fixture(scope='module')
def allowance_list():
    allowances = []
    while len(allowances) < 10:
        allow_id = str(uuid.uuid4())
        allowances.append(
            {
                "id": allow_id,
                "url": "https://api.emburse.com/v1/allowances/{0}".format(allow_id),
                "interval": choice(["weekly", 'daily', 'monthly']),
                "amount": float('{0}.{1}'.format(randint(1000, 9999), randint(10, 99))),
                "usage_limit": 'null',
                "transaction_limit": float('{0}.{1}'.format(randint(10, 99), randint(10, 99))),
                "daily_limit": 'null',
                "end_time": (datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat(),
                "scope": [randint(1, 9)],
                "balance": float('{0}.{1}'.format(randint(100, 999), randint(10, 99))),
                "uses_remaining": 'null',
                "created_at": datetime.datetime.utcnow().isoformat()
            }
        )
    return allowances


def test_allowance_details(mocker, emburse_client, allowance_dict):
    allowance = emburse_client.Allowance
    assert isinstance(allowance, Allowance)
    allowance.id = allowance_dict.get('id')
    mocker.patch.object(allowance, 'make_request')
    allowance.make_request.return_value = allowance_dict
    allowance = allowance.refresh()
    assert isinstance(allowance, Allowance)
    assert isinstance(allowance.created_at, datetime.datetime)
    assert isinstance(allowance.end_time, datetime.datetime)
    for key, value in allowance_dict.items():
        assert hasattr(allowance, key)
        if key == 'created_at' or key == 'end_time':
            assert getattr(allowance, key) == date_parser(value)
        else:
            assert getattr(allowance, key) == value


def test_allowance_list(mocker, emburse_client, allowance_list):
    allowance = emburse_client.Allowance
    assert isinstance(allowance, Allowance)
    mocker.patch.object(allowance, 'make_request')
    allowance.make_request.return_value = {'allowances': allowance_list}
    allowances = allowance.list()
    assert isinstance(allowances, list)
    assert len(allowances) == 10
    for allow in allowances:
        assert isinstance(allow, Allowance)
        allow_dict = list(filter(lambda a: a.get('id') == allow.id, allowance_list)).pop()
        for key, value in allow_dict.items():
            assert hasattr(allow, key)
            if key == 'created_at' or key == 'end_time':
                assert getattr(allow, key) == date_parser(value)
            else:
                assert getattr(allow, key) == value
