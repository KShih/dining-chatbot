import json

def lambda_handler(event, context):
    # TODO implement
    return {
        
        'statusCode': 200,
        'body': {
                  "messages": [
                    {
                      "type": "string",
                      "unstructured": {
                        "id": 0,
                        "text": "Hi, this is testing message",
                        "timestamp": "string"
                      }
                    }
                  ]
                }
    }

