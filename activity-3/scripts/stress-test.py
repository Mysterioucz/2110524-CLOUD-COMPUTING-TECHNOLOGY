from doctest import SKIP
import re
import subprocess
import sys

# --- CONFIGURATION (UPDATE THESE) ---
KEY_PATH = "/home/chatrin/.ssh/cu_cloud_usa.pem"  # Path to your .pem file on YOUR PC
SIEGE_INSTANCE_IP = "44.202.196.66"  # The Public IP of the Siege EC2 instance
TARGET_URL = "http://phpiaasgroup-1-407212990.us-east-1.elb.amazonaws.com/"  # Your Beanstalk URL

# Test Settings
USER_COUNTS = [10, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250]
TEST_TIME = "2M"
SKIP_COUNT= int(input("Number to skip operation:"))


def run_remote_test():
    print(f"\n--- Connecting to {SIEGE_INSTANCE_IP} to test {TARGET_URL} ---")
    print("Users,Throughput,AvgResponseTime")
    i=0
    for users in USER_COUNTS:
        if i < SKIP_COUNT:
            print(f"Skipping {i}")
            i += 1
            continue
        sys.stderr.write(f"Remote testing with {users} users... ")
        sys.stderr.flush()
        
        # The command we want the REMOTE server to execute
        # We add '2>&1' to force Siege's stderr output into stdout so SSH captures it easily
        remote_cmd = f"siege -c {users} -t {TEST_TIME} -b {TARGET_URL}"

        # The SSH command to run from your PC
        # -o StrictHostKeyChecking=no prevents the "Are you sure?" yes/no prompt
        if users == 250:
            remote_cmd = remote_cmd = f"siege -c {users} -t 15M -b {TARGET_URL}"
        ssh_cmd = [
            "ssh",
            "-i",
            KEY_PATH,
            "-o",
            "StrictHostKeyChecking=no",
            f"ec2-user@{SIEGE_INSTANCE_IP}",
            remote_cmd,
        ]

        try:
            # Run SSH and wait for it to finish
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)

            # Combine stdout and stderr because siege writes to stderr
            output = result.stderr + result.stdout

            # --- PARSING RESULTS ---
            t_match = re.search(r"Transaction rate:\s+([\d\.]+)", output)
            r_match = re.search(r"Response time:\s+([\d\.]+)", output)

            if t_match and r_match:
                throughput = t_match.group(1)
                resp_time = r_match.group(1)
                print(
                    f"{users},{throughput},{resp_time}"
                )  # Prints to your local screen
                with open("results.csv", "a") as f:
                    f.write(
                        f"{users},{throughput},{resp_time}\n"
                    )  # Appends to local file
                sys.stderr.write("Done.\n")
            else:
                sys.stderr.write("Failed (Did you install siege on the EC2?).\n")
                # Optional: print output to debug
                # print(output)

        except Exception as e:
            sys.stderr.write(f"\nError: {e}\n")
            break


def plot_results():
    import matplotlib.pyplot as plt

    users = []
    throughputs = []
    resp_times = []

    with open("results.csv", "r") as f:
        next(f)  # Skip header
        for line in f:
            u, t, r = line.strip().split(",")
            users.append(int(u))
            throughputs.append(float(t))
            resp_times.append(float(r))

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(users, throughputs, marker="o")
    plt.title("Throughput vs Users")
    plt.xlabel("Number of Users")
    plt.ylabel("Throughput (transactions/sec)")

    plt.subplot(1, 2, 2)
    plt.plot(users, resp_times, marker="o", color="r")
    plt.title("Response Time vs Users")
    plt.xlabel("Number of Users")
    plt.ylabel("Average Response Time (sec)")

    plt.tight_layout()
    plt.savefig("performance_plot.png")
    plt.show()


if __name__ == "__main__":
    run_remote_test()
    # plot_results()
