FROM python:3.11-slim

# Render上でChrome (Chromium) を動作させるための依存パッケージと日本語フォントをインストール
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    fonts-liberation \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# RenderではPORT環境変数が自動的に与えられるため、シェル形式で起動して変数を展開する
CMD gunicorn app:app --bind 0.0.0.0:$PORT