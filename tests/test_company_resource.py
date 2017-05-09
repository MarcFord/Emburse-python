import pytest
import datetime
from dateutil.parser import parse as date_parser
from pytest_mock import mocker
from emburse.client import Client, Company


@pytest.fixture(scope='module')
def emburse_client():
    return Client(auth_token='Testing123')


@pytest.fixture(scope='module')
def company_dict():
    return {
        "id": "95e6d004-7907-415e-a373-91e9e10b4a36",
        "name": "Emburse Inc.",
        "website": "https://emburse.com/",
        "shipping_address": {
            "id": "1535a7d0-6797-46b3-8b7a-593e59d52851",
            "url": "https://api.emburse.com/v1/shipping_addresses/1535a7d0-6797-46b3-8b7a-593e59d52851",
            "address_1": "123 Main St.",
            "address_2": "",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94104"
        },
        "created_at": "2015-08-27T14:43:02.346387Z"
    }


def test_company_details(mocker, emburse_client, company_dict):
    company = emburse_client.Company
    assert isinstance(company, Company)
    company.id = company_dict.get('id')
    mocker.patch.object(company, 'make_request')
    company.make_request.return_value = company_dict
    company = company.refresh()
    assert isinstance(company, Company)
    assert isinstance(company.created_at, datetime.datetime)
    for key, value in company_dict.items():
        assert hasattr(company, key)
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                obj = getattr(company, key)
                assert getattr(obj, sub_key) == sub_value
        elif key == 'created_at':
            assert getattr(company, key) == date_parser(value)
        else:
            assert getattr(company, key) == value
