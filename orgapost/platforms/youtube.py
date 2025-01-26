import time

from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from orgapost.utils.utils import remove_non_bmp_characters

# profile_path = "/Users/emmanuellandau/Library/Application Support/Google/Chrome/Profile 1"
# chrome_options = Options()
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# driver = webdriver.Chrome(options=chrome_options)


def schedule_on_youtube(driver, video_path, description, date, time_input):
    """
    Automates uploading a video to YouTube Studio with metadata and scheduling.

    :param driver: Selenium WebDriver instance
    :param video_path: Path to the video file to upload
    :param description: Description of the video
    :param date: Scheduled date for the video (format: "Jan 15, 2025")
    :param time_input: Scheduled time for the video (format: "HH:MM")
    """


    # Click "Create" button
    create_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='dashboard-actions']/a[1]"))
    )
    create_button.click()

    # Upload the video
    video_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    driver.execute_script("arguments[0].style.display = 'block';", video_input)  # Make input visible
    video_input.send_keys(video_path)

    # Enter the description
    description_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "(//div[@id='textbox' and @contenteditable='true'])[2]"))
    )
    description_input.click()
    description_input.send_keys(remove_non_bmp_characters(description))

    # Indicate "Not made for kids"
    kids_radio = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-radio-button[@name='VIDEO_MADE_FOR_KIDS_NOT_MFK']"))
    )
    kids_radio.click()

    # Click "Next" three times
    for _ in range(3):
        next_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='next-button']/ytcp-button-shape/button"))
        )
        next_button.click()
        print("Clicked 'Next'.")

    # Set video to "Public"
    public_radio = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-radio-button[@name='PUBLIC']"))
    )
    public_radio.click()

    # Expand scheduling options
    expand_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//ytcp-icon-button[@id='second-container-expand-button']"))
    )
    expand_button.click()
    print("Clicked 'Expand' button.")

    # Trigger dropdown for scheduling
    dropdown_trigger = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'right-container')]"))
    )
    dropdown_trigger.click()
    print("Dropdown triggered.")



    # Fill in the date
    # date_input = WebDriverWait(driver, 20).until(
    #     EC.presence_of_element_located((By.XPATH, "(//input[@class='style-scope tp-yt-paper-input'])[1]"))
    # )
    # driver.execute_script("document.querySelector('tp-yt-iron-overlay-backdrop').remove();")
    # # date_input.click()
    # driver.execute_script("arguments[0].click();", date_input)
    #
    # date_input.clear()
    # date_input.send_keys(date)
    # print("Date input filled.")

    select_date_in_calendar(driver, date)
    # Fill in the time
    time_input_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'style-scope tp-yt-paper-input')]"))
)
    time_input_field.clear()
    time_input_field.send_keys(time_input)
    print("Time input filled.")

    # Confirm schedule
    calendar_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='done-button']/ytcp-button-shape/button"))
    )
    calendar_button.click()
    print("Video scheduled successfully.")


def select_date_in_calendar(driver, date_str):
    """
    Select a date in the YouTube calendar from a date string in format 'DD:MM:YYYY'.
    Handles both French and English month names.
    """
    try:
        # Parse the date
        day, month, year = date_str.split(':')
        target_date = f"{int(day)}"  # Convert to integer to remove leading zeros

        # Define month mappings for both languages
        month_mappings = {
            'fr': {
                '01': 'janv.', '02': 'févr.', '03': 'mars', '04': 'avr.',
                '05': 'mai', '06': 'juin', '07': 'juil.', '08': 'août',
                '09': 'sept.', '10': 'oct.', '11': 'nov.', '12': 'déc.'
            },
            'en': {
                '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
                '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
            }
        }

        # Try to detect language from the page
        try:
            # First try to get language attribute
            lang_attr = driver.find_element(By.CSS_SELECTOR, "html").get_attribute("lang")
            language = 'fr' if lang_attr and lang_attr.startswith('fr') else 'en'
        except:
            # If can't get language attribute, try to detect from content
            try:
                # Look for a month label
                first_month = driver.find_element(By.CLASS_NAME, "calendar-month-label").text
                language = 'fr' if any(fr_month in first_month for fr_month in month_mappings['fr'].values()) else 'en'
            except:
                # Default to English if detection fails
                language = 'en'

        print(f"[INFO] Detected language: {language}")

        # Get the appropriate month mapping
        month_mapping = month_mappings[language]
        target_month = month_mapping[month]

        # Format month-year according to language
        target_month_year = f"{target_month} {year}" if language == 'en' else f"{target_month} {year}"
        print(f"[INFO] Target: {day} {target_month} {year}")

        # Find the target month section
        month_labels = driver.find_elements(By.CLASS_NAME, "calendar-month-label")
        target_month_element = None

        for label in month_labels:
            print(target_month_year.upper() , label.text)
            if target_month_year.upper() in label.text:
                target_month_element = label
                break

        if not target_month_element:
            raise Exception(f"Month {target_month_year} not found")

        # Scroll the month into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_month_element)
        time.sleep(0.5)

        # Get the parent month container
        month_container = target_month_element.find_element(By.XPATH, "./..")

        # Find the day using a more precise XPath
        day_xpath = f".//span[contains(@class, 'calendar-day') and not(contains(@class, 'invisible')) and normalize-space(text())='{target_date}']"
        days = month_container.find_elements(By.XPATH, day_xpath)

        # Filter out any invisible or disabled days
        available_days = [day for day in days if
                          'disabled' not in day.get_attribute('class') and 'invisible' not in day.get_attribute(
                              'class')]

        if not available_days:
            raise Exception(f"Day {target_date} not found or not available")

        target_day = available_days[0]

        # Scroll and click
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_day)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", target_day)

        print(f"[INFO] Successfully selected date: {date_str}")

    except Exception as e:
        print(f"[ERROR] Failed to select date: {str(e)}")
        raise


# schedule_on_youtube(driver, "/Users/emmanuellandau/Documents/data_insta/astro/8_test_en/9/The 3 signs Sagittarius gets along with best.mp4", "Comment your birth date! 🔮#zodiacsigns #zodiac #horoscope", "27:01:2025", "15:30")

# select_date_in_calendar(driver, "19:02:2025")