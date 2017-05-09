import pytest
import datetime
import uuid
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


def test_location_details(mocker, emburse_client, location_dict):
    location = emburse_client.Location
    assert isinstance(location, Location)
    location.id = location_dict.get('id')
    mocker.patch.object(location, 'make_request')
    location.make_request.return_value = location_dict
    location = location.refresh()
    assert isinstance(location, Location)
    assert isinstance(location.created_at, datetime.datetime)
    for key, value in location_dict.items():
        assert hasattr(location, key)
        if isinstance(value, dict):
            obj = getattr(location, key)
            for sub_key, sub_value in value.items():
                assert hasattr(obj, sub_key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(location, key) == date_parser(value)
        else:
            assert getattr(location, key) == value


def test_location_list(mocker, emburse_client, location_list):
    location = emburse_client.Location
    assert isinstance(location, Location)
    mocker.patch.object(location, 'make_request')
    location.make_request.return_value = {'locations': location_list}
    locations = location.list()
    assert isinstance(locations, list)
    assert len(locations) == 10
    for loc in locations:
        assert isinstance(loc, Location)
        lab_dict = list(filter(lambda a: a.get('id') == loc.id, location_list)).pop()
        for key, value in lab_dict.items():
            assert hasattr(loc, key)
            if isinstance(value, dict):
                obj = getattr(loc, key)
                for sub_key, sub_value in value.items():
                    assert hasattr(obj, sub_key)
                    assert getattr(obj, sub_key) == sub_value
            elif key == 'created_at':
                assert getattr(loc, key) == date_parser(value)
            else:
                assert getattr(loc, key) == value


def test_location_update(mocker, emburse_client, location_dict):
    loc_data = location_dict
    loc_update_data = {"name": "Droid Repair Fleet #{0}".format(randint(1000, 9999))}
    updated_loc_dict = loc_data
    updated_loc_dict['name'] = loc_update_data['name']
    location = Location(
        auth_token='Testing123',
        **loc_data
    )
    mocker.patch.object(location, 'make_request')
    location.make_request.return_value = updated_loc_dict
    location.update(**loc_update_data)
    assert isinstance(location, Location)
    assert isinstance(location.created_at, datetime.datetime)
    for key, value in updated_loc_dict.items():
        assert hasattr(location, key)
        if isinstance(value, dict):
            obj = getattr(location, key)
            for sub_key, sub_value in value.items():
                assert hasattr(obj, sub_key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(location, key) == date_parser(value)
        else:
            assert getattr(location, key) == value


def test_location_create(mocker, emburse_client):
    location_id = str(uuid.uuid4())
    new_label = {
        "id": location_id,
        "url": "https://api.emburse.com/v1/locations/{0}".format(location_id),
        "name": "Tatoonie",
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    location = emburse_client.Location
    mocker.patch.object(location, 'make_request')
    location.make_request.return_value = new_label
    location = location.create(**{'name': new_label['name']})
    assert isinstance(location, Location)
    assert isinstance(location.created_at, datetime.datetime)
    for key, value in new_label.items():
        assert hasattr(location, key)
        if isinstance(value, dict):
            obj = getattr(location, key)
            for sub_key, sub_value in value.items():
                assert hasattr(obj, sub_key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(location, key) == date_parser(value)
        else:
            assert getattr(location, key) == value
