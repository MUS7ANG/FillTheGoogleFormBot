import time
import os
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.config import CHROME_OPTIONS
from services.time_sync import get_exact_time, get_bishkek_time

async def fill_form(bot, user_id, form_url, answers):
    print(f"!!! fill_form вызвана для user_id={user_id} в {get_bishkek_time()} !!!")
    driver = None
    temp_dir = None
    try:
        # Создаём уникальную временную директорию
        temp_dir = tempfile.mkdtemp(prefix="chrome-data-")
        print(f"Создана временная директория: {temp_dir}")
        print(f"Директория существует после создания: {os.path.exists(temp_dir)}")

        # Убиваем все процессы Chrome и ChromeDriver перед запуском
        print("Завершаем процессы Chrome и ChromeDriver...")
        os.system("killall -9 chrome")
        os.system("killall -9 chromedriver")

        print("Инициализация ChromeDriver...")
        options = webdriver.ChromeOptions()

        # Логируем окружение
        print("Текущие CHROME_OPTIONS:", CHROME_OPTIONS)
        print("Проверка существования Chrome:", os.path.exists("/usr/local/bin/google-chrome"))
        print("Проверка существования ChromeDriver:", os.path.exists("/usr/local/bin/chromedriver"))

        # Добавляем опции из CHROME_OPTIONS
        for option in CHROME_OPTIONS:
            options.add_argument(option)

        # Добавляем уникальную директорию --user-data-dir
        options.add_argument(f"--user-data-dir={temp_dir}")

        # Указываем путь к Chrome
        options.binary_location = "/usr/local/bin/google-chrome"
        print(f"Путь к Chrome: {options.binary_location}")

        # Логируем все аргументы
        print("Все добавленные аргументы:", options.arguments)

        # Путь к ChromeDriver
        driver_path = "/usr/local/bin/chromedriver"
        print(f"Попытка запустить ChromeDriver из: {driver_path}")
        service = Service(
            executable_path=driver_path,
            log_path="/tmp/chromedriver.log"  # Логи ChromeDriver
        )
        driver = webdriver.Chrome(service=service, options=options)
        print("ChromeDriver успешно запущен.")

        # Логируем версии Chrome и ChromeDriver
        print(f"Chrome version: {driver.capabilities['browserVersion']}")
        print(f"ChromeDriver version: {driver.capabilities['chrome']['chromedriverVersion']}")

        # Открываем форму
        driver.get(form_url)
        print("Форма загружается...")
        time.sleep(5)

        # Ждём, пока форма появится
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//form"))
        )
        print("Форма полностью загружена.")

        # Находим текстовые поля
        inputs = driver.find_elements(By.XPATH, '//input[@type="text"] | //textarea')
        print(f"Найдено текстовых полей: {len(inputs)}")
        for i, elem in enumerate(inputs):
            print(f"Поле {i + 1}: tag={elem.tag_name}, type={elem.get_attribute('type') or 'none'}")

        # Заполняем поля
        for i, answer in enumerate(answers):
            if i < len(inputs):
                inputs[i].clear()
                inputs[i].send_keys(answer)
                print(f"Заполнено поле {i + 1}: {answer}")

        # Нажимаем кнопку "Отправить"
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Отправить")] | //div[contains(@role, "button") and contains(text(), "Отправить")]'))
        )
        print("Кнопка 'Отправить' найдена.")
        submit_button.click()
        print("Кнопка 'Отправить' нажата.")

        time.sleep(3)
        print("URL после отправки:", driver.current_url)

        bishkek_time = get_bishkek_time().strftime("%H:%M:%S %d-%m-%Y")
        await bot.send_message(user_id, f"✅ Форма отправлена в {bishkek_time} по времени Бишкека!")
    except Exception as e:
        print(f"Ошибка в fill_form: {str(e)}")
        # Выводим содержимое лога ChromeDriver, если он есть
        if os.path.exists("/tmp/chromedriver.log"):
            with open("/tmp/chromedriver.log", "r") as f:
                print("Содержимое chromedriver.log:")
                print(f.read())
        await bot.send_message(user_id, f"❌ Ошибка при заполнении формы: {str(e)}")
    finally:
        if driver is not None:
            driver.quit()
            print("Браузер закрыт.")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Временная директория удалена: {temp_dir}")
        else:
            print("Временная директория не была создана или уже удалена.")