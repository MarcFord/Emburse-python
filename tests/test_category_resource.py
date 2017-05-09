import pytest
import datetime
import uuid
from random import randint
from pytest_mock import mocker
from emburse.client import Client, Category


@pytest.fixture(scope='module')
def enburse_client():
    return Client(auth_token='Testing123')


@pytest.fixture(scope='module')
def category_dict():
    return {
        'id': "ce0693b7-53dd-47cf-b145-dfaa6c9f7c00",
        "url": "https://api.emburse.com/v1/category/ce0693b7-53dd-47cf-b145-dfaa6c9f7c00",
        "code": 1002,
        "name": "Office Expenses",
        "parent": {
              "id": "b93e384f-204e-4582-b97d-2243bf7abac1",
              "url": "https://api.emburse.com/v1/category/b93e384f-204e-4582-b97d-2243bf7abac1",
              "code": 1000,
              "name": "Expenses",
              "parent": 'null'
        },
        "created_at": "2016-02-28T08:40:53.373895Z"
    }


@pytest.fixture(scope='module')
def category_list_dict():
    categories = []
    while len(categories) < 10:
        cat_id = str(uuid.uuid4())
        categories.append(
            {
                'id': cat_id,
                'url': 'https://api.emburse.com/v1/category/{0}'.format(cat_id),
                'code': randint(1000, 9999),
                'name': 'Office-{0}'.format(randint(1000, 9999)),
                'created_at': datetime.datetime.utcnow().isoformat()
            }
        )
    return categories


def test_category_details(mocker, enburse_client, category_dict):
    category = enburse_client.Category
    assert isinstance(category, Category)
    category.id = "ce0693b7-53dd-47cf-b145-dfaa6c9f7c00"
    mocker.patch.object(category, 'make_request')
    category.make_request.return_value = category_dict
    category = category.refresh()
    assert isinstance(category, Category)
    assert category.name == "Office Expenses"
    assert isinstance(category.parent, Category)


def test_category_list(mocker, enburse_client, category_list_dict):
    category = enburse_client.Category
    assert isinstance(category, Category)
    mocker.patch.object(category, 'make_request')
    category.make_request.return_value = {'categories': category_list_dict}
    category_list = category.list()
    assert isinstance(category_list, list)
    assert len(category_list) == 10
    cat_ids = [x.get('id') for x in category_list_dict]
    for cat in category_list:
        assert cat.id in cat_ids


def test_category_create(mocker, enburse_client, category_dict):
    new_category_data = {
        'code': 1002,
        'name': "Office Expenses"
    }
    category = enburse_client.Category
    mocker.patch.object(category, 'make_request')
    category.make_request.return_value = category_dict
    new_cat = category.create(**new_category_data)
    assert isinstance(new_cat, Category)
    assert new_cat.code == 1002
    assert new_cat.name == 'Office Expenses'


def test_category_update(mocker, enburse_client, category_dict):
    cat_data = category_dict
    cat_update_data = {'code': 5001}
    updated_cat = cat_data
    updated_cat['code'] = 5001
    category = Category(
        auth_token='Testing123',
        **cat_data
    )
    mocker.patch.object(category, 'make_request')
    category.make_request.return_value = updated_cat
    category.update(**cat_update_data)
    assert isinstance(category, Category)
    assert category.code == cat_update_data['code']
