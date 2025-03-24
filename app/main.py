from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from app.github_client import (
    github_upload_file,
    github_get_file_info,
    github_delete_file,
    github_create_repo,
    github_delete_repo
)

app = FastAPI(title="GitHub File Storage & Repository Manager")

# --- Endpoints per la Gestione dei File ---

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    repo_name: str = Form(...)  # Specifica il repository di destinazione
):
    content = await file.read()
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Il file supera il limite di 100MB")
    commit_message = f"Aggiunto file {file.filename}"
    path = f"uploads/{file.filename}"
    result = github_upload_file(repo_name, path, content, commit_message)
    file_url = result.get("content", {}).get("download_url")
    return {"file": file.filename, "url": file_url}

@app.get("/download/{repo_name}/{file_name}")
def download_file(repo_name: str, file_name: str):
    path = f"uploads/{file_name}"
    file_info = github_get_file_info(repo_name, path)
    download_url = file_info.get("download_url")
    if not download_url:
        raise HTTPException(status_code=404, detail="File non trovato")
    return {"download_url": download_url}

@app.delete("/delete/{repo_name}/{file_name}")
def delete_file(repo_name: str, file_name: str):
    path = f"uploads/{file_name}"
    commit_message = f"Eliminato file {file_name}"
    result = github_delete_file(repo_name, path, commit_message)
    return {"detail": "File eliminato", "result": result}

# --- Endpoints per la Gestione dei Repository ---

@app.post("/repo/create/")
def create_repo(
    repo_name: str = Form(...),
    description: str = Form(""),
    private: bool = Form(True),
    readme_content: str = Form(None)
):
    """
    Crea un nuovo repository.
    Se readme_content è fornito, viene usato per il primo commit del README.md.
    Il repository verrà inizializzato automaticamente con una branch 'main'.
    """
    result = github_create_repo(repo_name, description, private, readme_content)
    return {"repository": result}

@app.delete("/repo/delete/{repo_name}")
def delete_repo(repo_name: str):
    """
    Elimina un repository.
    Attenzione: questa operazione è irreversibile.
    """
    result = github_delete_repo(repo_name)
    return result
