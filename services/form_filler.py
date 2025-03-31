import time
import os
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

async def fill_form(bot, user_id, form_url, answers):
    driver = None
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="chrome-data-")
        print(f"Создана временная директория: {temp_dir}")

        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-data-dir={temp_dir}")

        options.add_argument("--headless")
        options.binary_location = "/usr/local/bin/google-chrome"

        driver_path = "/usr/local/bin/chromedriver"
        service = Service(executable_path=driver_path)

        driver = webdriver.Chrome(service=service, options=options)
        print("ChromeDriver запущен.")

        driver.get(form_url)
        time.sleep(5)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//form"))
        )

        inputs = driver.find_elements(By.XPATH, '//input[@type="text"] | //textarea')
        for i, answer in enumerate(answers):
            if i < len(inputs):
                inputs[i].clear()
                inputs[i].send_keys(answer)
                print(f"Заполнено поле {i + 1}: {answer}")

        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Отправить")]'))
        )
        submit_button.click()
        print("Форма отправлена.")

        await bot.send_message(user_id, "✅ Форма успешно отправлена!")
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        await bot.send_message(user_id, f"❌ Ошибка: {str(e)}")
    finally:
        if driver is not None:
            driver.quit()
            print("Браузер закрыт.")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Директория {temp_dir} удалена.")