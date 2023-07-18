## Imports
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import exceptions
import time
import io
import pandas as pd
import numpy as np
import csv
import sys
import os  # For cloud

## Function Definition
def scrapfyt(url):
    ## Opening chrome and URL
    option = webdriver.ChromeOptions()
    option.binary_location = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Update with your Chrome binary location
    option.add_argument('--headless')
    option.add_argument('-no-sandbox')
    option.add_argument("--mute-audio")
    option.add_argument("--disable-extensions")
    option.add_argument('-disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(executable_path="C:/chromedriver.exe"), options=option)  # Update with your Chrome driver path
    driver.set_window_size(960, 800)

    driver.get(url)
    time.sleep(2)

    ## Pause youtube video
    pause = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'ytp-play-button')))
    pause.click()
    time.sleep(0.2)
    pause.click()
    time.sleep(4)

    ## Scrolling through all the comments
    driver.execute_script("window.scrollBy(0,500)","")
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(4)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    ## Scraping details
    video_title = driver.find_element(By.NAME, 'title').get_attribute('content')

    video_owner1 = driver.find_elements(By.XPATH, '//*[@id="text"]/a')
    video_owner = []
    for owner in video_owner1:
        video_owner.append(owner.text)
    video_owner = video_owner[0]

    video_comment_with_replies = driver.find_element(By.XPATH, '//*[@id="count"]/yt-formatted-string/span[1]').text + ' Comments'

    users = driver.find_elements(By.XPATH, '//*[@id="author-text"]/span')
    comments = driver.find_elements(By.XPATH, '//*[@id="content-text"]')

    with io.open('comments.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter =",", quoting=csv.QUOTE_ALL)
        writer.writerow(["Username", "Comment"])
        for username, comment in zip(users, comments):
            writer.writerow([username.text, comment.text])
    
    commentsfile = pd.read_csv("comments.csv", encoding ="utf-8")
    all_comments = commentsfile.replace(np.nan, '-', regex=True)

    # Set the file path for saving the CSV file in the current directory
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, "Full Comments.csv")

    # Remove the file if it already exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Save the processed data in the CSV file
    all_comments.to_csv(file_path, index=False)

    video_comment_without_replies = str(len(commentsfile.axes[0])) + ' Comments'

    driver.close()

    return all_comments, video_title, video_owner, video_comment_with_replies, video_comment_without_replies


# Test the function with the given URL
#url = "https://www.youtube.com/watch?v=714w3HQDTcA"
#scrapfyt(url)

