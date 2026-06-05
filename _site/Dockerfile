ARG PYTHON_VERSION=3.11-slim
FROM python:${PYTHON_VERSION} as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 1. Install system dependencies needed for compiling python packages
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y build-essential && \
    rm -rf /var/lib/apt/lists/*

# 2. Create a secure non-root user
RUN useradd -m pythonapp && chown -R pythonapp:pythonapp /app
USER pythonapp

# 3. Point the environment path to where your '--user' pip binaries are saved
ENV PATH="/home/pythonapp/.local/bin:${PATH}"

# 4. Copy ONLY requirements first to keep build speeds fast via caching layers
COPY --chown=pythonapp:pythonapp backend/requirements.txt ./backend/requirements.txt

# 5. Explicitly upgrade pip first, then install requirements
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir --user -r backend/requirements.txt

# 🌟 FIX: Copy the ENTIRE root directory (including index.html, css, js)
# instead of isolating just the backend folder.
COPY --chown=pythonapp:pythonapp . .

# 6. Open network bindings
EXPOSE 4000

# 7. Explicitly set PYTHONPATH to allow folder mapping
ENV PYTHONPATH="/app/backend:/app"

# 8. Start your production ASGI server
CMD ["python", "-m", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:4000", "app.main:app"]
