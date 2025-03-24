# Documentazione Dettagliata dell'API e degli Script Generati

Questa documentazione fornisce una panoramica completa del backend sviluppato e delle relative API, spiegando come utilizzarle, quali endpoint sono disponibili e come eseguire gli script generati per interagire con il sistema.

---

## 1. Panoramica del Sistema

Il sistema è composto da due componenti principali:

- **Backend API:** Un'applicazione FastAPI che espone endpoints per la gestione dei file e dei repository su GitHub.  
- **Client di Test:** Uno script Python che interagisce con il backend, permettendo di creare un repository, caricare un file, scaricare e cancellare file tramite le API definite.

Il backend sfrutta le API di GitHub (con il proprio PAT e configurazione) per eseguire le seguenti operazioni:
- Creazione di repository (con inizializzazione automatica e possibilità di aggiornare il README.md)
- Eliminazione di repository
- Upload di file in un percorso specifico del repository
- Download di file
- Eliminazione di file

---

## 2. Configurazione e Requisiti

### 2.1. Variabili d'Ambiente (config.py)
Il file di configurazione contiene le variabili d'ambiente necessarie per l'interazione con le API di GitHub:
- **GITHUB_TOKEN:** Personal Access Token con scope adeguato (es. `repo`, `delete_repo`).
- **GITHUB_OWNER:** Nome utente o nome dell'organizzazione GitHub.
- **GITHUB_API_URL:** URL base delle API di GitHub (solitamente `https://api.github.com`).

Esempio di `config.py`:
```python
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_API_URL = "https://api.github.com"
```
> **Nota:** Assicurarsi di non committare il PAT nel codice sorgente e di utilizzare strumenti di gestione dei segreti (ad esempio, file `.env`).

### 2.2. Dipendenze
Utilizzare il file `requirements.txt` per installare le librerie necessarie:
```
fastapi
uvicorn
requests
```
Installa le dipendenze con:
```bash
pip install -r requirements.txt
```

---

## 3. Documentazione dell'API (Backend)

Il backend è esposto tramite FastAPI e offre i seguenti endpoints:

### 3.1. Endpoint per la Gestione dei File

#### 3.1.1. **POST /upload/**
- **Descrizione:** Carica (o aggiorna) un file in un repository specificato.
- **Parametri:**
  - **Form Data:**
    - `repo_name` (string): Nome del repository in cui caricare il file.
  - **Multipart File:**
    - `file` (file): Il file da caricare.
- **Logica:**  
  Legge il contenuto del file, verifica che non superi 100 MB e chiama la funzione `github_upload_file` per creare/aggiornare il file nel percorso `uploads/{nome_file}`.
- **Risposta:**  
  Un oggetto JSON contenente informazioni sul file caricato, compreso l’URL di download (campo `download_url`).

#### 3.1.2. **GET /download/{repo_name}/{file_name}**
- **Descrizione:** Recupera le informazioni di un file e restituisce l’URL di download.
- **Parametri (Path):**
  - `repo_name` (string): Nome del repository.
  - `file_name` (string): Nome del file (presumibilmente situato nel percorso `uploads/{file_name}`).
- **Logica:**  
  Chiama `github_get_file_info` per ottenere le informazioni del file e ne estrae l'URL di download.
- **Risposta:**  
  JSON contenente l’URL di download (`download_url`).

#### 3.1.3. **DELETE /delete/{repo_name}/{file_name}**
- **Descrizione:** Elimina un file dal repository.
- **Parametri (Path):**
  - `repo_name` (string): Nome del repository.
  - `file_name` (string): Nome del file da eliminare (dal percorso `uploads/{file_name}`).
- **Logica:**  
  Ottiene lo SHA del file tramite `github_get_file_info` e poi chiama `github_delete_file` per rimuoverlo.
- **Risposta:**  
  JSON con un messaggio di conferma e i dettagli dell'operazione.

### 3.2. Endpoint per la Gestione dei Repository

#### 3.2.1. **POST /repo/create/**
- **Descrizione:** Crea un nuovo repository.
- **Parametri:**
  - **Form Data:**
    - `repo_name` (string): Nome del repository da creare.
    - `description` (string, opzionale): Descrizione del repository.
    - `private` (boolean): Indica se il repository deve essere privato o pubblico.
    - `readme_content` (string, opzionale): Contenuto personalizzato da utilizzare per il README.md. Se non fornito, il repository verrà inizializzato con un README.md di default.
- **Logica:**  
  Chiama `github_create_repo` con il parametro `auto_init=True` per inizializzare automaticamente il repository (creando la branch predefinita, solitamente "main"). Se viene fornito `readme_content`, il README.md appena creato verrà aggiornato con il contenuto fornito.
- **Risposta:**  
  JSON contenente le informazioni del repository creato.

#### 3.2.2. **DELETE /repo/delete/{repo_name}**
- **Descrizione:** Elimina un repository.
- **Parametri (Path):**
  - `repo_name` (string): Nome del repository da eliminare.
- **Logica:**  
  Chiama `github_delete_repo` per rimuovere il repository dall'account indicato.
- **Risposta:**  
  JSON con un messaggio di conferma dell’eliminazione.

---

## 4. Documentazione degli Script Generati

### 4.1. **github_client.py**
Questo modulo contiene le funzioni che interagiscono direttamente con le API di GitHub (mediante il PAT) per eseguire operazioni su file e repository.

