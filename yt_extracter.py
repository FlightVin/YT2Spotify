import time
import sys
import re
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class playlist_webpage(webdriver.Chrome):
    def __init__(self, base_url, num_vids) -> None:
        self.url = base_url
        self.num_vids = num_vids
        super().__init__()

    def open_playlist(self) -> None:
        self.get(self.url)

    def access_links(self) -> list:
        # scrolling page until all videos are visible
        cur_vid_count = 0
        while(cur_vid_count < self.num_vids):
            self.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(0.5)
            cur_vid_count = len(self.find_elements(By.CSS_SELECTOR, 'a#video-title'))

        # returning all things
        return self.find_elements(By.CSS_SELECTOR, 'a#video-title')[:self.num_vids]

# cleaning text - removing all text within () [] {}
def clean_text(text: str) -> str:
    pattern = r'\([^()]*\)|\{[^{}]*\}|\[[^\[\]]*\]'
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

# extracting song artist and title from video name
def extract_title(text: str, uploader: str) -> list:
    split_text = text.split("-", 1)

    if len(split_text) >= 2:
        artist_name = split_text[0].strip()
        song_title = split_text[1].strip()
    else:
        split_text = text.split("|", 1)
        if len(split_text) >= 2:
            artist_name = split_text[0].strip()
            song_title = split_text[1].strip()
        else:
            # manual entry
            print("\n", text, '--BY--', uploader.split("•")[0].strip())
            artist_name = input("Artist (hit enter if above is accurate): ")

            if (artist_name == ""): # if uploader name matches artist - hit enter
                artist_name = uploader.split("•")[0].strip()
                song_title = text
            else:
                song_title = input("Title: ")

    return artist_name, song_title

# saving to csv
def save_data_in_csv(data: list, filename: str):
    keys = data[0].keys()

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

if __name__ == '__main__':
    try:
        base_url = sys.argv[1]
        num_vids = int(sys.argv[2])
    except:
        print("Invalid number of arguments!")
        exit()
    print("Opening", base_url)

    # accessing webpage of playlist
    current_session = playlist_webpage(base_url, num_vids)
    current_session.open_playlist()

    # uncomment this line if you want to modify things on page (filters, etc.) before extracting
    # holder = input("Press enter to continue ")

    # accessing all videos
    vid_objs = current_session.access_links()
    vid_list = []

    for i in range(1, num_vids + 1):
        link = vid_objs[i-1]
        
        # extracting only useful parts of names
        vid_name = link.get_attribute('title')
        vid_name = clean_text(vid_name)

        uploader = link.find_element(By.XPATH, '../..//div[@id="byline-container"]').text
        vid_artist, vid_title = extract_title(vid_name, uploader)

        vid_link = link.get_attribute('href')
        vid_list.append({'artist': vid_artist, 'title': vid_title, 'url': vid_link})
        print(i, ':', vid_artist, '-', vid_title)

    save_data_in_csv(vid_list, "data.csv")

    
