import pytest
import datetime
import uuid
import json
from random import randint
from dateutil.parser import parse as date_parser
from pytest_mock import mocker
from emburse.client import Client, Location


@pytest.fixture(scope='module')
def emburse_client():
    return Client(auth_token='Testing123')


@pytest.fixture(scope='module')
def location_dict():
    id_ = str(uuid.uuid4())
    pid = str(uuid.uuid4())
    return {
        "id": id_,
        "url": "https://api.emburse.com/v1/locations/{0}".format(id_),
        "name": "TIE Fighter GE-{0}".format(randint(1000, 9999)),
        "parent": {
            "id": pid,
            "url": "https://api.emburse.com/v1/locations/{0}".format(pid),
            "name": "Death Star",
            "parent": 'null'
        },
        "created_at": "2016-03-11T11:57:35.467667Z"
    }


@pytest.fixture(scope='module')
def location_list():
    locations = []
    while len(locations) < 10:
        location_id = str(uuid.uuid4())
        parent_id = str(uuid.uuid4())
        locations.append(
            {
                "id": location_id,
                "url": "https://api.emburse.com/v1/locations/{0}".format(location_id),
                "name": "Storm Trooper #{0}".format(randint(1000, 9999)),
                "parent": {
                    "id": parent_id,
                    "url": "https://api.emburse.com/v1/locations/{0}".format(parent_id),
                    "name": "Star Destroyer GE-{0}".format(randint(1000, 9999)),
                    "parent": 'null'
                },
                "created_at": datetime.datetime.utcnow().isoformat()
            }
        )
    return locations


def test_label_details(mocker, emburse_client, location_dict):
    assert False, 'Test needs to be updated!'
    label = emburse_client.Label
    assert isinstance(label, Label)
    label.id = location_dict.get('id')
    mocker.patch.object(label, 'make_request')
    label.make_request.return_value = json.dumps(location_dict)
    label = label.refresh()
    assert isinstance(label, Label)
    assert isinstance(label.created_at, datetime.datetime)
    for key, value in location_dict.iteritems():
        assert hasattr(label, key)
        if isinstance(value, dict):
            obj = getattr(label, key)
            for sub_key, sub_value in value.iteritems():
                assert hasattr(obj, sub_key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(label, key) == date_parser(value)
        else:
            assert getattr(label, key) == value


def test_label_list(mocker, emburse_client, location_list):
    assert False, 'Test needs to be updated!'
    label = emburse_client.Label
    assert isinstance(label, Label)
    mocker.patch.object(label, 'make_request')
    label.make_request.return_value = json.dumps({'labels': location_list})
    labels = label.list()
    assert isinstance(labels, list)
    assert len(labels) == 10
    for lab in labels:
        assert isinstance(lab, Label)
        lab_dict = list(filter(lambda a: a.get('id') == lab.id, location_list)).pop()
        for key, value in lab_dict.iteritems():
            assert hasattr(lab, key)
            if isinstance(value, dict):
                obj = getattr(lab, key)
                for sub_key, sub_value in value.iteritems():
                    assert hasattr(obj, sub_key)
                    assert getattr(obj, sub_key) == sub_value
            elif key == 'created_at':
                assert getattr(lab, key) == date_parser(value)
            else:
                assert getattr(lab, key) == value


def test_label_update(mocker, emburse_client, location_dict):
    assert False, 'Test needs to be updated!'
    lab_data = location_dict
    lab_update_data = {"name": "Droid Repair Fleet #{0}".format(randint(1000, 9999))}
    updated_lab_dict = lab_data
    updated_lab_dict['name'] = lab_update_data['name']
    label = Label(
        auth_token='Testing123',
        **lab_data
    )
    mocker.patch.object(label, 'make_request')
    label.make_request.return_value = json.dumps(updated_lab_dict)
    label.update(**lab_update_data)
    assert isinstance(label, Label)
    assert isinstance(label.created_at, datetime.datetime)
    for key, value in updated_lab_dict.iteritems():
        assert hasattr(label, key)
        if isinstance(value, dict):
            obj = getattr(label, key)
            for sub_key, sub_value in value.iteritems():
                assert hasattr(obj, sub_key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(label, key) == date_parser(value)
        else:
            assert getattr(label, key) == value


def test_label_create(mocker, emburse_client):
    assert False, 'Test needs to be updated!'
    label_id = str(uuid.uuid4())
    new_label = {
        "id": label_id,
        "url": "https://api.emburse.com/v1/labels/{0}".format(label_id),
        "name": "Storm Trooper #{0}".format(randint(1000, 9999)),
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    label = emburse_client.Label
    mocker.patch.object(label, 'make_request')
    label.make_request.return_value = json.dumps(new_label)
    label = label.create(**{'name': new_label['name']})
    assert isinstance(label, Label)
    assert isinstance(label.created_at, datetime.datetime)
    for key, value in new_label.iteritems():
        assert hasattr(label, key)
        if isinstance(value, dict):
            obj = getattr(label, key)
            for sub_key, sub_value in value.iteritems():
                assert hasattr(obj, sub_key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(label, key) == date_parser(value)
        else:
            assert getattr(label, key) == value