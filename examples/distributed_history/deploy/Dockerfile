FROM python:3.11-slim

WORKDIR /app
COPY ecommerce_backend ./ecommerce_backend
ENV PYTHONPATH=/app
ENV ECOMMERCE_PORT=18080
EXPOSE 18080
CMD ["python", "-m", "ecommerce_backend.service"]
