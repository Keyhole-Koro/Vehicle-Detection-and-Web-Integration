import requests
import numpy as np

def fetchSnapshot(urls = ['https://img1.wsimg.com/isteam/ip/e2cee288-4555-474a-aa0b-21382ac1a006/AB-Tests-for-Low-Traffic-Sites-few-cars-on-roa.png', 
'https://media.licdn.com/dms/image/C5112AQFEvUvPobiSQw/article-cover_image-shrink_720_1280/0/1531285631513?e=2147483647&v=beta&t=aBO7TLyO9y6hohWi7I2ajfhqULSeKNkP5o_4jNsjFbA']):
    images = []
    for url in urls:
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                images.append(np.frombuffer(response.content, np.uint8))
            else:
                print(f"Failed to fetch image from {url}")
        except Exception as e:
            print(f"An error occurred while fetching image from {url}: {e}")
    return images