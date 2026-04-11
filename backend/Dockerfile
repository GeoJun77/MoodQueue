# Start from the official lightweight Python image.
# "slim" = no unnecessary build tools, smaller image size,
# faster to download and deploy.
FROM python:3.12-slim

# Set the working directory inside the container.
# All following commands run from /app.
WORKDIR /app

# Copy requirements.txt FIRST, before the rest of the code.
# Docker caching trick: if this file hasn't changed, Docker
# skips the pip install step and uses the cached layer.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY . .

# Command that starts the server.
# --reload automatically restarts when you edit your code.
# --host 0.0.0.0 makes the server reachable outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]