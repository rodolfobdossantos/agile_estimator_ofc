FROM python:3.11-slim

RUN pip install --no-cache-dir mlflow==3.12.0

WORKDIR /app

COPY model/experiments/mlruns ./mlruns

EXPOSE 5000

CMD ["sh", "-c", "mlflow server \
    --backend-store-uri file:///app/mlruns \
    --default-artifact-root file:///app/mlruns \
    --host 0.0.0.0 \
    --port ${PORT:-5000} \
    --workers 1 \
    --allowed-hosts '*'"]
