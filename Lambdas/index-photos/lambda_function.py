import json
import urllib.parse
import boto3
import requests
import logging
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# Code Build Comment
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
HOST = 'search-photos-3ovexijakbdotzinh3ijjbhzyq.us-east-1.es.amazonaws.com'
INDEX='photos'
region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
ca_certs_path = '/full/path/to/root-ca.pem'

def get_url(index, type):
    url = 'https://search-photos-3ovexijakbdotzinh3ijjbhzyq.us-east-1.es.amazonaws.com/' + index + '/_doc/' + type
    return url

def lambda_handler(event, context):
    print("Received event: {}".format(json.dumps(event)))

    # Get the object and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        # Call Rekognition to detect the labels of the image
        print("calling rekognition to detect labels")
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            }
        )
        print("Image Labels: {}".format(response['Labels']))
        
        # Use the S3 SDK’s headObject method to retrieve the S3 metadata created at the object’s upload time. Retrieve the x-amz-meta-customLabels metadata field, if applicable, and create a JSON array (A1) with the labels.
        s3_head_response = s3.head_object(
            Bucket=bucket,
            Key=key
        )
        custom_labels_metadata = s3_head_response.get('Metadata', {}).get('x-amz-meta-customLabels')
        labels = []
        for label in response['Labels']:
            labels.append(label['Name'])
        if custom_labels_metadata:
            custom_labels = custom_labels_metadata.split(',')
            labels.extend(custom_labels)
            
        logger.debug("CREATING JSON OBJECT")
        
        # Create the JSON object
        obj = {
            'objectKey': key,
            'bucket': bucket,
            'createdTimestamp': s3_head_response['LastModified'].isoformat(),
            'labels': labels
        }
        print("JSON object: {}".format(obj))
        logger.debug("created json object")
        
        # # create "photos" index
        # client = OpenSearch(hosts=[{
        #     'host': HOST,
        #     'port': 443
        #     }],
        #     http_auth=awsauth,
        #     use_ssl=True,
        #     verify_certs=True,
        #     connection_class=RequestsHttpConnection)
        
        # logger.debug("creating photos index")
        # index_name = 'photos'
        # index_body = {
        #   'settings': {
        #     'index': {
        #       'number_of_shards': 1
        #     }
        #   }
        # }
        # resp = client.indices.create(index_name, body=index_body)
        # logger.debug("created photo index")
        
        # Store a JSON object in an OpenSearch index (“photos”) that references the S3 object from the PUT event (E1) and append string labels to the labels array (A1), one for each label detected by Rekognition.
        url = get_url('photos', key)
        print("ES URL: {}".format(url))
        
        body = json.loads(json.dumps(obj))
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, auth=awsauth, json=body, headers=headers)
        print(r.text)
        print("Indexing photos complete.")
        
        
    except Exception as e:
        print("Error")
        print(e)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
