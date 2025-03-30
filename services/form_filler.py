import time
import tempfile
import os
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
        print("Инициализация ChromeDriver...")
        options = webdriver.ChromeOptions()

        temp_dir = tempfile.mkdtemp(prefix="chrome-data-")
        print(f"Создана временная директория: {temp_dir}")

        filtered_options = [opt for opt in CHROME_OPTIONS if not opt.startswith("--user-data-dir")]
        options.add_argument(f"--user-data-dir={temp_dir}")
        for option in filtered_options:
            options.add_argument(option)

        driver_path = "/usr/local/bin/chromedriver"
        print(f"Попытка запустить ChromeDriver из: {driver_path}")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print("ChromeDriver успешно запущен.")

        driver.get(form_url)
        print("Форма загружается...")
        time.sleep(5)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//form"))
        )
        print("Форма полностью загружена.")

        inputs = driver.find_elements(By.XPATH, '//input[@type="text"] | //textarea')
        print(f"Найдено текстовых полей: {len(inputs)}")
        for i, elem in enumerate(inputs):
            print(f"Поле {i + 1}: tag={elem.tag_name}, type={elem.get_attribute('type') or 'none'}")

        for i, answer in enumerate(answers):
            if i < len(inputs):
                inputs[i].clear()
                inputs[i].send_keys(answer)
                print(f"Заполнено поле {i + 1}: {answer}")

        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '//span[contains(text(), "Отправить")] | //div[contains(@role, "button") and contains(text(), "Отправить")]'))
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
        await bot.send_message(user_id, f"❌ Ошибка при заполнении формы: {str(e)}")
    finally:
        if driver is not None:
            driver.quit()
            print("Браузер закрыт.")
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            print(f"Временная директория удалена: {temp_dir}")
        else:
            print("Браузер или директория не были созданы, ничего удалять не нужно.")