# Recipe Website - FastAPI Backend

The backend provides a FastAPI REST API and a server-rendered Jinja2 admin panel for managing recipes.

## Development

Using `uv`:
```bash
uv sync
uv run uvicorn main:app --reload
```

Using standard pip/venv:
```python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Docker

```bash
docker build -t fastapi-backend .
docker run -d -p 8000:8000 --name fastapi-backend fastapi-backend
curl http://localhost:8000/
```
