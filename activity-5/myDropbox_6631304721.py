import json
import boto3
import sys
import base64
from datetime import datetime

s3 = boto3.client("s3")
BUCKET_NAME = "act-5"
SYSTEM_KEY = "system/system_data.json"


def get_db():
    """Get system data from S3 bucket"""
    try:
        res = s3.get_object(Bucket=BUCKET_NAME, Key=SYSTEM_KEY)
        return json.loads(res["Body"].read().decode("utf-8"))
    except s3.exceptions.NoSuchKey:  # if system_data.json not found
        return {"user": {}, "files": []}
    except:  # any other error
        print("Error getting database")
        return {"user": {}, "files": []}


def save_db(db):
    """Save system data to S3 bucket"""
    data_json = json.dumps(db)
    try:
        res = s3.put_object(Bucket=BUCKET_NAME, Key=SYSTEM_KEY, Body=data_json)
    except:  # any error
        print("Error saving database")
    return


def create_file(
    filename, owner, shared_with=[], s3_key=None, size=0, last_modified=None
):
    if last_modified is None:
        last_modified = datetime.now().isoformat()
    return {
        "filename": filename,
        "owner": owner,
        "shared_with": shared_with,
        "s3_key": s3_key,
        "size": size,
        "last_modified": last_modified,
    }


def lambda_handler(event, context):
    """Main Lambda function handler"""

    # Parse body from API Gateway
    body = json.loads(event.get("body", "{}"))
    command = body.get("command")

    # Load state
    db = get_db()
    res_msg = "Error: Unknown Command"

    if command == "put":
        username = body["username"]
        filename = body["filename"]
        file_content_b64 = body["file_data"]

        file_bytes = base64.b64decode(file_content_b64)

        s3_key = f"files/{username}/{filename}"
        res = s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=file_bytes)

        file_exists = False
        for file in db["files"]:
            if file["owner"] == username and file["filename"] == filename:
                file["size"] = sys.getsizeof(file_bytes)
                file["last_modified"] = datetime.now().isoformat()
                file_exists = True
                break

        if not file_exists:
            db["files"].append(
                create_file(
                    filename=filename,
                    owner=username,
                    s3_key=s3_key,
                    size=sys.getsizeof(file_bytes),
                    last_modified=datetime.now().isoformat(),
                )
            )

        save_db(db)
        res_msg = "Upload Successful"
    elif command == "view":
        username = body["username"]
        files = []
        for file in db["files"]:
            if file["owner"] == username or username in file["shared_with"]:
                files.append(file)
        res_msg = files
    elif command == "get":
        target_file = body["filename"]
        requester = body["username"]

        for file in db["files"]:
            if (
                file["owner"] == requester or requester in file["shared_with"]
            ) and file["filename"] == target_file:
                obj = s3.get_object(Bucket=BUCKET_NAME, Key=file["s3_key"])
                file_data = base64.b64encode(obj["Body"].read()).decode("utf-8")
                res_msg = file_data
                break

    return {"statusCode": 200, "body": json.dumps({"message": res_msg})}
