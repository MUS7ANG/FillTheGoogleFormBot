import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from services.time_sync import get_exact_time, get_bishkek_time

async def fill_form(bot, user_id, form_url, answers):
    print(f"!!! fill_form вызвана для user_id={user_id} в {get_bishkek_time()} !!!")
    driver = None
    try:
        print("Инициализация Chrome и Chromedriver...")

        options = Options()
        options.add_argument("--headless=new")  # или "--headless"
        options.add_argument("--no-sandbox")  # важно!
        options.add_argument("--disable-dev-shm-usage")  # важно!
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")  # важно!
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-software-rasterizer")

        driver_path = "/usr/bin/chromedriver"  # Убедись, что chromedriver установлен
        service = Service(executable_path=driver_path)
        service = Service()  # если chromedriver в PATH
        driver = webdriver.Chrome(service=service, options=options)
        print("Chromedriver успешно запущен.")

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


        print("Поиск кнопки отправки...")
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Submit"]/ancestor::div[@role="button"]'))
        )
        print("Кнопка 'Отправить' найдена.")
        submit_button.click()
        print("Кнопка 'Отправить' нажата.")

        time.sleep(3)
        print("URL после отправки:", driver.current_url)

        bishkek_time = get_bishkek_time().strftime("%H:%M:%S %d-%m-%Y")
        await bot.send_message(user_id, f"✅ Форма отправлена в {bishkek_time} по времени Бишкека!")
    except Exception as e:
        print(f"❌ Ошибка в fill_form: {str(e)}")
        await bot.send_message(user_id, f"❌ Ошибка при заполнении формы: {str(e)}")
    finally:
        if driver is not None:
            driver.quit()
            print("Браузер закрыт.")
