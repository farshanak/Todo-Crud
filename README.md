# Todo CRUD

![CI](https://github.com/farshanak/Todo-Crud/actions/workflows/ci.yml/badge.svg)

Small Todo app: Python FastAPI backend + TypeScript/Vite frontend.

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs on http://localhost:8000.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on http://localhost:5173.

## API

- `GET    /todos`          list all
- `POST   /todos`          create `{title, done}`
- `PUT    /todos/{id}`     update
- `DELETE /todos/{id}`     delete

Storage is in-memory — restarting the backend clears all todos.
