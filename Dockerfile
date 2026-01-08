FROM python:3.11-slim-bookworm as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ==========================================
# Final Runner
# ==========================================

FROM python:3.11-slim-bookworm as final

WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN useradd -m -u 1000 pefindouser
RUN mkdir -p /app/logs

COPY --chown=pefindouser:pefindouser . .

RUN chown -R pefindouser:pefindouser /app
RUN chmod -R 755 /app

USER pefindouser

EXPOSE 8001

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8001", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "--timeout", "120"]