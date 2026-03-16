import requests
import base64

# --- CONFIGURATION ---
# TODO: Replace with your actual API Gateway Invoke URL after deployment
API_URL = (
    "https://ffgpq1coec.execute-api.ap-southeast-7.amazonaws.com/default/cloud-act-6"
)

current_user = None


def main():
    global current_user
    print("Welcome to myDropbox! Type 'help' for commands.")

    while True:
        try:
            user_input = (
                input(f"{current_user + '>>' if current_user else '>>'} ")
                .strip()
                .split()
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
            # Usage: newuser <username> <password> <password>
            if len(user_input) != 4:
                print("Usage: newuser <username> <password> <password>")
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
            response = requests.post(API_URL, json=payload)
            print(response.json()["message"])
            pass

        elif cmd == "login":
            # Usage: login <email> <password>
            # TODO: Send login request. If success, set current_user = username
            if len(user_input) != 3:
                print(f"3 Arguments needed only {len(user_input)} given")
                continue
            payload = {
                "command": "login",
                "username": user_input[1],
                "password": user_input[2],
            }
            response = requests.post(API_URL, json=payload)
            print(response.json()["message"])
            if response.json()["message"] == "Login successful":
                current_user = user_input[1]
        elif cmd == "put":
            # Usage: put <filename>
            if current_user == None:
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
                res = requests.post(API_URL, json=payload)
                print(res.json()["message"])
            except FileNotFoundError:
                print("File not found.")

        elif cmd == "view":
            # Usage: view
            if not current_user:
                print("Please login first.")
                continue

            payload = {"command": cmd, "username": current_user}
            res = requests.post(API_URL, json=payload)
            res_json = res.json()

            if "files" in res_json:
                files = res_json["files"]
                if not files:
                    print("No files found.")
                else:
                    print(
                        f"{'Filename':<20} | {'Size':<10} | {'Last Modified':<25} | {'Owner':<10}"
                    )
                    print("-" * 75)
                    for file in files:
                        print(
                            f"{file.get('filename', 'N/A'):<20} | {file.get('size', 0):<10} | {file.get('last_modified', 'N/A'):<25} | {file.get('owner', 'N/A'):<10}"
                        )
            else:
                print(f"Error: {res_json.get('message', 'Unknown error occurred')}")

        elif cmd == "get":
            # Usage: get <filename> [owner_username]
            target_user = current_user
            filename = user_input[1]

            if len(user_input) == 3:
                target_user = user_input[2]

            payload = {
                "command": cmd,
                "username": current_user,
                "filename": filename,
                "target_user": target_user,
            }
            res = requests.post(API_URL, json=payload)
            res_json = res.json()
            print(res_json["message"])
            if "file_data" in res_json:
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(res_json["file_data"]))

        elif cmd == "share":
            # Usage: share <filename> <target_user>
            if len(user_input) != 3:
                print(f"3 Arguments needed only {len(user_input)} given")
            else:
                payload = {
                    "command": cmd,
                    "username": current_user,
                    "filename": user_input[1],
                    "target_user": user_input[2],
                }
                res = requests.post(API_URL, json=payload)
                print(res.json()["message"])
        elif cmd == "logout":
            current_user = None
            print("Logged out.")
        elif cmd == "help":
            print(
                """
newuser <email> <password> <password>
login <email> <password>
put <filename>
view
get <filename> [owner_username]
share <filename> <target_user>
logout
help
quit
"""
            )


if __name__ == "__main__":
    main()
