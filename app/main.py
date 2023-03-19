from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import date
from sqlalchemy import create_engine
import re
from flask import Flask


from selenium.webdriver.chrome.options import Options




app = Flask(__name__)


@app.route("/scrape")
def scrape():
    options = Options()
    options.add_argument("--headless")
    engine = create_engine('postgresql://postgres:postgrespw@localhost:32768/Ghana_YT_Trending', echo=True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    driver.get("https://www.youtube.com/feed/trending?bp=6gQJRkVleHBsb3Jl")
    videos = driver.find_elements(By.CLASS_NAME, 'style-scope ytd-video-renderer')
    video_list = []
    for video in videos:
        title = video.find_element(By.ID, 'video-title').text
        description = video.find_element(By.ID, 'description-text').text
        views = video.find_element(By.XPATH, './/*[@id="metadata-line"]/span[1]').text
        channel_name = video.find_element(By.CLASS_NAME, 'style-scope ytd-channel-name').text
        # title = title.str.encode('ascii', 'ignore').str.decode('ascii')
        # description = description.str.encode('ascii', 'ignore').str.decode('ascii')
        # views = views.str.encode('ascii', 'ignore').str.decode('ascii')
        # channel_name = channel_name.str.encode('ascii', 'ignore').str.decode('ascii')
        today = date.today()
        vid_items = {
            'title': re.sub("[^\w\s]", "", title.lower()),
            'channel_name': re.sub("[^\w\s]", "", channel_name.lower()),
            'description': re.sub("[^\w\s]", "", description.lower()),
            'views': re.sub("[^\w\s]", "", views.lower()),
            'date': today
        }

        video_list.append(vid_items)

    df = pd.DataFrame(video_list)

    df = df.drop_duplicates(['title', 'channel_name', 'description', 'date'], inplace=False)

    df = df.astype(str).apply(lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))
    driver.quit()
    return df.to_json()


@app.route("/")
def home():

    return("hello")