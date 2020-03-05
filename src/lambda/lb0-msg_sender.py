import boto3


def lambda_handler(event, context):
    client = boto3.client('lex-runtime')
    text = event['messages'][0]['unstructured']['text']
    response = client.post_text(
        botName='BookResturant',
        botAlias='$LATEST',
        userId='string',
        inputText=text
    )

    return response
