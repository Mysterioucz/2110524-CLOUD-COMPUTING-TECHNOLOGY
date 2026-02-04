import json

def lambda_handler(event, context):
    try:
        # 1. Parse the body string into a dictionary
        # Proxy Integration sends the payload as a string in event['body']
        body = json.loads(event.get('body', '{}'))
        
        a = int(body.get('a', 0))
        b = int(body.get('b', 0))
        op = body.get('op', '+')
        
        if op == '+':
            res = a + b
        elif op == '-':
            res = a - b
        elif op == '*':
            res = a * b
        elif op == '/':
            res = a / b if b != 0 else 'error zero division'
        else:
            res = 'error unknown operator'
            
        # 2. Construct the correct Proxy Response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "result": str(res)
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }