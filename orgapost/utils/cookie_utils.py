import os
import json

def get_cookie(driver, path, platform):
    """
    Save cookies from the Selenium WebDriver to a JSON file under a specific key (platform).
    If the file does not exist, it is created. If the key already exists, it is updated.

    Args:
        driver: Selenium WebDriver instance.
        path (str): Path to the JSON file where cookies will be stored.
        platform (str): Name of the key under which cookies will be saved (e.g., 'tiktok').
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Load existing cookies if the file exists
    if os.path.exists(path):
        with open(path, 'r') as cookiesfile:
            cookies_data = json.load(cookiesfile)
    else:
        cookies_data = {}

    # Add or update the key with platform-specific cookies
    cookies_data[platform] = driver.get_cookies()

    # Save the cookies back to the file
    with open(path, 'w') as cookiesfile:
        json.dump(cookies_data, cookiesfile, indent=4)


def load_cookie(driver, path, platform):
    """
    Load cookies for a specific platform from a JSON file and add them to the WebDriver session.

    Args:
        driver: Selenium WebDriver instance.
        path (str): Path to the JSON file containing cookies.
        platform (str): The platform key (e.g., 'tiktok', 'instagram') to load cookies for.
    """
    try:
        # Open the JSON file and load cookies
        with open(path, 'r') as cookiesfile:
            cookies_data = json.load(cookiesfile)

        # Check if the platform exists in the cookies file
        if platform not in cookies_data:
            raise KeyError(f"No cookies found for platform: {platform}")

        # Add cookies for the specified platform
        for cookie in cookies_data[platform]:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Error adding cookie: {cookie['name']}, {e}")

    except FileNotFoundError:
        print(f"Cookie file not found at: {path}")
    except json.JSONDecodeError:
        print(f"Invalid JSON format in cookie file: {path}")
    except KeyError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



