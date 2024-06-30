import os
import sqlite3
import datetime
from googleapiclient.discovery import build
from pytube import YouTube

# Replace with your own API key
API_KEY = 'YOUR_YOUTUBE_API_KEY'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Initialize YouTube API client
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

def get_trending_videos(max_results=10):
    # Call the API to get trending videos
    request = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        chart='mostPopular',
        regionCode='US',  # Adjust region as needed
        maxResults=max_results
    )
    response = request.execute()
    return response['items']

def download_video(video_url, output_path='downloads'):
    yt = YouTube(video_url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    stream.download(output_path)

def setup_database(db_path='trending_videos.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
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

def save_video_info(video_info, db_path='trending_videos.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO videos (id, title, description, publishedAt, channelId, channelTitle, videoUrl, downloadPath)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        video_info['id'],
        video_info['title'],
        video_info['description'],
        video_info['publishedAt'],
        video_info['channelId'],
        video_info['channelTitle'],
        video_info['videoUrl'],
        video_info['downloadPath']
    ))
    conn.commit()
    conn.close()

def main():
    setup_database()
    trending_videos = get_trending_videos()

    for video in trending_videos:
        video_id = video['id']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        title = video['snippet']['title']
        description = video['snippet']['description']
        published_at = video['snippet']['publishedAt']
        channel_id = video['snippet']['channelId']
        channel_title = video['snippet']['channelTitle']
        
        print(f'Downloading: {title}')
        
        download_path = os.path.join('downloads', f'{video_id}.mp4')
        download_video(video_url, 'downloads')
        
        video_info = {
            'id': video_id,
            'title': title,
            'description': description,
            'publishedAt': published_at,
            'channelId': channel_id,
            'channelTitle': channel_title,
            'videoUrl': video_url,
            'downloadPath': download_path
        }
        
        save_video_info(video_info)

if __name__ == '__main__':
    main()
