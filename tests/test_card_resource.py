import pytest
import datetime
import uuid
import json
from random import randint
from pytest_mock import mocker
from emburse import Client, EmburseAttributeError
from emburse.resource import (
    Allowance,
    Card,
    Category,
    SharedLink
)


@pytest.fixture(scope='module')
def enburse_client():
    return Client(auth_token='Testing123')


@pytest.fixture(scope='session')
def card_id():
    return "2316d331-e2d5-43f1-9c9d-8ca3a738df28"


@pytest.fixture(scope='session')
def card_details_json():
    return """
    {
      "id": "2316d331-e2d5-43f1-9c9d-8ca3a738df28",
      "url": "https://api.emburse.com/v1/...",
      "description": "Courier #125",
      "is_virtual": true,
      "last_four": "0632",
      "state": "active",
      "assigned_to": null,
      "category": {
        "id": "ce0693b7-53dd-47cf-b145-dfaa6c9f7c00",
        "url": "https://api.emburse.com/v1/...",
        "code": null,
        "name": "Office Expenses"
      },
      "department": null,
      "label": null,
      "location": null,
      "allowance": {
        "id": "1032d733-29ff-4388-905c-458292468aab",
        "url": "https://api.emburse.com/v1/...",
        "interval": null,
        "amount": 100.0,
        "usage_limit": null,
        "transaction_limit": 100.0,
        "daily_limit": null,
        "end_time": null,
        "scope": [],
        "balance": 100.0,
        "uses_remaining": null
      },
      "expiration": "2017-09-30",
      "billing_address": {
        "address_1": "123 Main St.",
        "address_2": "",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94104"
      },
      "shared_link": {
          "id": "37c9613f-d6d9-4009-ab50-8c3a4b240e1f",
          "url": "https://api.emburse.com/v1/...",
          "link": "https://app.emburse.com/c/2316d331...",
          "card": "2316d331-e2d5-43f1-9c9d-8ca3a738df28"
      },
      "created_at": "2016-08-19T23:56:22.020801Z"
    }
"""


