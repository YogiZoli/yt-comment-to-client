#!/usr/bin/env python3
"""
YouTube Comment-to-Client Polling Script
YT Comment-to-Client Plugin v0.2.0
https://github.com/YogiZoli/yt-comment-to-client

HOW IT WORKS:
  1. Runs hourly via Cowork scheduler (~2 API units per check)
  2. Compares latest video ID with last_video_state.json
     - No new video -> exits in <2 seconds
     - New video detected -> runs full comment poll on ALL channel videos
  3. Filters out troll/negative comments (no reply sent)
  4. Posts a randomised reply with UTM-tracked landing page link
  5. Logs everything to Google Sheet defined in config.json

CONFIG: config.json  (same directory as this script)
STATE:  last_video_state.json  (same directory)
"""

import os, json, random, time, re, datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import gspread

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'config.json')
TOKEN_FILE  = os.path.join(SCRIPT_DIR, 'token.json')
CREDS_FILE  = os.path.join(SCRIPT_DIR, 'client_secrets.json')
STATE_FILE  = os.path.join(SCRIPT_DIR, 'last_video_state.json')

try:
    with open(CONFIG_FILE) as f:
        _cfg = json.load(f)
except FileNotFoundError:
    print("ERROR: config.json not found. Run the setup skill first.")
    raise SystemExit(1)

CHANNEL_ID      = _cfg['channel_id']
KEYWORD         = _cfg.get('keyword', 'GUIDE')
LANDING_URL     = _cfg['landing_url']
SHEET_ID        = _cfg['sheet_id']
REPLY_DELAY_MIN = _cfg.get('reply_delay_min', 120)
REPLY_DELAY_MAX = _cfg.get('reply_delay_max', 900)

TROLL_PATTERNS = [
    r'\bscam\b', r'\bfake\b', r'\bspam\b', r'\bbot\b',
    r'\bstupid\b', r'\bidiot\b', r'\bwaste\b', r'\bterrible\b',
    r'\bworthless\b', r'\bfraud\b', r'\bscammer\b',
    r'\U0001F92E', r'\U0001F44E',
]

REPLY_VARIANTS = _cfg.get('reply_variants', [
    "@{name}, here's your free guide \U0001F447 {link}",
    "@{name} here you go — your free guide is ready \U0001F447 {link}",
    "@{name}, just as promised \U0001F3AF {link}",
    "@{name} — download your free guide here \U0001F447 {link}",
    "Hey @{name}, your guide is live \U0001F447 {link}",
    "@{name}, caught your comment! Here's the guide \U0001F447 {link}",
    "@{name} — here it is, enjoy! \U0001F447 {link}",
    "@{name}, this one's for you \U0001F381 {link}",
    "@{name} your free guide is one click away \U0001F447 {link}",
    "@{name}, here's what you asked for \U0001F447 {link}",
])

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/spreadsheets',
]

def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return creds

def local_now():
    return datetime.datetime.now(datetime.timezone.utc)

def is_troll(text):
    t = text.lower()
    return any(re.search(p, t) for p in TROLL_PATTERNS)

def has_keyword(text):
    return KEYWORD.lower() in text.lower()

def utm_link(video_id):
    return f"{LANDING_URL}?utm_source=youtube&utm_medium=comment&utm_campaign={video_id}"

def pick_reply(author, video_id):
    return random.choice(REPLY_VARIANTS).format(name=author, link=utm_link(video_id))

def load_last_video_id():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f).get('last_video_id')
        except Exception:
            pass
    return None

def save_last_video_id(video_id):
    with open(STATE_FILE, 'w') as f:
        json.dump({'last_video_id': video_id,
                   'updated_at': local_now().isoformat()}, f)

def get_processed_ids(sheet):
    try:
        rows = sheet.get_all_records()
        return {r['comment_id'] for r in rows if str(r.get('reply_sent', '')) == 'TRUE'}
    except Exception:
        return set()

def poll_and_reply():
    _creds = get_credentials()
    _yt    = build('youtube', 'v3', credentials=_creds)
    _ch    = _yt.channels().list(part='contentDetails', id=CHANNEL_ID).execute()
    _upl   = (_ch.get('items', [{}])[0]
              .get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads'))
    _latest = None
    if _upl:
        _r = _yt.playlistItems().list(part='snippet', playlistId=_upl, maxResults=1).execute()
        if _r.get('items'):
            _latest = _r['items'][0]['snippet']['resourceId']['videoId']

    _last = load_last_video_id()
    if _latest and _latest == _last:
        print(f"[{local_now().strftime('%H:%M UTC')}] No new video — skipping. ({_latest})")
        return
    if _latest:
        print(f"[{local_now().strftime('%H:%M UTC')}] New video: {_latest} — running full poll...")
        save_last_video_id(_latest)

    creds = get_credentials()
    yt    = build('youtube', 'v3', credentials=creds)
    gc    = gspread.authorize(creds)
    sheet = gc.open_by_key(SHEET_ID).sheet1
    processed = get_processed_ids(sheet)

    ch_resp  = yt.channels().list(part='contentDetails', id=CHANNEL_ID).execute()
    uploads  = (ch_resp.get('items', [{}])[0]
                .get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads'))
    videos = []
    if uploads:
        req = yt.playlistItems().list(part='snippet', playlistId=uploads, maxResults=50)
        while req and len(videos) < 500:
            resp = req.execute()
            for item in resp.get('items', []):
                s = item['snippet']
                videos.append({'id': {'videoId': s['resourceId']['videoId']},
                               'snippet': {'title': s['title'], 'publishedAt': s['publishedAt']}})
            req = yt.playlistItems().list_next(req, resp)

    print(f"Monitoring {len(videos)} videos...")

    for item in videos:
        vid_id    = item['id']['videoId']
        vid_title = item['snippet']['title']
        pub_str   = item['snippet']['publishedAt']
        try:
            ct = yt.commentThreads().list(
                part='snippet', videoId=vid_id, order='time', maxResults=100
            ).execute()
        except Exception as e:
            print(f"  Could not fetch comments for {vid_id}: {e}")
            continue

        for thread in ct.get('items', []):
            snip   = thread['snippet']['topLevelComment']['snippet']
            cid    = thread['id']
            author = snip['authorDisplayName']
            ch_url = snip.get('authorChannelUrl', '')
            text   = snip['textDisplay']
            if cid in processed or not has_keyword(text):
                continue
            if is_troll(text):
                print(f"  Troll skipped: {text[:60]}")
                sheet.append_row([vid_id, vid_title, pub_str, cid, author,
                                   ch_url, text, 'TRUE', 'troll', 'FALSE', '', '', ''])
                processed.add(cid)
                continue
            delay = random.randint(REPLY_DELAY_MIN, REPLY_DELAY_MAX)
            print(f"  Replying to @{author} in {delay}s...")
            time.sleep(delay)
            reply = pick_reply(author, vid_id)
            link  = utm_link(vid_id)
            try:
                yt.comments().insert(part='snippet', body={'snippet': {
                    'parentId': cid, 'textOriginal': reply}}).execute()
                ts = local_now().isoformat()
                print(f"  Replied to @{author} on '{vid_title}'")
                sheet.append_row([vid_id, vid_title, pub_str, cid, author,
                                   ch_url, text, 'TRUE', 'positive', 'TRUE', reply, ts, link])
                processed.add(cid)
            except Exception as e:
                print(f"  Reply failed for {cid}: {e}")

    print("Poll complete.\n")

if __name__ == '__main__':
    poll_and_reply()
