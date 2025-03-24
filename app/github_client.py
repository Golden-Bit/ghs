import base64
import requests
from fastapi import HTTPException
from app.config import GITHUB_TOKEN, GITHUB_OWNER, GITHUB_API_URL


# --- Gestione File ---

def github_upload_file(repo_name: str, path: str, content: bytes, commit_message: str, sha: str = None):
    """
    Crea o aggiorna un file nel repository GitHub specificato da repo_name.
    """
    url = f"{GITHUB_API_URL}/repos/{GITHUB_OWNER}/{repo_name}/contents/{path}"
    base64_content = base64.b64encode(content).decode('utf-8')
    data = {
        "message": commit_message,
        "content": base64_content,
    }
    if sha:
        data["sha"] = sha
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.put(url, json=data, headers=headers)
    if response.status_code not in (200, 201):
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()


def github_get_file_info(repo_name: str, path: str):
    """
    Recupera le informazioni sul file dal repository specificato (compreso lo SHA).
    """
    url = f"{GITHUB_API_URL}/repos/{GITHUB_OWNER}/{repo_name}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()


def github_delete_file(repo_name: str, path: str, commit_message: str):
    """
    Elimina un file dal repository specificato.
    """
    file_info = github_get_file_info(repo_name, path)
    sha = file_info.get("sha")
    url = f"{GITHUB_API_URL}/repos/{GITHUB_OWNER}/{repo_name}/contents/{path}"
    data = {
        "message": commit_message,
        "sha": sha,
    }
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.delete(url, json=data, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()


# --- Gestione Repository ---

def github_create_repo(repo_name: str, description: str = "", private: bool = True, readme_content: str = None):
    """
    Crea un nuovo repository per l'utente autenticato.
    Il repository viene inizializzato automaticamente (auto_init=True) con una branch 'main'.
    Se viene fornito readme_content, verrà usato per aggiornare il README.md appena creato.
    """
    url = f"{GITHUB_API_URL}/user/repos"
    data = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": True  # Inizializza il repository con un commit iniziale (README.md default)
    }
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code not in (201, 200):
        raise HTTPException(status_code=response.status_code, detail=response.json())
    repo_info = response.json()

    # Se viene fornito readme_content, aggiorna il README.md con il contenuto personalizzato.
    if readme_content:
        try:
            file_info = github_get_file_info(repo_name, "README.md")
            sha = file_info.get("sha")
        except HTTPException:
            sha = None
        update_message = "Aggiornato README.md con contenuto personalizzato"
        github_upload_file(repo_name, "README.md", readme_content.encode('utf-8'), update_message, sha)

    return repo_info


def github_delete_repo(repo_name: str):
    """
    Elimina un repository esistente appartenente a GITHUB_OWNER.
    """
    url = f"{GITHUB_API_URL}/repos/{GITHUB_OWNER}/{repo_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.delete(url, headers=headers)
    if response.status_code != 204:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return {"detail": "Repository eliminato con successo."}
