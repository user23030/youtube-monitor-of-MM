import os
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build

# 設定
API_KEY = os.getenv('YOUTUBE_API_KEY')
VIDEO_IDS = [
    'AH7x78UqTDk', 'mROly8hbyFQ', '7Y9sJvLI3Po', '4FV-sT2_WB4',
    '7Ctjjdc92Ew', 'JFsahjfoAQ8', '2zilNT7hgFc', 'K64V4V_SGGQ'
]

def get_full_stats():
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # 1. まず動画の情報を取得（ここでチャンネルIDも手に入ります）
    video_request = youtube.videos().list(
        part='snippet,statistics',
        id=','.join(VIDEO_IDS)
    )
    video_response = video_request.execute()
    
    # チャンネルIDを重複なくリストアップ
    channel_ids = list(set([item['snippet']['channelId'] for item in video_response['items']]))
    
    # 2. チャンネルの情報を一括取得
    channel_request = youtube.channels().list(
        part='statistics',
        id=','.join(channel_ids)
    )
    channel_response = channel_request.execute()
    
    # チャンネル情報を辞書形式で整理（後で検索しやすくするため）
    channel_stats = {
        item['id']: {
            'subscribers': item['statistics'].get('subscriberCount', 0),
            'total_views': item['statistics'].get('viewCount', 0),
            'total_videos': item['statistics'].get('videoCount', 0)
        }
        for item in channel_response['items']
    }
    
    data = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 3. 動画データとチャンネルデータを合体させる
    for item in video_response['items']:
        c_id = item['snippet']['channelId']
        c_info = channel_stats.get(c_id, {})
        
        data.append({
            'date': now,
            'title': item['snippet']['title'],
            'views': item['statistics'].get('viewCount', 0),
            'likes': item['statistics'].get('likeCount', 0),
            'comments': item['statistics'].get('commentCount', 0),
            # チャンネル情報（追加分）
            'channel_subscribers': c_info.get('subscribers', 0),
            'channel_total_views': c_info.get('total_views', 0),
            'channel_total_videos': c_info.get('total_videos', 0)
        })
    return data

# CSVに保存（追記モード）
df_new = pd.DataFrame(get_full_stats())
if os.path.exists('youtube_stats.csv'):
    df_old = pd.read_csv('youtube_stats.csv')
    df_final = pd.concat([df_old, df_new], ignore_index=True)
else:
    df_final = df_new

df_final.to_csv('youtube_stats.csv', index=False)
