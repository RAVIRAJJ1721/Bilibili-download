
import requests

# Paste your copied cookies string here
cookies = "cookie1=value1; cookie2=value2; cookie3=value3"

# Set headers with the cookies
headers = {
    'Cookie': cookies
}

# Example request to Bilibili
url = 'https://www.bilibili.com/'
response = requests.get(url, headers=headers)

# Print the response (or use the response as needed)
print(response.text)

# Optional: Save cookies to a file
with open('cookies.txt', 'w') as f:
    f.write(cookies)