@pytest.fixture(scope='session')
def card_list_json():
    card_str = {
          "id": "{card_id}",
          "url": "https://api.emburse.com/v1/cards/{card_id}",
          "description": "Courier #125",
          "is_virtual": True,
          "last_four": "{last_four}",
          "state": "active",
          "assigned_to": None,
          "category": {
            "id": "{cat_id}",
            "url": "https://api.emburse.com/v1/categories/{cat_id}",
            "code": None,
            "name": "Office Expenses"
          },
          "department": None,
          "label": None,
          "location": None,
          "allowance": {
            "id": "{allowance_id}",
            "url": "https://api.emburse.com/v1/allowances/{allowance_id}",
            "interval": None,
            "amount": 100.0,
            "usage_limit": None,
            "transaction_limit": None,
            "daily_limit": None,
            "end_time": None,
            "scope": [],
            "balance": 100.0,
            "uses_remaining": None
          },
          "expiration": "{card_exp}",
          "billing_address": {
            "address_1": "123 Main St.",
            "address_2": "",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94104"
          },
          "shared_link": {
              "id": "{shared_link_id}",
              "url": "https://api.emburse.com/v1/shared_links/{shared_link_id}",
              "link": "https://app.emburse.com/c/2316d331...",
              "card": "{card_id}"
          },
          "created_at": "{created_at}"
    }
    cards = []
    while len(cards) < 10:
        card_id = str(uuid.uuid4())
        cat_id = str(uuid.uuid4())
        allowance_id = str(uuid.uuid4())
        shared_link_id = str(uuid.uuid4())
        last_four = randint(1000, 9999)
        card_exp = (datetime.datetime.utcnow() + datetime.timedelta(days=31)).date()
        created_at = datetime.datetime.utcnow()
        cards.append(
            {
                "id": card_id,
                "url": "https://api.emburse.com/v1/cards/{0}".format(card_id),
                "description": "Courier #125",
                "is_virtual": True,
                "last_four": last_four,
                "state": "active",
                "assigned_to": None,
                "category": {
                    "id": cat_id,
                    "url": "https://api.emburse.com/v1/categories/{cat_id}".format(cat_id=cat_id),
                    "code": None,
                    "name": "Office Expenses"
                },
                "department": None,
                "label": None,
                "location": None,
                "allowance": {
                    "id": allowance_id,
                    "url": "https://api.emburse.com/v1/allowances/{allowance_id}".format(allowance_id=allowance_id),
                    "interval": None,
                    "amount": 100.0,
                    "usage_limit": None,
                    "transaction_limit": None,
                    "daily_limit": None,
                    "end_time": None,
                    "scope": [],
                    "balance": 100.0,
                    "uses_remaining": None
                },
                "expiration": card_exp.strftime('%Y-%m-%d'),
                "billing_address": {
                    "address_1": "123 Main St.",
                    "address_2": "",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip_code": "94104"
                },
                "shared_link": {
                    "id": shared_link_id,
                    "url": "https://api.emburse.com/v1/shared_links/{shared_link_id}".format(shared_link_id=shared_link_id),
                    "link": "https://app.emburse.com/c/2316d331...",
                    "card": card_id
                },
                "created_at": created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
        )
    return json.dumps({'cards': cards})


def test_card_details(mocker, enburse_client, card_id, card_details_json):
    card = enburse_client.Card
    assert isinstance(card, Card)
    card.id = card_id
    mocker.patch.object(card, 'make_request')
    card.make_request.return_value = card_details_json
    card = card.refresh()
    assert isinstance(card, Card)
    assert card.id == card_id
    assert card.description == "Courier #125"
    assert card.last_four == '0632'
    assert card.expiration == datetime.datetime(2017, 9, 30)
    assert card.created_at.replace(tzinfo=None) == datetime.datetime(2016, 8, 19, 23, 56, 22, 20801)
    assert card.is_virtual
    assert isinstance(card.category, Category)
    assert isinstance(card.shared_link, SharedLink)
    assert isinstance(card.allowance, Allowance)


def test_card_list(mocker, enburse_client, card_list_json):
    card = enburse_client.Card
    mocker.patch.object(card, 'make_request')
    card.make_request.return_value = card_list_json
    cards = card.list()
    assert len(cards) == 10
    for card in cards:
        assert isinstance(card, Card)
        assert isinstance(card.category, Category)
        assert isinstance(card.shared_link, SharedLink)
        assert isinstance(card.allowance, Allowance)


def test_card_create(mocker, enburse_client, card_details_json):
    new_card_data = {
        'allowance': enburse_client.Allowance.create(interval='null', amount=100.0, transaction_limit=100.0),
        'description': "Vendor #125",
        'is_virtual': True
    }
    card = enburse_client.Card
    mocker.patch.object(card, 'make_request')
    card.make_request.return_value = card_details_json
    new_card = card.create(**new_card_data)
    assert isinstance(new_card, Card)
    assert isinstance(new_card.allowance, Allowance)
    assert new_card.allowance.amount == 100.0


def test_card_create_missing_required(enburse_client):
    new_card_data = {
        'allowance': enburse_client.Allowance.create(interval='null', amount=100.0, transaction_limit=100.0),
        'description': "Vendor #125"
    }
    with pytest.raises(EmburseAttributeError):
        card = enburse_client.Card.create(**new_card_data)


def test_card_update(mocker, card_details_json):
    card_data = json.loads(card_details_json)
    card_update_data = {'description': 'This is a test'}
    updated_card = card_data
    updated_card['description'] = 'This is a test'
    card = Card(
        auth_token='Testing123',
        **card_data
    )
    mocker.patch.object(card, 'make_request')
    card.make_request.return_value = json.dumps(updated_card)
    card.update(**card_update_data)
    assert isinstance(card, Card)
    assert card.description == card_update_data['description']
