import requests
import json
import base64
import os
import sys

# --- CONFIGURATION ---
# TODO: Replace with your actual API Gateway Invoke URL after deployment
API_URL = "https://xyz123.execute-api.us-east-1.amazonaws.com/prod/dropbox"

current_user = "user"


def main():
    global current_user
    print("Welcome to myDropbox! Type 'help' for commands.")

    while True:
        try:
            user_input = (
                input(f"{current_user if current_user else '>>'} ").strip().split()
            )
        except EOFError:
            break

        if not user_input:
            continue

        cmd = user_input[0].lower()

        if cmd == "quit":
            break

        # --- COMMANDS ---
        elif cmd == "put":
            # Usage: put <filename>

            filename = user_input[1]
            try:
                with open(filename, "rb") as f:
                    file_data = f.read()
                    # Convert binary file to Base64 string to send over JSON
                    b64_data = base64.b64encode(file_data).decode("utf-8")

                payload = {
                    "command": "put",
                    "username": current_user,
                    "filename": filename,
                    "file_data": b64_data,
                }
                # TODO: requests.post(API_URL, json=payload)
                requests.post(API_URL, json=payload)
                print("OK")
            except FileNotFoundError:
                print("File not found.")

        elif cmd == "view":
            # Usage: view

            # TODO: Send 'view' command, print the list of files returned
            payload = {"command": "view", "username": current_user}
            response = requests.post(API_URL, json=payload)
            res = response.json()
            if res["statusCode"] == 200:
                body_data = json.loads(res["body"])
                files = body_data["message"]
                res = []
                for file in files:
                    res.append(
                        f"{file['filename']} {file['size']} {file['last_modified']} {file['owner']}"
                    )
                print("\n".join(res))
        elif cmd == "get":
            # Usage: get <filename> [owner_username]
            # TODO: Handle args. If owner_username not provided, use current_user
            # TODO: Send request.
            # TODO: If response contains file data (Base64), decode it and write to file:
            # with open(filename, "wb") as f:
            #     f.write(base64.b64decode(response_data))
            filename = user_input[1]
            try:
                owner = user_input[2]
            except:
                owner = current_user
            payload = {"command": "get", "filename": filename, "username": owner}
            response = requests.post(API_URL, json=payload)
            res = response.json()
            if res["statusCode"] == 200:
                body_data = json.loads(res["body"])
                file_data = base64.b64decode(body_data["message"])
                with open(filename, "wb") as f:
                    f.write(file_data)
                print("OK")
            else:
                print("Download Error")


if __name__ == "__main__":
    main()
