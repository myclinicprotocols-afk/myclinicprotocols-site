FROM python:3.12-slim

WORKDIR /app
COPY fulfillment/requirements.txt /app/fulfillment/requirements.txt
RUN pip install --no-cache-dir -r /app/fulfillment/requirements.txt
COPY fulfillment /app/fulfillment
RUN useradd --create-home --uid 10001 appuser && mkdir -p /data && chown appuser:appuser /data
USER appuser

ENV MYCP_PRIVATE_ROOT=/data
EXPOSE 8000
CMD ["sh", "-c", "uvicorn fulfillment.service:app --host 0.0.0.0 --port ${PORT:-10000} --proxy-headers"]
