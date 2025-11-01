from flask import Flask, request, redirect, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# --- הגדרות ראשוניות ---
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_flask_secret_key_here")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "https://spotifyy-zeta.vercel.app/"  # חשוב לעדכן לפי Render
SCOPE = "user-read-recently-played"

# --- דף הבית ---
@app.route('/')
def index():
    if 'token_info' not in session:
        return render_template('index.html', logged_in=False)
    else:
        sp = spotipy.Spotify(auth=session['token_info']['access_token'])
        results = sp.current_user_recently_played(limit=10)
        tracks = [{
            'artist': item['track']['artists'][0]['name'],
            'name': item['track']['name'],
            'album': item['track']['album']['name']
        } for item in results['items']]
        return render_template('index.html', logged_in=True, tracks=tracks)

# --- התחברות לספוטיפיי ---
@app.route('/login')
def login():
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI,
                            scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# --- חזרה מספוטיפיי ---
@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI,
                            scope=SCOPE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

