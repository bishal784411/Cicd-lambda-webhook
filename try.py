import json

def lambda_handler(event, context):
    print("Received event:")
    print(json.dumps(event))  # logs full event payload

    if 'body' in event:
        print("Webhook body:")
        print(event['body'])

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Webhook received successfully'})
    }
