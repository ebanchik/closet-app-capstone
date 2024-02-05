# client_script.py
import requests

base_url = "http://127.0.0.1:5000"
login_url = f"{base_url}/login"

email = "eli@banchik.com"
password = "password"

# Make a login request and print the cookies
login_response = requests.post(login_url, data={"email": email, "password": password})
print("Cookies:", login_response.cookies)

# Print the response text
print("Response:", login_response.text)
