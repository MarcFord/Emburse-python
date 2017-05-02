import pytest
import datetime
import uuid
import json
from pytest_mock import mocker
from emburse.client import Client, Department


@pytest.fixture(scope='module')
def emburse_client():
    return Client(auth_token='Testing123')


@pytest.fixture(scope='module')
def department_dict():
    return {
        "id": "5f93e176-7064-46dd-b517-cf1a8454d0f1",
        "url": "https://api.emburse.com/v1/departments/5f93e176-7064-46dd-b517-cf1a8454d0f1",
        "name": "Finance",
        "parent": {
          "id": "b93e384f-204e-4582-b97d-2243bf7abac1",
          "url": "https://api.emburse.com/v1/departments/b93e384f-204e-4582-b97d-2243bf7abac1",
          "name": "Money",
          "parent": 'null'
        },
        "created_at": "2016-03-11T11:59:27.666749Z"
    }


@pytest.fixture(scope='module')
def department_list():
    departments = []
    while len(departments) < 10:
        dep_id1 = str(uuid.uuid4())
        dep_id2 = str(uuid.uuid4())
        departments.append(
            {
                "id": dep_id1,
                "url": 'https://api.emburse.com/v1/departments/{dep_id}'.format(dep_id=dep_id1),
                "name": "Finance",
                "parent": {
                    "id": dep_id2,
                    "url": 'https://api.emburse.com/v1/departments/{dep_id}'.format(dep_id=dep_id2),
                    "name": "Money",
                    "parent": 'null'
                },
                "created_at": datetime.datetime.utcnow().isoformat()
            }
        )
    return departments


def test_department_details(mocker, emburse_client, department_dict):
    department = emburse_client.Department
    assert isinstance(department, Department)
    department.id = "5f93e176-7064-46dd-b517-cf1a8454d0f1"
    mocker.patch.object(department, 'make_request')
    department.make_request.return_value = json.dumps(department_dict)
    department = department.refresh()
    assert isinstance(department, Department)
    assert department.name == "Finance"
    assert isinstance(department.parent, Department)
    assert department.parent.name == 'Money'


def test_department_list(mocker, emburse_client, department_list):
    department = emburse_client.Department
    assert isinstance(department, Department)
    mocker.patch.object(department, 'make_request')
    department.make_request.return_value = json.dumps({'departments': department_list})
    departments = department.list()
    assert isinstance(departments, list)
    assert len(departments) == 10
    dep_ids = [x.get('id') for x in department_list]
    for dep in departments:
        assert dep.id in dep_ids


def test_department_create(mocker, emburse_client, department_dict):
    new_department_data = {
        'name': "Office Expenses"
    }
    department_dict['name'] = new_department_data['name']
    department = emburse_client.Department
    mocker.patch.object(department, 'make_request')
    department.make_request.return_value = json.dumps(department_dict)
    new_dep = department.create(**new_department_data)
    assert isinstance(new_dep, Department)
    assert new_dep.name == new_department_data['name']


def test_department_update(mocker, emburse_client, department_dict):
    dep_data = department_dict
    dep_update_data = {'name': 'Python Developers Team'}
    updated_dep = dep_data
    updated_dep['name'] = dep_update_data['name']
    department = Department(
        auth_token='Testing123',
        **dep_data
    )
    mocker.patch.object(department, 'make_request')
    department.make_request.return_value = json.dumps(updated_dep)
    department.update(**dep_update_data)
    assert isinstance(department, Department)
    assert department.name == dep_update_data['name']
