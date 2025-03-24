import requests

url = 'https://raw.githubusercontent.com/Bit-Gen/test_repo_2/main/uploads/hello.txt'
headers = {
    'Authorization': 'token YOUR_TOKEN'
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    print("File scaricato con successo")
    content = response.content
    print(content)
    # Puoi salvare il file o elaborarlo
else:
    print("Errore:", response.status_code)