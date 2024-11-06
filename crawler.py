from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import json
import os
import time

def get_playlist(play_list_id): 
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
    for song in song_list.find_all('a'):
        song_name = song.text
        song_id = re.search(r'id=(\d+)', song['href']).group(1)
        songs.append({'Song_name': song_name, 'ID': song_id})

        # Create a DataFrame object
        df = pd.DataFrame(songs)

        # Save the DataFrame as an Excel file
        df.to_excel('music_list.xlsx', index=False)
    return df

def get_lyrics(song_id):
    '''
    Retrieve lyrics based on song ID
    :param song_id: str
    :return: str
    '''
    link = 'http://music.163.com/api/song/media?id=' 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }

    if song_id != "":
        song_link = link + song_id
        web_data = requests.get(url=song_link, headers=headers).text
        json_data = json.loads(web_data)
        try:
            return json_data['lyric']
        except KeyError:
            return "The lyrics do not exist, please check the song ID and try again!"
        except Exception as e:
            return "Error: {}".format(str(e))
    else:
        return "The song ID is empty, please enter a valid song ID!"
    
def save_lyrics_to_file(lyrics, filename):
    filename = str(filename)
    directory = os.path.join(os.path.dirname(__file__), "lyrics")
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename + ".txt")
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(lyrics)
    print("The lyrics have been successfully saved to a file: " + filepath)
    
def get_music_information(song_id):
    '''
    Retrieve music information based on song ID
    :param song_id: str
    :return: str
    '''
    api_url_detail = f"http://music.163.com/api/song/detail/?id={song_id}&ids=%5B{song_id}%5D" 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    try:
        # Get song details
        time.sleep(2.5)
        response_detail = requests.get(api_url_detail, headers=headers)
        response_detail.raise_for_status()  # Check if the request was successful
        music_detail_data = response_detail.json()
        
        # Extract artist information
        artists = music_detail_data['songs'][0]['artists']
        artist_names = [artist['name'] for artist in artists]
        artist_info = ', '.join(artist_names)
        
        # Extract other information of interest
        song_name = music_detail_data['songs'][0]['name']
        album_name = music_detail_data['songs'][0]['album']['name']
        duration = music_detail_data['songs'][0]['duration']
        popularity = music_detail_data['songs'][0]['popularity']
        def seconds_to_minutes_and_seconds(milliseconds):
            seconds = milliseconds / 1000
            minutes = seconds // 60
            seconds %= 60
            return f"{int(minutes):02d}:{int(seconds):02d}"
        duration_in_correct_format=seconds_to_minutes_and_seconds(duration)
        #lyric = lyric_data.get('lrc', {}).get('lyric', '')
        
        # Store in DataFrame
        music_df = pd.DataFrame({
            'ID': [song_id],
            'Song_name': [song_name],
            'Album': [album_name],
            'Artist': [artist_info],
            'Duration': [duration_in_correct_format],
            'Popularity': [popularity]
            # 'Lyrics': [lyric]  # Commented out, as it is not included in the provided code snippet
        })
        print(music_df)
        return music_df
    except Exception as e:
        return f"Error obtaining music information: try again later or change your network{str(e)}"

def process_music_list(excel_filename):
    music_list = pd.read_excel(excel_filename)

    # Initialize an empty DataFrame to store music information
    music_information = pd.DataFrame(columns=['ID', 'Song_name', 'Album', 'Artist', 'Duration'])

    for index, row in music_list.iterrows():
        song_name = row['Song_name']
        song_id = row['ID']
        # Get lyrics
        lyrics = get_lyrics(str(song_id))  # Convert song_id to string
        save_lyrics_to_file(lyrics, song_id)

        # Get music information
        music_info = get_music_information(song_id)
        music_id = music_info['ID'][0]
        music_name = music_info['Song_name'][0]
        music_album = music_info['Album'][0]
        music_artist = music_info['Artist'][0]
        music_duration = music_info['Duration'][0]
        music_info_input = {
            'ID': music_id,
            'Song_name': music_name,
            'Album': music_album,
            'Artist': music_artist,
            'Duration': music_duration
        }
        # Add music information to DataFrame
        music_information = pd.concat([music_information, pd.DataFrame([music_info_input])], ignore_index=True)
        
        # Write the current music information to an Excel file
        music_information.to_excel('music_information.xlsx', index=False)
        time.sleep(2.5)

    # After the loop ends, write the entire DataFrame to an Excel file again
    music_information.to_excel('music_information.xlsx', index=False)

play_list_id=input("Enter the playlist ID: ") # hot song playlist id is 3778678, so just input 3778678 if you want to get the hot songs playlist
play_list = get_playlist(play_list_id)
time.sleep(10)
excel_filename="music_list.xlsx"
process_music_list(excel_filename)