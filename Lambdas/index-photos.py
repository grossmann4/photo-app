import json
import urllib.parse
import boto3
import requests

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
HOST = 'https://vpc-photos-3ovexijakbdotzinh3ijjbhzyq.us-east-1.es.amazonaws.com'

def get_url(index, type):
    url = HOST + '/' + index + '/' + type
    return url

def lambda_handler(event, context):
    print("Received event: {}".format(json.dumps(event)))

    # Get the object and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        # Call Rekognition to detect the labels of the image
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
            Key=object_key
        )
        custom_labels_metadata = s3_head_response.get('Metadata', {}).get('x-amz-meta-customLabels')
        labels = []
        for label in response['Labels']:
            labels.append(label['Name'])
        if custom_labels_metadata:
            custom_labels = custom_labels_metadata.split(',')
            labels.extend(custom_labels)
            
        # Create the JSON object
        obj = {
            'objectKey': key,
            'bucket': bucket,
            'createdTimestamp': s3_head_response['LastModified'].isoformat(),
            'labels': labels
        }
        print("JSON object: {}".format(obj))
        
        # Store a JSON object in an OpenSearch index (“photos”) that references the S3 object from the PUT event (E1) and append string labels to the labels array (A1), one for each label detected by Rekognition.
        url = get_url('photos', 'Photo')
        print("ES URL: {}".format(url))
        body = json.dumps(obj)
        headers = {"Content-Type": "application/json"}
        r = requests.post(url=url, data=body, headers=headers)

        print("Indexing photos complete.")

    except Exception as e:
        print("Error")
        print(e)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
