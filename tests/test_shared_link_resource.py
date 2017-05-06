import pytest
import datetime
import uuid
import json
from dateutil.parser import parse as date_parser
from random import randint
from pytest_mock import mocker
from emburse.client import Client, SharedLink


@pytest.fixture(scope='module')
def emburse_client():
    return Client(auth_token='Testing123')


@pytest.fixture(scope='module')
def shared_link_dict():
    link_id = str(uuid.uuid4())
    card_id = str(uuid.uuid4())
    return {
        "id": link_id,
        "url": "https://api.emburse.com/v1/shared-links/{0}".format(link_id),
        "link": "https://app.emburse.com/c/{0}".format(card_id),
        "card": card_id
    }


@pytest.fixture(scope='module')
def shared_link_list():
    links = []
    while len(links) < 10:
        link_id = str(uuid.uuid4())
        card_id = str(uuid.uuid4())
        links.append(
            {
                "id": link_id,
                "url": "https://api.emburse.com/v1/shared-links/{0}".format(link_id),
                "link": "https://app.emburse.com/c/{0}".format(card_id),
                "card": card_id
            }
        )
    return links


def test_shared_link_details(mocker, emburse_client, shared_link_dict):
    link = emburse_client.SharedLink
    assert isinstance(link, SharedLink)
    link.id = shared_link_dict.get('id')
    mocker.patch.object(link, 'make_request')
    link.make_request.return_value = json.dumps(shared_link_dict)
    link = link.refresh()
    assert isinstance(link, SharedLink)
    for key, value in shared_link_dict.items():
        assert hasattr(link, key)
        if isinstance(value, dict):
            obj = getattr(link, key)
            for sub_key, sub_value in value.items():
                assert hasattr(obj, sub_key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(link, key) == date_parser(value)
        else:
            assert getattr(link, key) == value


def test_shared_link_list(mocker, emburse_client, shared_link_list):
    link = emburse_client.SharedLink
    assert isinstance(link, SharedLink)
    mocker.patch.object(link, 'make_request')
    link.make_request.return_value = json.dumps({'shared-links': shared_link_list})
    links = link.list()
    assert isinstance(links, list)
    assert len(links) == 10
    for lin in links:
        assert isinstance(lin, SharedLink)
        lab_dict = list(filter(lambda a: a.get('id') == lin.id, shared_link_list)).pop()
        for key, value in lab_dict.items():
            assert hasattr(lin, key)
            if isinstance(value, dict):
                obj = getattr(lin, key)
                for sub_key, sub_value in value.items():
                    assert hasattr(obj, sub_key)
                    assert getattr(obj, sub_key) == sub_value
            elif key == 'created_at':
                assert getattr(lin, key) == date_parser(value)
            else:
                assert getattr(lin, key) == value


def test_shared_link_create(mocker, emburse_client):
    link_id = str(uuid.uuid4())
    card_id = str(uuid.uuid4())
    new_link_data = {
        "id": link_id,
        "url": "https://api.emburse.com/v1/shared-links/{0}".format(link_id),
        "link": "https://app.emburse.com/c/{0}".format(card_id),
        "card": card_id
    }
    link = emburse_client.SharedLink
    mocker.patch.object(link, 'make_request')
    link.make_request.return_value = json.dumps(new_link_data)
    link = link.create(**new_link_data)
    assert isinstance(link, SharedLink)
    for key, value in new_link_data.items():
        assert hasattr(link, key)
        if isinstance(value, dict):
            obj = getattr(link, key)
            for sub_key, sub_value in value.items():
                assert hasattr(obj, sub_key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(link, key) == date_parser(value)
        else:
            assert getattr(link, key) == value
