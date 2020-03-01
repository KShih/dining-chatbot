from __future__ import print_function # Python 2/3 compatibility
import boto3
import os
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

session = boto3.session.Session()
credentials = session.get_credentials()
service = 'es'
ENDPOINT = "https://search-restaurants-kcmb5vcpfi2wp6m25xvuy2ht5m.us-east-1.es.amazonaws.com"
AWSAUTH = AWS4Auth(credentials.access_key, credentials.secret_key, session.region_name, service)

def scan_dynamodb():
    """
    scan through the dynamodb, scrap only id and cuisine
    :return: list of dic which contain id and cuisine
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp-restaurants')

    pe = "id, cuisine"
    responses = table.scan(ProjectionExpression=pe)['Items']
    return responses

def push_elastic(responses):
    """
    push the data to elastic search index
    :param responses: list of dic which contain id and cuisine
    """
    es = Elasticsearch(ENDPOINT, http_auth=AWSAUTH, use_ssl=True, verify_certs=True, connection_class=RequestsHttpConnection)

    for response in responses:
        es.index(index="restaurants", doc_type="restaurant", id=response['id'], body=response)


# es = Elasticsearch(ENDPOINT, http_auth=AWSAUTH, use_ssl=True, verify_certs=True, connection_class=RequestsHttpConnection)
# es.indices.create(index="restaurant", ignore=400)
response = scan_dynamodb()
push_elastic(response)