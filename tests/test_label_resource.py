import pytest
import datetime
import uuid
from random import randint
from dateutil.parser import parse as date_parser
from pytest_mock import mocker
from emburse.client import Client, Label


@pytest.fixture(scope='module')
def emburse_client():
    return Client(auth_token='Testing123')


@pytest.fixture(scope='module')
def label_dict():
    return {
        "id": "066a22d6-943c-4a45-b2ec-9ccd417e2685",
        "url": "https://api.emburse.com/v1/labels/066a22d6-943c-4a45-b2ec-9ccd417e2685",
        "name": "Storm Trooper #{0}".format(randint(1000, 9999)),
        "parent": {
            "id": "b93e384f-204e-4582-b97d-2243bf7abac1",
            "url": "https://api.emburse.com/v1/labels/labels/b93e384f-204e-4582-b97d-2243bf7abac1",
            "name": "Galactic Empire",
            "parent": 'null'
        },
        "created_at": "2016-03-11T11:57:35.467667Z"
    }


@pytest.fixture(scope='module')
def label_list():
    labels = []
    while len(labels) < 10:
        label_id = str(uuid.uuid4())
        label_id2 = str(uuid.uuid4())
        labels.append(
            {
                "id": label_id,
                "url": "https://api.emburse.com/v1/labels/{0}".format(label_id),
                "name": "Storm Trooper #{0}".format(randint(1000, 9999)),
                "parent": {
                    "id": label_id2,
                    "url": "https://api.emburse.com/v1/labels/{0}".format(label_id2),
                    "name": "Galactic Empire",
                    "parent": 'null'
                },
                "created_at": datetime.datetime.utcnow().isoformat()
            }
        )
    return labels


def test_label_details(mocker, emburse_client, label_dict):
    label = emburse_client.Label
    assert isinstance(label, Label)
    label.id = label_dict.get('id')
    mocker.patch.object(label, 'make_request')
    label.make_request.return_value = label_dict
    label = label.refresh()
    assert isinstance(label, Label)
    assert isinstance(label.created_at, datetime.datetime)
    for key, value in label_dict.items():
        assert hasattr(label, key)
        if isinstance(value, dict):
            obj = getattr(label, key)
            for sub_key, sub_value in value.items():
                assert hasattr(obj, sub_key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(label, key) == date_parser(value)
        else:
            assert getattr(label, key) == value


def test_label_list(mocker, emburse_client, label_list):
    label = emburse_client.Label
    assert isinstance(label, Label)
    mocker.patch.object(label, 'make_request')
    label.make_request.return_value = {'labels': label_list}
    labels = label.list()
    assert isinstance(labels, list)
    assert len(labels) == 10
    for lab in labels:
        assert isinstance(lab, Label)
        lab_dict = list(filter(lambda a: a.get('id') == lab.id, label_list)).pop()
        for key, value in lab_dict.items():
            assert hasattr(lab, key)
            if isinstance(value, dict):
                obj = getattr(lab, key)
                for sub_key, sub_value in value.items():
                    assert hasattr(obj, sub_key)
                    assert getattr(obj, sub_key) == sub_value
            elif key == 'created_at':
                assert getattr(lab, key) == date_parser(value)
            else:
                assert getattr(lab, key) == value


def test_label_update(mocker, emburse_client, label_dict):
    lab_data = label_dict
    lab_update_data = {"name": "Droid Repair Fleet #{0}".format(randint(1000, 9999))}
    updated_lab_dict = lab_data
    updated_lab_dict['name'] = lab_update_data['name']
    label = Label(
        auth_token='Testing123',
        **lab_data
    )
    mocker.patch.object(label, 'make_request')
    label.make_request.return_value = updated_lab_dict
    label.update(**lab_update_data)
    assert isinstance(label, Label)
    assert isinstance(label.created_at, datetime.datetime)
    for key, value in updated_lab_dict.items():
        assert hasattr(label, key)
        if isinstance(value, dict):
            obj = getattr(label, key)
            for sub_key, sub_value in value.items():
                assert hasattr(obj, sub_key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(label, key) == date_parser(value)
        else:
            assert getattr(label, key) == value


def test_label_create(mocker, emburse_client):
    label_id = str(uuid.uuid4())
    new_label = {
        "id": label_id,
        "url": "https://api.emburse.com/v1/labels/{0}".format(label_id),
        "name": "Storm Trooper #{0}".format(randint(1000, 9999)),
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    label = emburse_client.Label
    mocker.patch.object(label, 'make_request')
    label.make_request.return_value = new_label
    label = label.create(**{'name': new_label['name']})
    assert isinstance(label, Label)
    assert isinstance(label.created_at, datetime.datetime)
    for key, value in new_label.items():
        assert hasattr(label, key)
        if isinstance(value, dict):
            obj = getattr(label, key)
            for sub_key, sub_value in value.items():
                assert hasattr(obj, sub_key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(label, key) == date_parser(value)
        else:
            assert getattr(label, key) == value
