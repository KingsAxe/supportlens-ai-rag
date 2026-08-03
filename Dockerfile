# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    PYTHONPATH=/app

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && \
    pip install \
      "numpy>=1.26,<3" \
      "scikit-learn>=1.5,<2" \
      "sentence-transformers>=3,<4" \
      "openai>=1.40,<2" \
      "python-dotenv>=1.0,<2" \
      "streamlit>=1.38,<2" \
      "pandas>=2.2,<3"

COPY app ./app
COPY src ./src
COPY data ./data
COPY docs ./docs
COPY .env.example ./.env.example

EXPOSE 8501

CMD ["streamlit", "run", "app/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
