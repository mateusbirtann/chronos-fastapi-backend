FROM python:3.10.12-slim

WORKDIR /app

# Copiar o arquivo requirements.txt primeiro
COPY requirements.txt .

# Instalar as dependências
RUN pip install -r requirements.txt

# Copiar o resto dos arquivos
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
