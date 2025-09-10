# Welcome to Learuma AI

In many parts of the world, internet access is still limited or unreliable, restricting access to education, healthcare, and agricultural knowledge.  
**Learuma AI** aims to bring the power of AI to underserved communities even completely offline.

This repository comes from my work on the original frontend of this project ([https://github.com/Osiris8/learuma-ai-frontend](https://github.com/Osiris8/learuma-ai-frontend)) and the original backend of this project ([https://github.com/Osiris8/learnable-ai-backend](https://github.com/Osiris8/learnable-ai-backend)).

## Objective

- Enable teachers to better prepare their courses without documentary resources.
- Help healthcare professionals with limited staff (especially in rural areas) in decision-making and save more human lives.
- Guide and assist farmers in increasing their agricultural production in order to reduce hunger and poverty.

## How to Use Learuma AI ?

Learuma uses:

- **Flask** (Python framework) as the backend
- **Next.js** (JavaScript framework) as the frontend
- **SQLite** as the database

### Prerequisites

- Download **Python** if you don’t have it already → [python.org](https://www.python.org/)
- Download **Node.js** if you don’t have it already → [nodejs.org](https://nodejs.org/en)

## Clone This Repository

```bash
git clone https://github.com/Osiris8/learuma-ai
```

- Open the folder **"learuma-ai"** in your favorite code editor (VS Code, Cursor, Sublime Text, Kiro... etc.)

## Backend Setup

1. Open your terminal and navigate to the backend:

   ```bash
   cd backend
   ```

2. **Create a virtual environment**

   - On **macOS/Linux**:

     ```bash
     python3 -m venv .venv
     ```

   - On **Windows**:

     ```bash
     py -3 -m venv .venv
     ```

3. **Activate your environment**

   - On **macOS/Linux**:

     ```bash
     . .venv/bin/activate
     ```

   - On **Windows**:

     ```bash
     .venv\Scripts\activate
     ```

   More details on virtual environments: [Flask Installation Guide](https://flask.palletsprojects.com/en/stable/installation/)

4. **.env file**

   - In the root of your backend folder, create a file named `.env`.
   - Copy and paste the contents of backend file `.env.example` into it.

5. **Install backend dependencies**

   ```bash
   pip install pip Flask flask-cors flask-jwt-extended Flask-SQLAlchemy python-dotenv chromadb ollama pypdf
   ```

6. **Download Ollama**

   - Go to [ollama.com](https://ollama.com) and download it.

7. **Add `gpt-oss:20b` in Ollama**

   You have two options:

   - Option 1: Download `gpt-oss:20b` directly from Ollama
   - Option 2: Run in your backend terminal:

     ```bash
     ollama pull gpt-oss:20b
     ```

8. **Install `nomic-embed-text`**

   `nomic-embed-text` is a large context length text encoder that surpasses OpenAI’s `text-embedding-ada-002` and `text-embedding-3-small` on short and long context tasks.

   In your backend terminal, run:

   ```bash
   ollama pull nomic-embed-text
   ```

### Start Your Backend

Run:

```bash
flask --app main run
```

This command generates the `chroma` folder as well as the `instance` folder, which contains the SQLite file `app.db`.

By default, your backend will run at:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

## Routes Test

### Authentification

#### SignUp

```bash
curl -X POST http://localhost:5000/signup \
-H "Content-Type: application/json" \
-d '{
  "firstname": "John",
  "lastname": "Doe",
  "email": "john.doe@example.com",
  "password": "password123"
}'

```

#### Login

```bash
curl -X POST http://localhost:5000/login \
-H "Content-Type: application/json" \
-d '{
  "email": "john.doe@example.com",
  "password": "password123"
}'
```

#### Logout

```bash
curl -X POST http://localhost:5000/logout \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <YOUR_JWT_HERE>"
```

**Reponse :**

```json
{
  "msg": "logout successfully"
}
```

#### User Data

```bash
curl -X GET http://localhost:5000/me \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <YOUR_JWT_HERE>"
```

**Reponse :**

```json
{
  "user": {
    "firstname": "John",
    "lastname": "Doe",
    "email": "john.doe@example.com"
  }
}
```
