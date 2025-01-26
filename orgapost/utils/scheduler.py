import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from orgapost.platforms.instagram import schedule_on_ig
from orgapost.platforms.tiktok import schedule_on_tiktok
from orgapost.platforms.youtube import schedule_on_youtube


def get_unscheduled_posts(calendar_file):
    """
    Load Calendar.json and retrieve all unscheduled posts (scheduled = false)
    and posts with a future or current date. Posts are organized by accounts and platforms.

    Args:
        calendar_file (str): Path to the Calendar.json file.

    Returns:
        dict: Dictionary structured by accounts and platforms with unscheduled posts.
    """
    if not os.path.exists(calendar_file):
        raise FileNotFoundError(f"Le fichier {calendar_file} est introuvable.")

    with open(calendar_file, "r") as file:
        calendar = json.load(file)

    unscheduled_posts = {}
    today = datetime.now().date()

    for account, data in calendar.items():
        unscheduled_posts[account] = {}

        for post in data["posts"]:
            post_date = datetime.strptime(post["date"], "%d:%m:%Y").date()
            if not post["scheduled"] and post_date >= today:
                platform = post["platform"]
                if platform not in unscheduled_posts[account]:
                    unscheduled_posts[account][platform] = []
                unscheduled_posts[account][platform].append(post)

        if not unscheduled_posts[account]:
            del unscheduled_posts[account]

    return unscheduled_posts


def update_post_status(calendar_file, account, post):
    """
    Update the `scheduled` status of a specific post in the Calendar.json file.

    Args:
        calendar_file (str): Path to the Calendar.json file.
        account (str): The account under which the post exists.
        post (dict): The post to update.

    Returns:
        None
    """
    if not os.path.exists(calendar_file):
        raise FileNotFoundError(f"Le fichier {calendar_file} est introuvable.")

    with open(calendar_file, "r") as file:
        calendar = json.load(file)

    for calendar_post in calendar[account]["posts"]:
        if (
            calendar_post["platform"] == post["platform"]
            and calendar_post["date"] == post["date"]
            and calendar_post["time"] == post["time"]
            and calendar_post["folder_path"] == post["folder_path"]
        ):
            calendar_post["scheduled"] = True
            break

    # Save the updated calendar
    with open(calendar_file, "w") as file:
        json.dump(calendar, file, indent=4)
    print(f"[INFO] Calendar updated for post: {post}")


def schedule_posts(unscheduled_posts, schedule_functions, calendar_file):
    """
    Iterate through unscheduled posts by platform and call the corresponding function for each platform.

    Args:
        unscheduled_posts (dict): Dictionary of unscheduled posts by account and platform.
        schedule_functions (dict): Dictionary mapping platforms to scheduling functions.
        calendar_file (str): Path to the Calendar.json file.

    Returns:
        None
    """
    profile_path = "/Users/emmanuellandau/Library/Application Support/Google/Chrome/Profile 1"
    #/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/Users/emmanuellandau/Library/Application Support/Google/Chrome/Profile 1"
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)

    for account, platforms in unscheduled_posts.items():
        for platform, posts in platforms.items():
            if platform not in schedule_functions:
                print(f"[Warning] No scheduling function defined for {platform}.")
                continue

            schedule_function = schedule_functions[platform]

            for post in posts:
                folder_path = post["folder_path"]
                date = post["date"]
                time = post["time"]

                video_path = next(
                    (
                        os.path.join(folder_path, f) for f in os.listdir(folder_path)
                        if f.endswith(".mp4") and "trimmed" not in f
                    ),
                    None
                ) if os.path.isdir(folder_path) else None

                description_path = os.path.join(folder_path, f"cap_{platform}.txt")
                description = None
                if os.path.exists(description_path):
                    with open(description_path, "r") as desc_file:
                        description = desc_file.read().strip()

                if not video_path:
                    print(f"[Warning] No video file found in {folder_path} for {platform}.")
                    continue
                if not description:
                    print(f"[Warning] No description file found in {folder_path} for {platform}.")
                    continue

                try:
                    print(f"Scheduling post for {account} on {platform}: {video_path}, {description}, {time}, {date}")
                    if platform == "instagram":
                        driver.get(
                            "https://business.facebook.com/latest/reels_composer?ref=biz_web_home_create_reel&context_ref=HOME"
                        )

                        schedule_function(driver, video_path, description, date, time)
                    elif platform == "youtube":
                        driver.get("https://studio.youtube.com/channel/")
                        schedule_function(driver, video_path, description, date, time)
                    else:
                        driver.get("https://www.tiktok.com/@astronomos8")
                        schedule_function(driver, video_path, description, time, date, "United States")

                    # Mark the post as scheduled and update the calendar
                    post["scheduled"] = True
                    update_post_status(calendar_file, account, post)

                except Exception as e:
                    print(f"[Error] Failed to schedule post for {account} on {platform}: {e}")

schedule_functions = {
    "tiktok": schedule_on_tiktok,
    "instagram": schedule_on_ig,
    "youtube": schedule_on_youtube
}

unscheduled_posts = get_unscheduled_posts('../database/calendar.json')


schedule_posts(unscheduled_posts, schedule_functions, '../database/calendar.json')

