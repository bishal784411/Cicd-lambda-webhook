import json

def lambda_handler(event, context):
    print("Received event:")
    print(json.dumps(event))

    if 'body' in event:
        payload = json.loads(event['body'])
        commit_id = payload.get('head_commit', {}).get('id')
        commit_msg = payload.get('head_commit', {}).get('message')
        print(f"Commit ID: {commit_id}, Commit Message: {commit_msg}")

    return {
        'statusCode': 200,
        'body': json.dumps({"message": "This is"})
    }
