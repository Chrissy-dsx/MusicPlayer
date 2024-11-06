import re
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import requests
from io import BytesIO

def get_playlist_top_songs(play_list_id):
    url = 'https://music.163.com/discover/toplist?id='+play_list_id
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the <ul> element that contains all song names
    song_list = soup.find('ul', class_='f-hide')

    # Initialize an empty list to store song names and song IDs
    songs = []

    # Extract each song name and song ID and add them to the list
    i = 0
    for song in song_list.find_all('a'):
        if i == 10:
            break
        i += 1
        song_name = song.text
        song_id = re.search(r'id=(\d+)', song['href']).group(1)
        songs.append({'Song_name': song_name, 'ID': song_id})

    # Create a DataFrame object
    df = pd.DataFrame(songs)

    # Save the DataFrame as an Excel file
    excel_filename = 'playlist_top_' + play_list_id + '.xlsx'
    df.to_excel(excel_filename, index=False)
    return df

def get_song_pic_url(play_list_id):
    excel_filename = 'playlist_top_' + play_list_id + '.xlsx'
    df = pd.read_excel(excel_filename)
    song_id = df['ID'].iloc[0]
    api_url_detail = f"http://music.163.com/api/song/detail/?id={song_id}&ids=%5B{song_id}%5D"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    try:
        # Get song details
        time.sleep(0.3)
        response_detail = requests.get(api_url_detail, headers=headers)
        response_detail.raise_for_status()  # Check if the request was successful
        music_detail_data = response_detail.json()
        song_pic_url = music_detail_data['songs'][0]['album']['picUrl']
        return song_pic_url
    except Exception as e:
        return f"Error obtaining music information: try again later or change your network{str(e)}"

def get_image(url):
    # Download the image from URL and open it
    response = requests.get(url)
    img_data = response.content
    img = Image.open(BytesIO(img_data))

    # Resize the image
    new_size = (150, 150)  # New dimensions
    img = img.resize(new_size)

    # Convert the image to a format usable by Tkinter
    photo = ImageTk.PhotoImage(img)
    return photo

def plot_top_songs(root):
    get_playlist_top_songs('19723756')  # Soar rankings
    get_playlist_top_songs('3779629')  # New rankings
    get_playlist_top_songs('2884035')  # Original rankings
    get_playlist_top_songs('3778678')  # Hot rankings
    # Read data from Excel files

    df = pd.read_excel('playlist_top_19723756.xlsx')
    soar_rankings = df['Song_name'][:10].values.tolist()
    df = pd.read_excel('playlist_top_3779629.xlsx')
    new_rankings = df['Song_name'][:10].values.tolist()
    df = pd.read_excel('playlist_top_2884035.xlsx')
    original_rankings = df['Song_name'][:10].values.tolist()
    df = pd.read_excel('playlist_top_3778678.xlsx')
    hot_rankings = df['Song_name'][:10].values.tolist()

    # Create a Tkinter window
    new = tk.Toplevel(root)
    new.title("Rankings")
    # Create a frame
    frame1 = tk.Frame(new, padx=20, pady=20)
    frame1.pack(side=tk.LEFT)
    frame2 = tk.Frame(new, padx=20, pady=20)
    frame2.pack(side=tk.LEFT)
    frame3 = tk.Frame(new, padx=20, pady=20)
    frame3.pack(side=tk.LEFT)
    frame4 = tk.Frame(new, padx=20, pady=20)
    frame4.pack(side=tk.LEFT)
    # crate rankings
    rising_label = tk.Label(frame1, text="Soar Rankings", font=("Helvetica", 14))
    cover_photo1=get_image(get_song_pic_url('19723756'))
    cover_label1 = tk.Label(frame1,image=cover_photo1)
    rising_label.pack()
    cover_label1.pack()
    for index, song in enumerate(soar_rankings, start=1):
        song_label = tk.Label(frame1, text=f"{index} {song} ")
        song_label.pack()
    new_label = tk.Label(frame2, text="New Rankings", font=("Helvetica", 14))
    cover_photo2=get_image(get_song_pic_url('3779629'))
    cover_label2 = tk.Label(frame2,image=cover_photo2)
    new_label.pack()
    cover_label2.pack()
    for index, song in enumerate(new_rankings, start=1):
        song_label = tk.Label(frame2, text=f"{index} {song} ")
        song_label.pack()
    original_label = tk.Label(frame3, text="Original Rankings", font=("Helvetica", 14))
    cover_photo3=get_image(get_song_pic_url('2884035'))
    cover_label3 = tk.Label(frame3,image=cover_photo3)
    original_label.pack()
    cover_label3.pack()
    for index, song in enumerate(original_rankings, start=1):
        song_label = tk.Label(frame3, text=f"{index} {song} ")
        song_label.pack()
    hot_label = tk.Label(frame4, text="Hot Rankings", font=("Helvetica", 14))
    cover_photo4=get_image(get_song_pic_url('3778678'))
    cover_label4 = tk.Label(frame4,image=cover_photo4)
    hot_label.pack()
    cover_label4.pack()
    for index, song in enumerate(hot_rankings, start=1):
        song_label = tk.Label(frame4, text=f"{index} {song} ")
        song_label.pack()

    new.mainloop()