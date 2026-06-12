FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The EDSR_x2.pb model is large. If it is not included in the archive,
# Docker will download it during build.
RUN if [ ! -f EDSR_x2.pb ]; then ./scripts/download_model.sh; fi

EXPOSE 5000

CMD ["flask", "--app", "app:app", "run", "--host=0.0.0.0", "--port=5000"]
