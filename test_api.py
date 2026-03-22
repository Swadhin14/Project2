import requests

url = "http://127.0.0.1:8000/api/upload-resume"
files = {'file': open('d:/Hirable/test_resume.pdf', 'rb')}
response = requests.post(url, files=files)
print(response.status_code)
print(response.json())
