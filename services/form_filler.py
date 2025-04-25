import time
import os
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from config.config import FIREFOX_OPTIONS
from services.time_sync import get_exact_time, get_bishkek_time

async def fill_form(bot, user_id, form_url, answers):
    print(f"!!! fill_form вызвана для user_id={user_id} в {get_bishkek_time()} !!!")
    driver = None
    temp_dir = None
    try:
        # Создаём уникальную временную директорию
        temp_dir = tempfile.mkdtemp(prefix="firefox-data-")
        print(f"Создана временная директория: {temp_dir}")
        print(f"Директория существует после создания: {os.path.exists(temp_dir)}")

        # Убиваем все процессы Firefox и geckodriver перед запуском
        print("Завершаем процессы Firefox и geckodriver...")
        os.system("killall -9 firefox")
        os.system("killall -9 geckodriver")

        print("Инициализация geckodriver...")
        options = Options()

        # Логируем окружение
        print("Текущие FIREFOX_OPTIONS:", FIREFOX_OPTIONS)
        print("Проверка существования Firefox:", os.path.exists("/usr/bin/firefox-esr"))
        print("Проверка существования geckodriver:", os.path.exists("/usr/local/bin/geckodriver"))

        # Добавляем опции из FIREFOX_OPTIONS
        for option in FIREFOX_OPTIONS:
            options.add_argument(option)

        # Указываем профиль Firefox (аналог --user-data-dir)
        options.add_argument(f"-profile {temp_dir}")

        # Указываем путь к Firefox
        options.binary_location = "/usr/bin/firefox-esr"
        print(f"Путь к Firefox: {options.binary_location}")

        # Логируем все аргументы
        print("Все добавленные аргументы:", options.arguments)

        # Путь к geckodriver
        driver_path = "/usr/local/bin/geckodriver"
        print(f"Попытка запустить geckodriver из: {driver_path}")
        service = Service(
            executable_path=driver_path,
            log_path="/tmp/geckodriver.log"  # Логи geckodriver
        )
        driver = webdriver.Firefox(service=service, options=options)
        print("geckodriver успешно запущен.")

        # Логируем версии Firefox и geckodriver
        print(f"Firefox version: {driver.capabilities['browserVersion']}")
        print(f"geckodriver version: {driver.capabilities['moz:geckodriverVersion']}")

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
        # Выводим содержимое лога geckodriver, если он есть
        if os.path.exists("/tmp/geckodriver.log"):
            with open("/tmp/geckodriver.log", "r") as f:
                print("Содержимое geckodriver.log:")
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