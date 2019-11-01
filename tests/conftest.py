# -*- coding: utf-8 -*-
import os

import boto3
import pytest

from app import app as chalice_app

DDB_TABLE_NAME = 'chat'  # TODO: Better to acquire from other constant or configured env var

if os.environ['API_ENDPOINT'] == 'localhost':
    ddb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
else:
    ddb = boto3.resource('dynamodb')

table = ddb.Table(DDB_TABLE_NAME)


@pytest.fixture
def app():
    return chalice_app


def _create_test_ddb_table():
    return ddb.create_table(
        TableName=DDB_TABLE_NAME,
        AttributeDefinitions=[
            {
                'AttributeName': 'name',
                'AttributeType': 'S',
            },
            {
                'AttributeName': 'time',
                'AttributeType': 'S',
            },
            {
                'AttributeName': 'chat_room',
                'AttributeType': 'S',
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'name',
                'KeyType': 'HASH',
            },
            {
                'AttributeName': 'time',
                'KeyType': 'RANGE',
            },
        ],
        GlobalSecondaryIndexes=[{
            'IndexName': 'chat_room_time_idx',
            'KeySchema': [
                {
                    'AttributeName': 'chat_room',
                    'KeyType': 'HASH',
                },
                {
                    'AttributeName': 'time',
                    'KeyType': 'RANGE',
                },
            ],
            'Projection': {
                'ProjectionType': 'ALL',
            },
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 100,
                'WriteCapacityUnits': 100
            }
        }],
        ProvisionedThroughput={
            'ReadCapacityUnits': 100,
            'WriteCapacityUnits': 100
        },

    )


def ddb_test_data_put():
    table.put_item(
        Item={
            'name': 'test_name',
            'time': 'test_time',
            'comment': 'test_data',
            'chat_room': 'test_chat'
        },
        ReturnValues='ALL_OLD',
        ReturnConsumedCapacity='TOTAL'
    )


@pytest.fixture(autouse=True, scope='session')
def ddb_table():
    _create_test_ddb_table()
    table.wait_until_exists()
    ddb_test_data_put()

    yield table
    table.delete()
    table.wait_until_not_exists()
