FROM python:3.10-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application files
COPY service-account.json ./
COPY ./daily_word_bot ./daily_word_bot

EXPOSE 8443

# Run the application using uv
CMD ["uv", "run", "python", "-m", "daily_word_bot"]
