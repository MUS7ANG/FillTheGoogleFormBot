import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from config.config import CHROME_OPTIONS
from services.time_sync import get_exact_time, get_bishkek_time


async def fill_form(bot, user_id, form_url, answers):
    print(f"!!! fill_form вызвана для user_id={user_id} в {get_bishkek_time()} !!!")
    driver = None
    try:
        print("Инициализация ChromeDriver...")
        options = webdriver.ChromeOptions()
        for option in CHROME_OPTIONS:
            options.add_argument(option)

        driver_path = "./chromedriver-mac-arm64/chromedriver"
        print(f"Попытка запустить ChromeDriver из: {driver_path}")
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print("ChromeDriver успешно запущен.")

        driver.get(form_url)
        print("Форма загружается...")
        time.sleep(2)

        target_time = get_exact_time() + 3
        print(f"Ожидание точного времени: {target_time}")
        while get_exact_time() < target_time - 0.1:
            time.sleep(0.01)

        inputs = driver.find_elements(By.XPATH, '//input[@type="text"]')
        print(f"Найдено текстовых полей: {len(inputs)}")
        for i, answer in enumerate(answers):
            if i < len(inputs):
                inputs[i].send_keys(answer)
                print(f"Заполнено поле {i + 1}: {answer}")

        submit_button = driver.find_element(By.XPATH, '//span[text()="Отправить"]')
        submit_button.click()
        print("Форма отправлена.")

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