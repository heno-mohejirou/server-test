FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg \
    && rm -rf /var/lib/apt/lists/*

# Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# ★ ここが修正ポイント
RUN CHROME_MAJOR=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) && \
    DRIVER_VERSION=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR}) && \
    wget -q https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

RUN which google-chrome || true
RUN which chromedriver || true
RUN google-chrome --version || true
RUN chromedriver --version || true

CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT"]