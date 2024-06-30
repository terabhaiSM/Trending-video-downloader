import os
import sqlite3
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from pytube import YouTube

# Replace with your own API key
API_KEY = 'YOUR_YOUTUBE_API_KEY'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Initialize YouTube API client
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

def get_trending_shorts(max_results=10):
    # Define the time frame for the past 24 hours
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    published_after = yesterday.isoformat("T") + "Z"
    
    # Call the API to get trending shorts (using videoCategoryId for Shorts if applicable)
    request = youtube.search().list(
        part='snippet',
        type='video',
        chart='mostPopular',
        regionCode='US',  # Adjust region as needed
        videoCategoryId='shorts',
        publishedAfter=published_after,
        maxResults=max_results
    )
    response = request.execute()
    return response['items']

def download_short(video_url, output_path='downloads'):
    yt = YouTube(video_url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    stream.download(output_path)

def setup_database(db_path='trending_shorts.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shorts (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            publishedAt TEXT,
            channelId TEXT,
            channelTitle TEXT,
            videoUrl TEXT,
            downloadPath TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_short_info(short_info, db_path='trending_shorts.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO shorts (id, title, description, publishedAt, channelId, channelTitle, videoUrl, downloadPath)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        short_info['id'],
        short_info['title'],
        short_info['description'],
        short_info['publishedAt'],
        short_info['channelId'],
        short_info['channelTitle'],
        short_info['videoUrl'],
        short_info['downloadPath']
    ))
    conn.commit()
    conn.close()

def main():
    setup_database()
    trending_shorts = get_trending_shorts()

    for short in trending_shorts:
        video_id = short['id']['videoId']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        title = short['snippet']['title']
        description = short['snippet']['description']
        published_at = short['snippet']['publishedAt']
        channel_id = short['snippet']['channelId']
        channel_title = short['snippet']['channelTitle']
        
        print(f'Downloading: {title}')
        
        download_path = os.path.join('downloads', f'{video_id}.mp4')
        download_short(video_url, 'downloads')
        
        short_info = {
            'id': video_id,
            'title': title,
            'description': description,
            'publishedAt': published_at,
            'channelId': channel_id,
            'channelTitle': channel_title,
            'videoUrl': video_url,
            'downloadPath': download_path
        }
        
        save_short_info(short_info)

if __name__ == '__main__':
    main()
