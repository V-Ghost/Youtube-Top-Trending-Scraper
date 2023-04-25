from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import date

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import date

from datetime import datetime
from airflow import DAG
from airflow.decorators import task



with DAG(
    dag_id="demo_dag",
    start_date=datetime(2022, 1, 1),
    schedule="0 0 * * *"
) as dag:

    @task()
    def test_airflow():
        # Extract
        engine = create_engine(
            'postgresql://postgres:postgrespw@localhost:32768/Ghana_YT_Trending', echo=True)
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()))
        driver.get("https://www.youtube.com/feed/trending?bp=6gQJRkVleHBsb3Jl")
        videos = driver.find_elements(By.CLASS_NAME, 'style-scope ytd-video-renderer')
        video_list = []
        for video in videos:
            title = video.find_element(By.ID, 'video-title').text
            description = video.find_element(By.ID, 'description-text').text
            views = video.find_element(
                By.XPATH, './/*[@id="metadata-line"]/span[1]').text
            channel_name = video.find_element(
                By.CLASS_NAME, 'style-scope ytd-channel-name').text
            today = date.today()
            vid_items = {
                'Title': title,
                'Channel name': channel_name,
                'Description': description,
                'Views': views,
                'Date': str(today)
            }
            video_list.append(vid_items)
        df = pd.DataFrame(video_list)


        # Remove duplicates
        df = df.drop_duplicates(
            ['Title', 'Channel name', 'Description', 'Date'], inplace=False)
        # Create ID column based on index
        df['id'] = df.index
        # Applies lambda function on dataframe that converts data to lowercase
        # if data is a str
        df = df.applymap(lambda s: s.lower() if isinstance(s, str) else s)
        # Remove all characters that are neither numbers,strings nor whitespaces
        df = df.replace('[^\w\s]', '', regex=True)
        # Converts a dataFrame to a string data type and then applies a
        # function to each element of the DataFrame to remove non-ASCII characters.
        df = df.astype(str).apply(lambda x: x.str.encode(
            'ascii', 'ignore').str.decode('ascii'))

        # print(df)
        #
        # writer = pd.ExcelWriter('trending.xlsx')
        # df.to_excel(writer)
        # writer.close()

        # Append dataframe into sql table if it exists, if not create sql table
        df.to_sql('daily_trending_videos', engine, if_exists='append', index=False)

# def predict:

test_airflow()
