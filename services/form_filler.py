import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from config.config import CHROME_OPTIONS
from services.time_sync import get_exact_time, get_bishkek_time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


async def fill_form(bot, user_id, form_url, answers):
    print(f"!!! fill_form вызвана для user_id={user_id} в {get_bishkek_time()} !!!")
    driver = None
    try:
        print("Инициализация ChromeDriver...")
        options = webdriver.ChromeOptions()
        for option in CHROME_OPTIONS:
            options.add_argument(option)

#        "./chromedriver-mac-arm64/chromedriver"
        driver_path = "/usr/local/bin/chromedriver"
        print(f"Попытка запустить ChromeDriver из: {driver_path}")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print("ChromeDriver успешно запущен.")

        driver.get(form_url)
        print("Форма загружается...")
        time.sleep(5)

        # Ожидание загрузки формы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//form"))
        )
        print("Форма полностью загружена.")

        # Поиск всех текстовых полей (<input> и <textarea>)
        inputs = driver.find_elements(By.XPATH, '//input[@type="text"] | //textarea')
        print(f"Найдено текстовых полей: {len(inputs)}")
        for i, elem in enumerate(inputs):
            print(f"Поле {i + 1}: tag={elem.tag_name}, type={elem.get_attribute('type') or 'none'}")

        # Заполнение полей
        for i, answer in enumerate(answers):
            if i < len(inputs):
                inputs[i].clear()
                inputs[i].send_keys(answer)
                print(f"Заполнено поле {i + 1}: {answer}")

        # Клик по кнопке "Отправить"
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                                        '//span[contains(text(), "Отправить")] | //div[contains(@role, "button") and contains(text(), "Отправить")]'))
        )
        print("Кнопка 'Отправить' найдена.")
        submit_button.click()
        print("Кнопка 'Отправить' нажата.")

        # Проверка успешной отправки
        time.sleep(3)
        print("URL после отправки:", driver.current_url)
        if "formResponse" in driver.current_url:
            print("Форма успешно отправлена.")
        else:
            print("Ошибка: форма не отправилась, URL не изменился.")

        bishkek_time = get_bishkek_time().strftime("%H:%M:%S %d-%m-%Y")
        await bot.send_message(user_id, f"✅ Форма отправлена в {bishkek_time} по времени Бишкека!")
    except Exception as e:
        print(f"Ошибка в fill_form: {str(e)}")
        await bot.send_message(user_id, f"❌ Ошибка при заполнении формы: {str(e)}")
    finally:
        if driver is not None:
            driver.quit()
            print("Браузер закрыт.")
        else:
            print("Браузер не был запущен, ничего закрывать не нужно.")