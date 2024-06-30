import os
import sqlite3
import time
from instabot import Bot

# Initialize the bot
bot = Bot()

def login_instagram(username, password):
    bot.login(username=username, password=password)

def comment_on_posts(hashtag, comment_text, max_posts=10):
    media_ids = bot.get_hashtag_medias(hashtag, amount=max_posts)
    for media_id in media_ids:
        bot.comment(media_id, comment_text)
        print(f"Commented on post {media_id}")
        save_activity('comment', media_id, comment_text)
        time.sleep(2)  # To avoid being flagged as spam

def send_dm_to_followers(username, dm_text, max_dms=10):
    user_id = bot.get_user_id_from_username(username)
    followers = bot.get_user_followers(user_id, nfollows=max_dms)
    for follower in followers:
        bot.send_message(dm_text, [follower])
        print(f"Sent DM to user {follower}")
        save_activity('dm', follower, dm_text)
        time.sleep(2)  # To avoid being flagged as spam

def setup_database(db_path='bot_activity.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            target_id TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_activity(activity_type, target_id, message, db_path='bot_activity.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO activities (type, target_id, message)
        VALUES (?, ?, ?)
    ''', (activity_type, target_id, message))
    conn.commit()
    conn.close()

def main():
    # Replace with your Instagram credentials
    username = 'YOUR_INSTAGRAM_USERNAME'
    password = 'YOUR_INSTAGRAM_PASSWORD'
    
    # Login to Instagram
    login_instagram(username, password)
    
    # Setup database
    setup_database()

    # Define the service promotion details
    hashtag = 'examplehashtag'
    comment_text = 'Check out our amazing service at example.com!'
    dm_text = 'Hello! We are offering an amazing service that you might be interested in. Visit example.com for more details.'

    # Comment on posts with the specified hashtag
    print("Starting to comment on posts...")
    comment_on_posts(hashtag, comment_text)
    
    # Send DMs to followers
    print("Starting to send DMs to followers...")
    send_dm_to_followers(username, dm_text)

if __name__ == '__main__':
    main()
