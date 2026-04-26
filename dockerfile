FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg \
    fonts-liberation \
    libnss3 libatk-bridge2.0-0 libx11-6 libxcomposite1 libxrandr2 \
    libgbm1 libgtk-3-0 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub \
    | gpg --dearmor -o /usr/share/keyrings/google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# ★ 新方式（ここが全て）
RUN CHROME_MAJOR=$(google-chrome --version | grep -oP '\d+' | head -1) && \
    DRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_MAJOR}) && \
    wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${DRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -rf chromedriver-linux64*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]