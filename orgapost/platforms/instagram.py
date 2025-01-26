import time

import pyautogui as pyautogui
import pyperclip
import selenium.common.exceptions
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from orgapost.utils.footage_editor import trim_video
from orgapost.utils.utils import remove_non_bmp_characters

# profile_path = "/Users/emmanuellandau/Library/Application Support/Google/Chrome/Profile 1"
# chrome_options = Options()
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# driver = webdriver.Chrome(options=chrome_options)

def schedule_on_ig(driver, video_path, description, date, time_input):
    """
    Automates uploading a video reel to Facebook Business, filling in details, and scheduling it.

    :param driver: Selenium WebDriver instance
    :param video_path: Path to the video file
    :param description: Description of the reel
    :param time_input: Time (hour:minute format) for scheduling
    :param date: Date for scheduling (format: dd/mm/yyyy)
    :param location: Placeholder for additional functionality
    """
    video_path = trim_video(video_path, max_duration=90)

    # Open the Facebook Reels Composer page

    wait = WebDriverWait(driver, 20)

    # Add video
    add_video_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'x1fvot60') and text()='Ajouter une vidéo']"))
    )
    add_video_button.click()
    time.sleep(3)

    # Type the video path character by character
    for char in video_path:
        pyautogui.write(char)
    time.sleep(2)
    pyautogui.write(['enter'])
    time.sleep(2)
    pyautogui.write(['enter'])

    # Enter the reel description
    description_field = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[@aria-label=\"Décrivez votre reel pour que les gens sachent de quoi il s’agit\"]"))
    )
    description_field.click()
    description_field.send_keys(remove_non_bmp_characters(description))
    time.sleep(2)
    buttons = []
    while len(buttons) < 2:

        buttons = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.XPATH,
                                                 "//div[@role='button' and @tabindex='0' and not(@aria-disabled) and .//div[contains(text(), 'Suivant')]]"))
        )
        print('not loaded')

    next_button = buttons[-1]
    next_button.click()

    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH,
                                             "//div[@role='button' and @tabindex='0' and not(@aria-disabled) and .//div[contains(text(), 'Suivant')]]"))
    ).click()


    # Click "Schedule"
    schedule_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and .//div[text()='Programmer']]"))
    )
    schedule_button.click()

    # Enter the date
    date = date.replace(':', '/')
    date_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='jj/mm/aaaa']")))
    date_field.click()
    time.sleep(0.2)
    date_field.send_keys(Keys.COMMAND, 'a')  # Select existing text (CMD + A on Mac)
    date_field.send_keys(date)
    date_field.send_keys(Keys.TAB)
    time.sleep(0.2)

    # Enter the time
    hour_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='heures']")))
    hour_field.clear()
    time.sleep(0.1)
    hours = time_input.split(':')[0]
    print(hours)
    hour_field.send_keys(hours)

    minutes_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='minutes']")))
    minutes_field.clear()
    time.sleep(0.1)
    minutes = time_input.split(':')[1]
    print(minutes)
    minutes_field.send_keys(minutes)

    # Confirm "Programmer"
    elements_programmer = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//*[contains(text(), 'Programmer')]"))
    )
    if len(elements_programmer) >= 2:
        second_element_programmer = elements_programmer[1]  # Select the second "Programmer" element
        button_div = second_element_programmer.find_element(
            By.XPATH, "./ancestor::div[@role='button']"
        )
        button_div.click()
    else:
        print("Less than 2 elements containing 'Programmer' found.")

# schedule_on_ig(driver, "/Users/emmanuellandau/Documents/data_insta/astro/8_test_en/9/The 3 signs Sagittarius gets along with best.mp4", "Comment your birth date! 🔮#zodiacsigns #zodiac #horoscope", "27:01:2025", "15:30")
