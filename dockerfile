FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg \
    fonts-liberation \
    libnss3 libatk-bridge2.0-0 libx11-6 libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 libasound2 libxshmfence1 \
    libgtk-3-0 libxext6 libxfixes3 \
    && rm -rf /var/lib/apt/lists/*

# Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV CHROME_BIN=/usr/bin/google-chrome

CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT"]