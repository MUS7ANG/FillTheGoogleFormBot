# Используем Python 3.11 slim
FROM python:3.11-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    curl \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    psmisc \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Google Chrome (версия 126.0.6478.126 из Chrome for Testing)
RUN wget -O /tmp/chrome-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chrome-linux64.zip \
    && unzip /tmp/chrome-linux64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chrome-linux64/chrome /usr/local/bin/google-chrome \
    && chmod +x /usr/local/bin/google-chrome \
    && rm -rf /tmp/chrome-linux64.zip

# Устанавливаем ChromeDriver (версия 126.0.6478.126 из Chrome for Testing)
RUN wget -O /tmp/chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver-linux64.zip

# Установка зависимостей Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . .

# Запускаем контейнер от имени root
USER root

# Очищаем /tmp и завершаем процессы Chrome перед запуском
CMD rm -rf /tmp/* && killall chromedriver chrome || true && python main.py