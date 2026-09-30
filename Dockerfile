FROM python:3.13.15-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.lock ./
RUN python -m pip install --no-cache-dir --require-hashes --requirement requirements.lock \
    && groupadd --gid 10001 cicdbook \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin cicdbook

COPY --chown=10001:10001 app ./app

USER 10001:10001
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

