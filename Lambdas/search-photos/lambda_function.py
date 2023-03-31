import boto3
import json
import logging
import requests
import os
import time
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
import inflection

client = boto3.client('lexv2-runtime', region_name='us-east-1')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

REGION = 'us-east-1'
HOST = 'https://search-photos-3ovexijakbdotzinh3ijjbhzyq.us-east-1.es.amazonaws.com'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, REGION, service, session_token=credentials.token)


def get_url(index, keyword):
    url = HOST + '/' + index + '/_search?q=' + keyword.lower()
    return url

# example to search for keyword bird:
# https://search-photos-3ovexijakbdotzinh3ijjbhzyq.us-east-1.es.amazonaws.com/photos/_search?q=bird

def lambda_handler(event, context):
    print("Event: {}".format(json.dumps(event)))
            
    #bucket = event['Records'][0]['s3']['bucket']['name']
    bucket = 'ccbd-a2-photos'
    try:
        # Given a search query “q”, disambiguate the query using the Amazon Lex bot.
        query = event['queryStringParameters']['q']
        print("Query: {}".format(json.dumps(query)))

        bot_response = client.recognize_text(
            botId='HXW4ESDEMT',
            botAliasId='TSTALIASID',
            localeId='en_US',
            sessionId='testuser',
            text=query
        )
        print("Bot Response: {}".format(json.dumps(bot_response)))

        slots = bot_response['interpretations'][0]['intent']['slots']
        print("Slots: {}".format(json.dumps(slots)))
        keywords = []
        if slots['photo1']:
            print(slots['photo1']['value']['interpretedValue'])
            keywords.append(slots['photo1']['value']['interpretedValue'])
        if slots['photo2']:
            print(slots['photo2']['value']['interpretedValue'])
            keywords.append(slots['photo2']['value']['interpretedValue'])
        print("Keywords: {}".format(json.dumps(keywords)))
        
        h = {"Content-Type": "application/json"}
        
        # Search the OpenSearch "photos" index for results and return them accordingly.
        photo_matches = []
        if keywords:
            for k in keywords:
                search_query = get_url('photos', inflection.singularize(k))
                print("Search Query URL: {}".format(search_query))

                es_response = requests.get(search_query, auth=awsauth, headers=h).json()
                print("Search Response: {}".format(json.dumps(es_response)))
                
                results = es_response['hits']['hits']
                print("Search Hits: {}".format(json.dumps(results)))
                
                if results:
                    for photo in results:
                        labels = [word.lower() for word in photo['_source']['labels']]
                        if k in labels:
                            photo_key = photo['_source']['objectKey']
                            photo_url = 'https://' + bucket + '.s3.amazonaws.com/' + photo_key
                            photo_matches.append(photo_url)
                            print("Photo url: {}".format(photo_url))
        
        print("Photo Matches")
        print(photo_matches)
        return {
            'statusCode': 200,
            'body': json.dumps(photo_matches),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': '*',
                'Content-Type': 'application/json'
            }
        }



    except Exception as e:
        print("Error")
        print(e)
        return {
            'statusCode': 200,
            'body': json.dumps([]),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': '*',
                'Content-Type': 'application/json'
            }
        }


