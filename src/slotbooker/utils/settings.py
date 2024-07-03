import os


# Function to set credentials
def set_credentials():
    input_username = input("Insert username: ")
    input_password = input("Insert password: ")

    # Set environment variables
    os.environ["OCTIV_USERNAME"] = input_username
    os.environ["OCTIV_PASSWORD"] = input_password
