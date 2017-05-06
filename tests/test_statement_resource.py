import pytest
import datetime
from pytest_mock import mocker
from emburse.client import Statement
from emburse.errors import EmburseTypeError, EmburseValueError


def test_statement_export_requires_account_id():
    statement = Statement(auth_token='Test123')

    with pytest.raises(EmburseValueError):
        statement.export()


def test_statement_export_start_date():
    statement = Statement(auth_token='Test123', account_id=1)

    with pytest.raises(EmburseTypeError):
        statement.export(start_date='2017-05-01')


def test_statement_export_end_date():
    statement = Statement(auth_token='Test123', account_id=1)

    with pytest.raises(EmburseTypeError):
        statement.export(end_date='2017-05-01')


def test_statement_export_valid_request_call(mocker):
    statement = Statement(auth_token='Test123', account_id=1)
    e_date = datetime.datetime.utcnow()
    s_date = e_date - datetime.timedelta(days=3)
    mocker.patch.object(statement, 'make_request')
    statement.make_request.return_value = 'test1, test2, test3'
    statement.export(
        start_date=s_date,
        end_date=e_date,
        file_format=Statement.CSV_FORMAT
    )
    statement.make_request.assert_called_with(
        method='GET',
        url_='/accounts/1/statement.csv',
        params={
            'start_date': s_date,
            'end_date': e_date
        }
    )
