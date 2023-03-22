import boto3
import json

client = boto3.client('lexv2-runtime', region_name='us-east-1')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

REGION = 'us-east-1'
HOST = 'https://vpc-photos-3ovexijakbdotzinh3ijjbhzyq.us-east-1.es.amazonaws.com'

def get_url(es_index, es_type, keyword):
    url = HOST + '/' + es_index + '/' + es_type + '/_search?q=' + keyword.lower()
    return url

def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
   
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['sessionId'], intent_request['sessionState']['intent']['name']))

    intent_name = intent_request['sessionState']['intent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'SearchIntent':
        return searchPhotos(intent_request)
    # elif intent_name == 'ThankYouIntent':
    #     return thank(intent_request)
    # elif intent_name == 'DiningSuggestionsIntent':
    #     return suggest(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')    
    
def searchPhotos(intent_request)
    try:
        # Given a search query “q”, disambiguate the query using the Amazon Lex bot.
        query = event['queryStringParameters']['q']

        bot_response = client.recognize_text(
            botId='HXW4ESDEMT',
            botAlias='TSTALIASID',
            localeId='en_US',
            sessionId='testuser',
            text=query
        )
        print("Bot Response: {}".format(json.dumps(bot_response)))

        keywords = bot_response['slots']
    	
    	headers = { "Content-Type": "application/json" }
    					
        # Search the OpenSearch "photos" index for results and return them accordingly.
        photo_matches = []
        if keywords:
            for k in keywords:
                search_query = get_url('photos', 'Photo', k)
    		    print("Search Query URL: {}".format(search_query))
    		    
    		    es_response = requests.get(search_query, headers=headers).json()
    			print("Search Response: {}".format(json.dumps(es_response)))
    			
    			results = es_response['hits']['hits']
    			print("Search Hits: {}".format(json.dumps(results)))
    
    			for photo in results:
    				labels = [word.lower() for word in photo['_source']['labels']]
    				if k in labels:
    					objectKey = photo['_source']['objectKey']
    					photo_url = 'https://s3.amazonaws.com/ccbd-a2-photos/' + objectKey
    					photo_matches.append(photo_url)
    		    
        # Return the matching photos
    	if photo_matches:
    		return {
    			'statusCode': 200,
    			'headers': {
    				"Access-Control-Allow-Origin": "*",
    				'Content-Type': 'application/json'
    			},
    			'body': json.dumps(photo_matches)
    		}
    	else:
    		return {
    			'statusCode': 200,
    			'headers': {
    				"Access-Control-Allow-Origin": "*",
    				'Content-Type': 'application/json'
    			},
    			'body': json.dumps("No photos matching your keywords.")
    		}

    except Exception as e:
        print("Error")
        print(e)


