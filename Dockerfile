# Используем Python 3.11 slim
FROM python:3.11-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    psmisc \
    # Зависимости для Firefox
    firefox-esr \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем geckodriver
RUN GECKODRIVER_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep tag_name | cut -d '"' -f 4) \
    && wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz" \
    && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && rm -rf /tmp/geckodriver.tar.gz

# Установка зависимостей Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . .

# Запускаем контейнер от имени root
USER root

# Очищаем /tmp и завершаем процессы Firefox перед запуском
CMD rm -rf /tmp/* && killall firefox geckodriver || true && python main.py