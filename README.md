# SJYYJ

![img](img/gui.png)

## Get Started

```bash
python -m venv .venv
pip install -r requirements-dev.lock
# Install pytorch
```

### `.env` Example
```
OPENIE_URL='http://localhost:8000'
```

## Run CLI

```bash
docker compose up
python main.py file 'data/cnn/article.txt'
python main.py text 'I made arrangements pick up her dog'
```

## Run GUI

```bash
docker compose up
streamlit run web.py
```
