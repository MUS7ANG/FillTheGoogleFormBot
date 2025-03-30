# Базовый образ с Python
FROM python:3.11-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    psmisc \  # Для killall
    && rm -rf /var/lib/apt/lists/*

# Установка Chrome 134.0.6998.118
RUN wget -O /tmp/chrome.deb https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.118/linux64/chrome-linux64.zip \
    && unzip /tmp/chrome.deb -d /usr/local/bin/ \
    && mv /usr/local/bin/chrome-linux64/chrome /usr/local/bin/google-chrome \
    && chmod +x /usr/local/bin/google-chrome \
    && rm -rf /tmp/chrome.deb

# Установка ChromeDriver 134.0.6998.118
RUN wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.118/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver.zip

# Установка зависимостей Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Завершаем процессы Chrome перед запуском
CMD killall chromedriver chrome || true && python main.py