#### Funzioni:
- **`github_upload_file(repo_name: str, path: str, content: bytes, commit_message: str, sha: str = None)`**
  - **Scopo:** Crea o aggiorna un file nel repository specificato.
  - **Parametri:**
    - `repo_name`: Nome del repository target.
    - `path`: Percorso del file all’interno del repository.
    - `content`: Contenuto del file in byte.
    - `commit_message`: Messaggio di commit da associare all’operazione.
    - `sha`: (Opzionale) SHA del file esistente per aggiornamenti.
  - **Ritorno:** JSON di risposta dalla chiamata all’API GitHub.
  
- **`github_get_file_info(repo_name: str, path: str)`**
  - **Scopo:** Recupera le informazioni (compreso lo SHA e l’URL di download) di un file nel repository.
  - **Parametri:** `repo_name` e `path` del file.
  - **Ritorno:** JSON con le informazioni del file.
  
- **`github_delete_file(repo_name: str, path: str, commit_message: str)`**
  - **Scopo:** Elimina un file dal repository.
  - **Parametri:** `repo_name`, `path` del file e `commit_message` per il commit di eliminazione.
  - **Ritorno:** JSON di conferma dell’eliminazione.
  
- **`github_create_repo(repo_name: str, description: str = "", private: bool = True, readme_content: str = None)`**
  - **Scopo:** Crea un nuovo repository per l'utente autenticato e lo inizializza (auto_init=True).
  - **Parametri:**
    - `repo_name`: Nome del repository.
    - `description`: Descrizione del repository.
    - `private`: Flag per la visibilità.
    - `readme_content`: (Opzionale) Contenuto personalizzato per il README.md.
  - **Ritorno:** JSON contenente i dettagli del repository creato.
  
- **`github_delete_repo(repo_name: str)`**
  - **Scopo:** Elimina un repository esistente.
  - **Parametri:** `repo_name`.
  - **Ritorno:** JSON di conferma dell’eliminazione.

---

### 4.2. **app.py**
Questo file definisce l'applicazione FastAPI che espone gli endpoints per la gestione dei file e dei repository.  
Gli endpoints sono suddivisi in due sezioni:

#### 4.2.1. Endpoints per la Gestione dei File:
- **POST /upload/**
  - **Scopo:** Caricare o aggiornare un file.
  - **Parametri:**  
    - File (multipart) `file`.
    - Form Data `repo_name` per indicare il repository di destinazione.
  - **Output:** JSON con il nome del file e l'URL di download.

- **GET /download/{repo_name}/{file_name}**
  - **Scopo:** Ottenere l'URL di download di un file.
  - **Parametri:** `repo_name` e `file_name` (per il percorso `uploads/{file_name}`).
  - **Output:** JSON contenente `download_url`.

- **DELETE /delete/{repo_name}/{file_name}**
  - **Scopo:** Eliminare un file dal repository.
  - **Parametri:** `repo_name` e `file_name`.
  - **Output:** JSON con messaggio di conferma e dettagli della risposta.

#### 4.2.2. Endpoints per la Gestione dei Repository:
- **POST /repo/create/**
  - **Scopo:** Creare un nuovo repository.
  - **Parametri (Form Data):**
    - `repo_name`: Nome del repository.
    - `description`: (Opzionale) Descrizione.
    - `private`: Booleano (true/false) per la visibilità.
    - `readme_content`: (Opzionale) Contenuto personalizzato per il README.md.
  - **Output:** JSON con i dettagli del repository creato.

- **DELETE /repo/delete/{repo_name}**
  - **Scopo:** Eliminare un repository.
  - **Parametri:** `repo_name` (in Path).
  - **Output:** JSON con messaggio di conferma.

---

### 4.3. Script di Test (es. test_custom_api.py)
Questo script di test permette di verificare il corretto funzionamento dell'API del backend.

#### Funzionalità:
- **Creazione del Repository:**
  - Chiama l'endpoint `/repo/create/` passando il nome "test_repo_2" e altri parametri (descrizione, visibilità).
- **Upload di un File:**
  - Crea un file "hello.txt" contenente "hello world!".
  - Chiama l'endpoint `/upload/` passando il file e specificando il repository (test_repo_2).

#### Codice:
```python
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
        "private": str(private)
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
        data = {"repo_name": repo_name}
        response = requests.post(url, data=data, files=files)
    if response.status_code != 200:
        raise Exception(f"Errore nell'upload del file: {response.status_code} - {response.text}")
    file_info = response.json()
    print("File caricato con successo:", file_info)
    return file_info

if __name__ == "__main__":
    # Creazione del repository "test_repo_2"
    repo_name = "test_repo_2"
    try:
        create_repo(repo_name, description="Repository di test creato tramite API custom", private=True)
    except Exception as e:
        print("Errore nella creazione del repo:", e)
    
    # Creazione del file "hello.txt" con il contenuto "hello world!"
    file_name = "hello.txt"
    with open(file_name, "w") as f:
        f.write("hello world!")
    
    # Caricamento del file nel repository "test_repo_2"
    try:
        upload_file(file_name, repo_name)
    except Exception as e:
        print("Errore nel caricamento del file:", e)
```

---

## 5. Istruzioni per l'Uso

1. **Configurazione Ambiente:**
   - Imposta le variabili d'ambiente necessarie (GITHUB_TOKEN, GITHUB_OWNER) nel tuo ambiente oppure in un file `.env` (assicurati di caricarlo tramite `python-dotenv` se lo utilizzi).
2. **Avviare il Backend:**
   - Esegui il backend (app.py) con Uvicorn:
     ```bash
     uvicorn app:app --reload --host 0.0.0.0 --port 8000
     ```
3. **Testare le API:**
   - Utilizza strumenti come Postman o curl per interagire con gli endpoints.
   - Oppure, esegui lo script di test (test_custom_api.py) per verificare la creazione del repository e l'upload del file:
     ```bash
     python3 test_custom_api.py
     ```
