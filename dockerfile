FROM python:3.11-slim

# 必要パッケージ
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Python
WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# 環境変数（重要）
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT"]