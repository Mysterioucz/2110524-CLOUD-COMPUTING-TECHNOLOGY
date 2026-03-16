import json
import boto3
import sys
import base64
from datetime import datetime

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
users_table = dynamodb.Table("act-6-myDropboxUsers")
files_table = dynamodb.Table("act-6-myDropboxFiles")
BUCKET_NAME = "act-6"


def lambda_handler(event, context):
    """Main Lambda function handler"""

    # Parse body from API Gateway
    body_str = event.get("body")
    if body_str is None:
        body_str = "{}"
    body = json.loads(body_str)
    command = body.get("command")

    res_msg = "Error: Unknown Command"

    try:
        if command == "newuser":
            username = body.get("username")
            password = body.get("password")

            # Check if user exists
            response = users_table.get_item(Key={"username": username})
            if "Item" in response:
                res_msg = "Username already exists"
            else:
                users_table.put_item(Item={"username": username, "password": password})
                res_msg = "User created successfully"

        elif command == "login":
            username = body.get("username")
            password = body.get("password")

            response = users_table.get_item(Key={"username": username})
            if "Item" in response and response["Item"].get("password") == password:
                res_msg = "Login successful"
            else:
                res_msg = "Invalid username or password"

        elif command == "put":
            username = body.get("username")
            filename = body.get("filename")
            file_content_b64 = body.get("file_data")

            file_bytes = base64.b64decode(file_content_b64)
            s3_key = f"files/{username}/{filename}"
            size = sys.getsizeof(file_bytes)

            s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=file_bytes)

            files_table.put_item(
                Item={
                    "s3_key": s3_key,
                    "filename": filename,
                    "owner": username,
                    "size": size,
                    "last_modified": datetime.now().isoformat(),
                    "shared_with": [],
                }
            )
            res_msg = "Upload Successful"

        elif command == "view":
            username = body.get("username")
            files_list = []

            # Scan files table to find files owned by user or shared with user
            response = files_table.scan()
            items = response.get("Items", [])

            for f in items:
                if f.get("owner") == username or username in f.get("shared_with", []):
                    # Append file details
                    files_list.append(
                        {
                            "filename": f.get("filename"),
                            "owner": f.get("owner"),
                            "size": int(f.get("size")),
                            "last_modified": f.get("last_modified"),
                        }
                    )

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Success", "files": files_list}),
            }

        elif command == "get":
            requester = body.get("username")
            filename = body.get("filename")
            target_user = body.get("target_user", requester)

            s3_key = f"files/{target_user}/{filename}"
            response = files_table.get_item(Key={"s3_key": s3_key})

            if "Item" in response:
                f = response["Item"]
                if f.get("owner") == requester or requester in f.get("shared_with", []):
                    obj = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
                    file_data = base64.b64encode(obj["Body"].read()).decode("utf-8")
                    return {
                        "statusCode": 200,
                        "body": json.dumps(
                            {
                                "message": "File downloaded successfully",
                                "file_data": file_data,
                            }
                        ),
                    }
                else:
                    res_msg = "Permission denied"
            else:
                res_msg = "File not found"

        elif command == "share":
            requester = body.get("username")
            filename = body.get("filename")
            target_user = body.get("target_user")

            s3_key = f"files/{requester}/{filename}"
            response = files_table.get_item(Key={"s3_key": s3_key})

            if "Item" in response:
                f = response["Item"]
                if f.get("owner") == requester:
                    shared_with = f.get("shared_with", [])
                    if target_user not in shared_with:
                        shared_with.append(target_user)
                        files_table.update_item(
                            Key={"s3_key": s3_key},
                            UpdateExpression="SET shared_with = :s",
                            ExpressionAttributeValues={":s": shared_with},
                        )
                    res_msg = "File shared successfully"
                else:
                    res_msg = "Permission denied"
            else:
                res_msg = "File not found"

    except Exception as e:
        res_msg = f"Error: {str(e)}"

    return {"statusCode": 200, "body": json.dumps({"message": res_msg})}
