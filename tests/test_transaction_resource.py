import pytest
import datetime
import uuid
import json
from random import randint
from pytest_mock import mocker
from emburse.client import Client, Transaction, Card, Member, Category


@pytest.fixture(scope='module')
def emburse_client():
    return Client(auth_token='Testing123')


@pytest.fixture(scope='module')
def transaction_dict():
    return {
        "id": "0849b836-bc20-4a83-8218-e50f8c9e56c4",
        "url": "https://api.emburse.com/v1/transactions/0849b836-bc20-4a83-8218-e50f8c9e56c4",
        "amount": -119.21,
        "state": "pending",
        "vendor": {
            "mid": 445201094999,
            "mcc": 7311,
            "name": "ADROLL",
            "address": 'null',
            "city": "SAN FRANCISCO",
            "state": "CA",
            "zip_code": "94103"
        },
        "card": {
            "id": "c195f95f-42ea-42b9-bf62-25ea0995a9a4",
            "url": "https://api.emburse.com/v1/cards/c195f95f-42ea-42b9-bf62-25ea0995a9a4",
            "state": "active",
            "description": "Advertising",
            "last_four": "7640"
        },
        "member": {
            "id": "d8ef8d51-8c48-4da7-8758-a7b578a4d360",
            "url": "https://api.emburse.com/v1/member/d8ef8d51-8c48-4da7-8758-a7b578a4d360",
            "email": "justin@example.com",
            "first_name": "Justin",
            "last_name": "Jones"
        },
        "category": {
            "id": "c66b60c5-449c-4482-ac66-e3c5557f4b49",
            "url": "https://api.emburse.com/v1/category/c66b60c5-449c-4482-ac66-e3c5557f4b49",
            "code": 'null',
            "name": "Sales & Marketing"
        },
        "department": 'null',
        "label": 'null',
        "location": 'null',
        "receipt": 'null',
        "note": "",
        "time": "2016-08-19T04:02:05Z",
        "created_at": "2016-08-19T04:02:07.016369Z"
    }


@pytest.fixture(scope='module')
def transaction_list():
    transactions = []
    while len(transactions) < 10:
        trans_id = str(uuid.uuid4())
        card_id = str(uuid.uuid4())
        transactions.append(
            {
                "id": trans_id,
                "url": "https://api.emburse.com/v1/transactions/{0}".format(trans_id),
                "amount": float('{0}.{1}'.format(randint(1, 100), randint(1, 10))),
                "state": "pending",
                "vendor": {
                    "mid": randint(100000000000, 999999999999),
                    "mcc": randint(1000, 9999),
                    "name": "ADROLL",
                    "address": 'null',
                    "city": "SAN FRANCISCO",
                    "state": "CA",
                    "zip_code": "94103"
                },
                "card": {
                    "id": card_id,
                    "url": "https://api.emburse.com/v1/cards/{0}".format(card_id),
                    "state": "active",
                    "description": "Advertising",
                    "last_four": "{0}{1}{2}{3}".format(
                        randint(0, 9),
                        randint(0, 9),
                        randint(0, 9),
                        randint(0, 9)
                    )
                },
                "department": 'null',
                "label": 'null',
                "location": 'null',
                "receipt": 'null',
                "note": "",
                "time": datetime.datetime.utcnow().isoformat(),
                "created_at": datetime.datetime.utcnow().isoformat()
            }
        )
    return transactions


def test_department_details(mocker, emburse_client, transaction_dict):
    transaction = emburse_client.Transaction
    assert isinstance(transaction, Transaction)
    transaction.id = transaction_dict.get('id')
    mocker.patch.object(transaction, 'make_request')
    transaction.make_request.return_value = json.dumps(transaction_dict)
    transaction = transaction.refresh()
    assert isinstance(transaction, Transaction)
    assert transaction.amount == -119.21
    assert isinstance(transaction.card, Card)
    assert isinstance(transaction.member, Member)
    assert isinstance(transaction.category, Category)
    assert isinstance(transaction.created_at, datetime.datetime)


def test_department_list(mocker, emburse_client, transaction_list):
    transaction = emburse_client.Transaction
    assert isinstance(transaction, Transaction)
    mocker.patch.object(transaction, 'make_request')
    transaction.make_request.return_value = json.dumps({'transactions': transaction_list})
    transactions = transaction.list()
    assert isinstance(transactions, list)
    assert len(transactions) == 10
    tran_ids = [x.get('id') for x in transaction_list]
    card_ids = [x.get('card').get('id') for x in transaction_list]
    for tran in transactions:
        assert isinstance(tran, Transaction)
        assert tran.id in tran_ids
        assert isinstance(tran.created_at, datetime.datetime)
        assert isinstance(tran.card, Card)
        assert tran.card.id in card_ids


def test_department_update(mocker, emburse_client, transaction_dict):
    tran_data = transaction_dict
    cat_id = str(uuid.uuid4())
    tran_update_data = {
            "id": cat_id,
            "url": "https://api.emburse.com/v1/category/{0}".format(cat_id),
            "code": randint(1000, 9999),
            "name": "Python Edu"
        }
    updated_tran = tran_data
    updated_tran['category'] = tran_update_data
    transaction = Transaction(
        auth_token='Testing123',
        **tran_data
    )
    mocker.patch.object(transaction, 'make_request')
    transaction.make_request.return_value = json.dumps(updated_tran)
    transaction.update(**{'category': tran_update_data})
    assert isinstance(transaction, Transaction)
    assert isinstance(transaction.category, Category)
    assert transaction.category.id == tran_update_data['id']
    assert transaction.category.url == tran_update_data['url']
    assert transaction.category.code == tran_update_data['code']
    assert transaction.category.name == tran_update_data['name']
