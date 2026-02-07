import requests
import json
import base64
import os
import sys

# --- CONFIGURATION ---
# TODO: Replace with your actual API Gateway Invoke URL after deployment
API_URL = "https://xyz123.execute-api.us-east-1.amazonaws.com/prod/dropbox"

current_user = 'user'


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
        elif cmd == "newuser":
            # Usage: newuser <email> <password> <password>
            if len(user_input) != 4:
                print("Usage: newuser <email> <password> <password>")
                continue
            if user_input[2] != user_input[3]:
                print("Error: Passwords do not match.")
                continue

            payload = {
                "command": "newuser",
                "username": user_input[1],
                "password": user_input[2],
            }
            # TODO: Send POST request to API_URL with payload
            # response = requests.post(API_URL, json=payload)
            # print(response.json()['message'])
            pass

        elif cmd == "login":
            # Usage: login <email> <password>
            # TODO: Send login request. If success, set current_user = username
            pass

        elif cmd == "put":
            # Usage: put <filename>
            if not current_user:
                print("Please login first.")
                continue

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
            except FileNotFoundError:
                print("File not found.")

        elif cmd == "view":
            # Usage: view
            if not current_user:
                print("Please login first.")
                continue

            # TODO: Send 'view' command, print the list of files returned
            pass

        elif cmd == "get":
            # Usage: get <filename> [owner_username]
            # TODO: Handle args. If owner_username not provided, use current_user
            # TODO: Send request.
            # TODO: If response contains file data (Base64), decode it and write to file:
            # with open(filename, "wb") as f:
            #     f.write(base64.b64decode(response_data))
            pass

        elif cmd == "share":
            # Usage: share <filename> <target_user>
            # TODO: Send share command
            pass

        elif cmd == "logout":
            current_user = None
            print("Logged out.")


if __name__ == "__main__":
    main()
