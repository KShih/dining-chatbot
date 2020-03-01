import json
import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']
    

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


def send_sqs_msg(queue_name, msg_body):
    sqs_client = boto3.client('sqs')
    sqs_queue_url = sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']
    try:
        msg = sqs_client.send_message(QueueUrl=sqs_queue_url, MessageBody=json.dumps(msg_body))
    except ClientError as e:
        logging.error(e)
        return None
    return msg


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def validate_dining_suggestion(location, resturant_type, time, people):
    locations = ['new york']
    resturant_types = ['french', 'chinese', 'indian', 'american']
    
    if location is not None and location.lower() not in locations:
        return build_validation_result(False,
                                       'rLocation',
                                       'We do not serve {}'
                                       'The city we currently serve is New York'.format(location))
    
    if resturant_type is not None and resturant_type.lower() not in resturant_types:
        return build_validation_result(False,
                                       'rType',
                                       'We do not serve {resturant_type}'
                                       'The resturant type we currently serve is {resturant_types}'
                                       .format(resturant_type=resturant_type, resturant_types=str(resturant_types)))

    if time is not None:
        if len(time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'rTime', None)

        hour, minute = time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'rTime', None)

        if hour < 10 or hour > 23:
            # Outside of business hours
            return build_validation_result(False, 'rTime', 'Our business hours are from ten a m. to five p m. Can you specify a time during this range?')
            
    if people is not None and (people < 0 or isinstance(people,float)):
        return build_validation_result(False,
                                       'rPeople',
                                       'You should enter postive integer.')

    return build_validation_result(True, None, None)

""" --- Functions that control the bot's behavior --- """

def greeting(intent_request):
    source = intent_request['invocationSource']
    
    if source == 'DialogCodeHook':
        # There is no slot in greeting intent, send back msg to user directly
        slots = get_slots(intent_request)
        
        # Do nothing to the slot, bcuz there is no slots
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Hi, I am your dining chat bot how can I help you?'})


def dining_suggestion(intent_request):
    """
    Performs dialog management and fulfillment for ordering resturant.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """
    
    location = get_slots(intent_request)['rLocation']
    resturant_type = get_slots(intent_request)['rType']
    time = get_slots(intent_request)['rTime']
    people = get_slots(intent_request)['rPeople']
    phone_num = get_slots(intent_request)['PhoneNumber']
    source = intent_request['invocationSource']
    queue_name = 'reservationQ'
    
    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)
        print(slots)
        validation_result = validate_dining_suggestion(location, resturant_type, time, people)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        return delegate(output_session_attributes, get_slots(intent_request))
        
    sqs_msg = send_sqs_msg(queue_name, get_slots(intent_request))
    if sqs_msg is not None:
        return close(intent_request['sessionAttributes'],
                     'Fulfilled',
                     {'contentType': 'PlainText',
                      'content': 'Thanks, your order for {} type of resturant for {} at {} has been placed.'.format(resturant_type, people, time)})
    else:
        return close(intent_request['sessionAttributes'],
                     'Fulfilled',
                     {'contentType': 'PlainText',
                      'content': 'Sorry, there is something wrong with the SQS server, will get back to you later.'})


""" --- Intents --- """

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return dining_suggestion(intent_request)
    elif intent_name == 'GreetingIntent':
        return greeting(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')
    

""" --- Main handler --- """

def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)


