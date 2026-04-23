import os
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build

# ==========================================
# 設定
# ==========================================
API_KEY = os.getenv('YOUTUBE_API_KEY')
VIDEO_IDS = [
    'AH7x78UqTDk', 'mROly8hbyFQ', '7Y9sJvLI3Po', '4FV-sT2_WB4',
    '7Ctjjdc92Ew', 'JFsahjfoAQ8', '2zilNT7hgFc', 'K64V4V_SGGQ'
]

def get_full_stats():
    # YouTube API サービスの構築
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # 1. 動画の情報を取得 (タイトル, 再生数, 高評価, コメント数, チャンネルID)
    video_request = youtube.videos().list(
        part='snippet,statistics',
        id=','.join(VIDEO_IDS)
    )
    video_response = video_request.execute()
    
    # 今回取得した動画が属するチャンネルIDのリスト（重複排除）
    channel_ids = list(set([item['snippet']['channelId'] for item in video_response['items']]))
    
    # 2. チャンネルの情報を取得 (登録者数, 総再生数, 投稿本数)
    channel_request = youtube.channels().list(
        part='statistics',
        id=','.join(channel_ids)
    )
    channel_response = channel_request.execute()
    
    # チャンネル情報を辞書形式で整理 { 'チャンネルID': {データ} }
    channel_map = {
        item['id']: {
            'ch_subscribers': item['statistics'].get('subscriberCount', 0),
            'ch_total_views': item['statistics'].get('viewCount', 0),
            'ch_total_videos': item['statistics'].get('videoCount', 0)
        }
        for item in channel_response['items']
    }
    
    # 3. データの統合
    data_list = []
    # 取得時刻を日本時間に近い形（またはUTC）で固定
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    for item in video_response['items']:
        v_stats = item['statistics']
        v_snippet = item['snippet']
        c_id = v_snippet['channelId']
        c_info = channel_map.get(c_id, {})
        
        data_list.append({
            'date': now_str,
            'title': v_snippet['title'],
            'video_id': item['id'],
            'views': v_stats.get('viewCount', 0),
            'likes': v_stats.get('likeCount', 0),
            'comments': v_stats.get('commentCount', 0),
            # チャンネル側の数値
            'channel_subscribers': c_info.get('ch_subscribers', 0),
            'channel_total_views': c_info.get('ch_total_views', 0),
            'channel_total_videos': c_info.get('ch_total_videos', 0)
        })
    
    return data_list

# ==========================================
# メイン処理: データの取得とCSV保存
# ==========================================
def main():
    print("データ取得を開始します...")
    new_stats = get_full_stats()
    df_new = pd.DataFrame(new_stats)
    
    file_name = 'youtube_stats.csv'
    
    # 既存のCSVがあれば読み込んで結合
    if os.path.exists(file_name):
        print(f"既存の {file_name} にデータを追記します。")
        df_old = pd.read_csv(file_name)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        print(f"新しく {file_name} を作成します。")
        df_final = df_new
    
    # 保存
    df_final.to_csv(file_name, index=False, encoding='utf-8-sig')
    print("保存が完了しました。")

if __name__ == "__main__":
    main()
