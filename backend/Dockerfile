FROM python:3.10
WORKDIR /app
COPY app/ ./app/
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:fastapi_app", "--host", "0.0.0.0", "--port", "8000"]
