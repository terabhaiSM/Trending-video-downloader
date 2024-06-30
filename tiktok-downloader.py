import os
import sqlite3
from datetime import datetime, timedelta
from TikTokApi import TikTokApi

# Initialize TikTok API
api = TikTokApi.get_instance()

def get_trending_tiktoks(max_results=10):
    trending_videos = api.trending(count=max_results)
    return trending_videos

def download_tiktok(video_url, output_path='downloads'):
    # Use TikTokApi to download the video
    video_data = api.get_video_by_url(video_url)
    video_id = video_url.split('/')[-1]
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with open(os.path.join(output_path, f'{video_id}.mp4'), 'wb') as f:
        f.write(video_data)

def setup_database(db_path='trending_tiktoks.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tiktoks (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            publishedAt TEXT,
            username TEXT,
            videoUrl TEXT,
            downloadPath TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_tiktok_info(tiktok_info, db_path='trending_tiktoks.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO tiktoks (id, title, description, publishedAt, username, videoUrl, downloadPath)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        tiktok_info['id'],
        tiktok_info['title'],
        tiktok_info['description'],
        tiktok_info['publishedAt'],
        tiktok_info['username'],
        tiktok_info['videoUrl'],
        tiktok_info['downloadPath']
    ))
    conn.commit()
    conn.close()

def main():
    setup_database()
    trending_tiktoks = get_trending_tiktoks()

    for tiktok in trending_tiktoks:
        video_id = tiktok['id']
        video_url = tiktok['video']['playAddr']
        title = tiktok['desc']
        description = tiktok['desc']
        published_at = datetime.utcfromtimestamp(tiktok['createTime']).isoformat()
        username = tiktok['author']['uniqueId']
        
        print(f'Downloading: {title} by {username}')
        
        download_path = os.path.join('downloads', f'{video_id}.mp4')
        download_tiktok(video_url, 'downloads')
        
        tiktok_info = {
            'id': video_id,
            'title': title,
            'description': description,
            'publishedAt': published_at,
            'username': username,
            'videoUrl': video_url,
            'downloadPath': download_path
        }
        
        save_tiktok_info(tiktok_info)

if __name__ == '__main__':
    main()
