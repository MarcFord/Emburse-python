import pytest
from emburse import Client
from emburse.resource import (
    Account,
    Allowance,
    Card,
    Category,
    Company,
    Department,
    Label,
    Location,
    Member,
    SharedLink,
    Statement,
    Transaction
)


@pytest.fixture(scope='module')
def enburse_client():
    return Client(auth_token='Testing123')


def test_client_has_auth_token(enburse_client):
    assert enburse_client.auth_token == 'Testing123'


def test_account_property(enburse_client):
    assert isinstance(enburse_client.Account, Account)


def test_allowance_property(enburse_client):
    assert isinstance(enburse_client.Allowance, Allowance)


def test_card_property(enburse_client):
    assert isinstance(enburse_client.Card, Card)


def test_category_property(enburse_client):
    assert isinstance(enburse_client.Category, Category)


def test_company_property(enburse_client):
    assert isinstance(enburse_client.Company, Company)


def test_department_property(enburse_client):
    assert isinstance(enburse_client.Department, Department)


def test_label_property(enburse_client):
    assert isinstance(enburse_client.Label, Label)


def test_location_property(enburse_client):
    assert isinstance(enburse_client.Location, Location)


def test_member_property(enburse_client):
    assert isinstance(enburse_client.Member, Member)


def test_shared_link_property(enburse_client):
    assert isinstance(enburse_client.SharedLink, SharedLink)


def test_statement_property(enburse_client):
    assert isinstance(enburse_client.Statement, Statement)


def test_transaction_property(enburse_client):
    assert isinstance(enburse_client.Transaction, Transaction)
