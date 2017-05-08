import pytest
import datetime
from pytz import utc as UTC
import json
import uuid
from dateutil.parser import parse as date_parser
from random import randint
from pytest_mock import mocker
from emburse.requestor import Requestor
from emburse.http_client import new_default_http_client
from emburse.errors import EmburseAPIError


@pytest.fixture(scope='function')
def request_rtn():
    id_ = str(uuid.uuid4())
    pid = str(uuid.uuid4())
    return {
        "id": id_,
        "url": "https://api.emburse.com/v1/labels/{0}".format(id_),
        "name": "Storm Trooper #{0}".format(randint(1000, 9999)),
        "parent": {
            "id": pid,
            "url": "https://api.emburse.com/v1/labels/labels/{0}".format(pid),
            "name": "Galactic Empire",
            "parent": 'null'
        },
        "created_at": datetime.datetime.utcnow().replace(tzinfo=UTC).isoformat()
    }


@pytest.fixture(scope='function')
def requestor_obj(mocker, request_rtn):
    client = new_default_http_client()
    mocker.patch.object(client, 'request')
    client.request.return_value = json.dumps(request_rtn), 200, {'status': 'OK'}
    req_obj = Requestor(token='Testing123', client=client)
    return req_obj


@pytest.fixture(scope='function')
def request_date_params():
    return {
        'start_date': datetime.datetime.utcnow().replace(tzinfo=UTC),
        'end_date': (datetime.datetime.utcnow() - datetime.timedelta(days=30)).replace(tzinfo=UTC)
    }


@pytest.fixture(scope='function')
def request_nested_dict_params(request_date_params):
    return {
        'name': 'Test String',
        'date': request_date_params
    }


def test_api_encode_dates(requestor_obj, request_date_params):
    encoded_params = list(requestor_obj.api_encode(request_date_params))
    for param in encoded_params:
        assert request_date_params.get(param[0]).isoformat() == param[1]


def test_api_encode_nested(requestor_obj, request_nested_dict_params):
    encoded_params = list(requestor_obj.api_encode(request_nested_dict_params))
    solution_set = [
        'Test String',
        request_nested_dict_params['date']['start_date'].isoformat(),
        request_nested_dict_params['date']['end_date'].isoformat()
    ]
    for param in encoded_params:
        assert param[1] in solution_set


def test_request_raw(requestor_obj, request_rtn):
    resp = requestor_obj.request_raw(
        method='get',
        url='/cards/066a22d6-943c-4a45-b2ec-9ccd417e2685',
    )
    assert resp == (json.dumps(request_rtn), 200, {'status': 'OK'}, 'Testing123')


def test_interpret_response(requestor_obj, request_rtn):
    raw_resp = requestor_obj.request_raw(
        method='get',
        url='/cards/066a22d6-943c-4a45-b2ec-9ccd417e2685',
    )
    resp = requestor_obj.interpret_response(raw_resp[0], raw_resp[1], raw_resp[2])
    assert resp.get('name') == request_rtn.get('name')


def test_handle_api_error(requestor_obj, request_rtn):
    raw_resp = requestor_obj.request_raw(
        method='get',
        url='/cards/066a22d6-943c-4a45-b2ec-9ccd417e2685',
    )
    with pytest.raises(EmburseAPIError):
        requestor_obj.interpret_response(raw_resp[0], 404, {'status': 'Not Found'})


def test_request(requestor_obj, request_rtn):
    resp, token = requestor_obj.request(
        method='get',
        url_='/cards/066a22d6-943c-4a45-b2ec-9ccd417e2685',
    )
    assert resp.get('name') == request_rtn.get('name')
    assert token == 'Testing123'