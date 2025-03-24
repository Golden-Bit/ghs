import requests
import os

# URL base del nostro backend
BASE_URL = "http://localhost:8000"


def create_repo(repo_name: str, description: str = "", private: bool = True, readme_content: str = None):
    """
    Chiama l'endpoint del nostro backend per creare un nuovo repository.
    Se readme_content è fornito, viene usato per il primo commit del README.md.
    """
    url = f"{BASE_URL}/repo/create/"
    data = {
        "repo_name": repo_name,
        "description": description,
        "private": str(private)  # Invia come stringa ("True" o "False")
    }
    if readme_content is not None:
        data["readme_content"] = readme_content
    response = requests.post(url, data=data)
    if response.status_code != 200:
        raise Exception(f"Errore nella creazione del repo: {response.status_code} - {response.text}")
    repo_info = response.json()
    print("Repository creato con successo:", repo_info)
    return repo_info


def upload_file(file_path: str, repo_name: str):
    """
    Chiama l'endpoint del nostro backend per caricare un file nel repository specificato.
    """
    url = f"{BASE_URL}/upload/"
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        data = {"repo_name": repo_name}  # Specifica il repository di destinazione
        response = requests.post(url, data=data, files=files)
    if response.status_code != 200:
        raise Exception(f"Errore nell'upload del file: {response.status_code} - {response.text}")
    file_info = response.json()
    print("File caricato con successo:", file_info)
    return file_info


if __name__ == "__main__":
    # 1. Creazione del repository "test_repo_2"
    repo_name = "test_repo_2"
    try:
        create_repo(repo_name, description="Repository di test creato tramite API custom", private=True)
    except Exception as e:
        print("Errore nella creazione del repo:", e)

    # 2. Creazione del file "hello.txt" con il contenuto "hello world!"
    file_name = "hello.txt"
    with open(file_name, "w") as f:
        f.write("hello world!")

    # 3. Caricamento del file usando il nostro endpoint, specificando il repository di destinazione
    try:
        upload_file(file_name, repo_name)
    except Exception as e:
        print("Errore nel caricamento del file:", e)

