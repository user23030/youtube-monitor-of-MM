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

def get_stats():
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.videos().list(
        part='snippet,statistics',
        id=','.join(VIDEO_IDS)
    )
    response = request.execute()
    
    data = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    for item in response['items']:
        data.append({
            'date': now,
            'title': item['snippet']['title'],
            'views': item['statistics'].get('viewCount', 0),
            'likes': item['statistics'].get('likeCount', 0),
            'comments': item['statistics'].get('commentCount', 0)
        })
    return data

# CSVに保存（追記モード）
df_new = pd.DataFrame(get_stats())
if os.path.exists('youtube_stats.csv'):
    df_old = pd.read_csv('youtube_stats.csv')
    df_final = pd.concat([df_old, df_new], ignore_index=True)
else:
    df_final = df_new

df_final.to_csv('youtube_stats.csv', index=False)
