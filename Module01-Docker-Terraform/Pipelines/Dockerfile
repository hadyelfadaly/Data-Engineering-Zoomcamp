FROM python:3.13.11-slim
# Copy uv binary from official uv image (multi-stage build pattern) and placing it in bin directory
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

# Add virtual environment to PATH so we can use installed packages (can be used insted of uv run)
ENV PATH="/app/.venv/bin:$PATH"

# RUN pip install pandas pyarrow #isnt needed if we are using uv to install dependencies
# Copy dependency files first (better layer caching)
COPY "pyproject.toml" "uv.lock" ".python-version" ./

# Install dependencies from lock file (ensures reproducible builds)
RUN uv sync --locked

#Copy the pipeline script into the container
COPY pipeline.py pipeline.py
#Copy the ingest_data script into the container
COPY ingest_data.py ingest_data.py

# Set entry point
ENTRYPOINT ["python", "ingest_data.py"]
# CMD ["uv", "run", "python", "pipeline.py"] #Alternative way to run the script using uv