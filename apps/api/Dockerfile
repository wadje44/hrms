FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install deps first for better layer caching. A stub package lets the editable
# install resolve before the real source is copied, so the heavy dependency
# layer is cached across code changes.
COPY pyproject.toml ./
RUN pip install --upgrade pip \
    && mkdir -p app && touch app/__init__.py \
    && pip install -e ".[dev]" \
    && rm -rf app

COPY . .

EXPOSE 8000

# Default command (overridden by docker-compose for local reload).
# In production, migrations run as a separate CI step before deploy.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
