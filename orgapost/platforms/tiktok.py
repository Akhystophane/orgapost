import time

from selenium.webdriver import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from orgapost.utils.utils import remove_non_bmp_characters

# profile_path = "/Users/emmanuellandau/Library/Application Support/Google/Chrome/Profile 1"
# chrome_options = Options()
# chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
# driver = webdriver.Chrome(options=chrome_options)

def schedule_on_tiktok(driver, video_path, description, time_value, date, location):
    def select_time_in_timepicker(driver, target_time):
        """
        Select a time in the TikTok time picker by scrolling to and clicking the hour and minute spans.

        Args:
            driver: Selenium WebDriver instance.
            target_time: Target time in "HH:MM" format.

        Returns:
            None
        """

        def scroll_to_time(container_class, target_value, is_hour=True):
            """
            Scroll to the target time value within the specified container.

            Args:
                container_class: Class of the container element.
                target_value: Target time value to scroll to.
                is_hour: Boolean indicating if scrolling for hours (True) or minutes (False).
            """
            # Wait for the containers
            containers = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, container_class))
            )
            container = containers[0] if is_hour else containers[1]

            # Calculate scroll position
            option_height = 32
            target_int = int(target_value)
            scroll_position = target_int * option_height

            # Click container to ensure it's active
            driver.execute_script("arguments[0].click();", container)

            # Multiple scroll attempts to ensure proper positioning
            for _ in range(3):
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[1];",
                    container,
                    scroll_position
                )
                time.sleep(0.5)  # Small delay between scroll attempts

            side_class = "tiktok-timepicker-left" if is_hour else "tiktok-timepicker-right"
            time_xpath = f"//span[contains(@class, '{side_class}') and text()='{target_value}']"
            print(f"[DEBUG] Looking for xpath: {time_xpath}")

            try:
                # First try to find the element
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, time_xpath))
                )

                # Scroll element into view if needed
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

                # Wait for it to be clickable
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, time_xpath))
                )

                # Use JavaScript click for more reliability
                driver.execute_script("arguments[0].click();", element)
                print(f"[INFO] Clicked target {'hour' if is_hour else 'minute'}: {target_value}")

            except Exception as e:
                print(f"[ERROR] Failed to interact with time element: {str(e)}")
                # Try alternative approach for minutes
                if not is_hour:
                    try:
                        # Try finding by partial match
                        alt_xpath = f"//span[contains(@class, 'tiktok-timepicker-right')]/parent::div[contains(., '{target_value}')]"
                        element = driver.find_element(By.XPATH, alt_xpath)
                        driver.execute_script("arguments[0].click();", element)
                        print(f"[INFO] Clicked minute using alternative method: {target_value}")
                    except Exception as alt_e:
                        print(f"[ERROR] Alternative approach also failed: {str(alt_e)}")
                        raise

        try:
            # Parse the target time
            target_hour, target_minute = target_time.split(":")
            print(f"[INFO] Target time: {target_hour}:{target_minute}")

            # Handle hour selection
            scroll_to_time(
                "tiktok-timepicker-time-scroll-container",
                target_hour,
                is_hour=True
            )

            time.sleep(1)  # Increased delay between selections

            # Handle minute selection
            scroll_to_time(
                "tiktok-timepicker-time-scroll-container",
                target_minute,
                is_hour=False
            )

            print("[INFO] Time successfully selected.")

        except Exception as e:
            print(f"[ERROR] Failed to select time: {str(e)}")
            raise

    def select_date_in_calendar(driver, target_date):
        """
        Select a date in the calendar with 'jj:mm:yyyy' format.

        Args:
            driver: Instance of Selenium WebDriver.
            target_date: Target date in 'jj:mm:yyyy' format.

        Returns:
            None
        """
        try:
            # Mapping of months in French
            month_mapping = {
                "January": "Janvier",
                "February": "Février",
                "March": "Mars",
                "April": "Avril",
                "May": "Mai",
                "June": "Juin",
                "July": "Juillet",
                "August": "Août",
                "September": "Septembre",
                "October": "Octobre",
                "November": "Novembre",
                "December": "Décembre"
            }

            # Convert target date from 'jj:mm:yyyy' format to a datetime object
            target_date_obj = datetime.strptime(target_date, "%d:%m:%Y")
            target_month_english = target_date_obj.strftime("%B")  # Month name in English
            target_month_french = month_mapping[target_month_english]  # Convert to French
            target_year = str(target_date_obj.year)
            target_day = str(target_date_obj.day)  # Day without leading zeros

            print(f"[INFO] Target: {target_day} {target_month_french} {target_year}")

            # Locate the month and year elements in the calendar
            month_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "month-title"))
            )
            year_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "year-title"))
            )

            # Navigate to the target month and year
            while month_element.text != target_month_french or year_element.text != target_year:
                print(f"[DEBUG] Displayed month/year: {month_element.text}/{year_element.text}")
                if int(year_element.text) > int(target_year) or (
                        int(year_element.text) == int(target_year) and month_element.text > target_month_french
                ):
                    # Current month/year is after target: click the "previous" button
                    prev_button = driver.find_element(By.XPATH,
                                                      "//*[@id='root']/div/div/div[2]/div[2]/div/div/div/div[3]/div[1]/div[4]/div[1]/div[1]/div/div[3]/div[2]/div[2]/div[1]/span[1]")
                    prev_button.click()
                    print("[INFO] Navigation: Previous month")
                else:
                    # Current month/year is before target: click the "next" button
                    next_button = driver.find_element(By.XPATH,
                                                      "//*[@id='root']/div/div/div[2]/div[2]/div/div/div/div[3]/div[1]/div[4]/div[1]/div[1]/div/div[3]/div[2]/div[2]/div[1]/span[3]")
                    next_button.click()
                    print("[INFO] Navigation: Next month")

                # Refresh month and year elements
                month_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "month-title"))
                )
                year_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "year-title"))
                )

            print(f"[INFO] Month and year found: {month_element.text} {year_element.text}")
            # Select the target day
            try:
                WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//span[@class='jsx-1793871833 day selected valid' and text()='{target_day}']"))
                )
                print("today's date")
                return True
            except Exception as e:
                    print(f"[ERROR] An error occurred: {e}")
                    pass

            # Select the target day
            day_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//span[@class='jsx-1793871833 day valid' and text()='{target_day}']"))
            )
            day_element.click()
            print(f"[INFO] Day selected: {target_day}")
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")

    driver.get("https://www.tiktok.com/tiktokstudio/upload?from=creator_center")

    video_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @accept='video/*']"))
    )
    driver.execute_script("arguments[0].style.display = 'block';", video_input)
    time.sleep(1)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH,
                                        "//input[@type='file' and @accept='video/*']"))
    ).send_keys(video_path)

    description_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
    )
    # description_input.clear()
    description_input.send_keys(Keys.COMMAND + "a")  # Select all text (Cmd+A on Mac)
    description_input.send_keys(Keys.BACKSPACE)
    desc = remove_non_bmp_characters(description)
    print(desc)
    description_input.send_keys(desc)
    time.sleep(2)
    search_input = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'Select__searchInput')]"))
    )
    search_input.click()
    search_text = location
    search_input.send_keys(search_text)
    time.sleep(2)

    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'Select__contentWrapper')]/*[1]/*[1]"))
    ).click()

    radio_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "(//input[@name='postSchedule'])[2]"))

    )
    if not radio_button.is_selected():
        driver.execute_script("arguments[0].click();", radio_button)

    schedule_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-e2e='post_video_button']"))
    )
    inputs = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "TUXTextInput"))
    )
    #
    date_input = inputs[1]
    time_input = inputs[0]
    date_input.click()
    select_date_in_calendar(driver, date)
    time_input.click()
    select_time_in_timepicker(driver, time_value)
    time_input.click()
    schedule_button.click()
    time.sleep(5)
    print('done')


# schedule_on_tiktok(driver, "/Users/emmanuellandau/Documents/data_insta/astro/8_test_en/9/The 3 signs Sagittarius gets along with best.mp4", "Comment your birth date! 🔮#zodiacsigns #zodiac #horoscope", "15:30", "27:01:2025", "France")


