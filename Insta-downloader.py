import os
import sqlite3
from datetime import datetime, timedelta
import instaloader

# Initialize Instaloader
L = instaloader.Instaloader()

def login_instagram(username, password):
    L.login(username, password)

def get_reels_by_hashtag(hashtag, days=1):
    hashtag_posts = instaloader.Hashtag.from_name(L.context, hashtag).get_posts()
    reels = []
    since = datetime.now() - timedelta(days=days)
    for post in hashtag_posts:
        if post.date >= since and post.typename == 'GraphVideo':
            reels.append(post)
    return reels

def download_reel(reel, output_path='downloads'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    L.download_post(reel, output_path)

def setup_database(db_path='viral_reels.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reels (
            id TEXT PRIMARY KEY,
            shortcode TEXT,
            username TEXT,
            description TEXT,
            timestamp TEXT,
            video_url TEXT,
            download_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_reel_info(reel_info, db_path='viral_reels.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO reels (id, shortcode, username, description, timestamp, video_url, download_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        reel_info['id'],
        reel_info['shortcode'],
        reel_info['username'],
        reel_info['description'],
        reel_info['timestamp'],
        reel_info['video_url'],
        reel_info['download_path']
    ))
    conn.commit()
    conn.close()

def main():
    # Replace with your Instagram credentials
    username = 'YOUR_INSTAGRAM_USERNAME'
    password = 'YOUR_INSTAGRAM_PASSWORD'
    
    # Hashtag to search for viral reels
    hashtag = 'viralreels'
    
    # Login to Instagram
    login_instagram(username, password)
    
    # Setup database
    setup_database()
    
    # Fetch reels
    reels = get_reels_by_hashtag(hashtag)
    
    for reel in reels:
        reel_info = {
            'id': reel.mediaid,
            'shortcode': reel.shortcode,
            'username': reel.owner_username,
            'description': reel.caption,
            'timestamp': reel.date_utc.isoformat(),
            'video_url': f'https://www.instagram.com/p/{reel.shortcode}/',
            'download_path': os.path.join('downloads', f'{reel.shortcode}.mp4')
        }
        
        print(f'Downloading: {reel.shortcode} by {reel.owner_username}')
        
        download_reel(reel, 'downloads')
        save_reel_info(reel_info)

if __name__ == '__main__':
    main()
