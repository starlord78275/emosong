import cv2
from fer import FER
import tempfile
import os
import random
import pygame
import threading
import http.server
import socketserver
import time
import requests
import json
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

# Spotify API credentials
client_id = '5084271cea7549e191b858229e281e61'
client_secret = '7fa5f923c6964256ac6d601e74d30043'

# Set up Spotipy
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# Initialize Pygame mixer
pygame.mixer.init()

# Emotion to genre mapping
emotion_to_genre = {
    "happy": "amv happy",
    "sad": "bollywood sad",
    "angry": "trending phonk",
    "fear": "bollywood fear",
    "disgust": "bollywood disgust",
    "surprise": "bollywood surprise",
    "neutral": "chill"
}

# Global variables to store song info and history
current_track = {"name": "", "artist": "", "image_url": "", "mood": "", "frame": ""}
song_history = []
played_tracks = set()  # Set to track played tracks

# Function to download and cache the track
def download_and_cache_track(track_url):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file_path = temp_file.name
            response = requests.get(track_url)
            response.raise_for_status()
            temp_file.write(response.content)
        return temp_file_path
    except Exception as e:
        print(f"Error downloading track: {str(e)}")
        return None

# Function to play a track
def play_track(track_url, image_url):
    try:
        temp_file_path = download_and_cache_track(track_url)
        if not temp_file_path:
            print("Failed to download track.")
            return

        pygame.mixer.music.load(temp_file_path)
        pygame.mixer.music.play()
        print("Playing track...")

        # Update current track with image URL
        current_track["image_url"] = image_url

        while pygame.mixer.music.get_busy():
            continue

        os.remove(temp_file_path)
    except Exception as e:
        print(f"Error playing track: {str(e)}")

# Function to search and play a random Spotify track based on the detected emotion
def search_and_play_random_track(emotion):
    genre = emotion_to_genre.get(emotion, "bollywood")
    results = sp.search(q=genre, type='track', limit=10)

    if results['tracks']['items']:
        tracks = results['tracks']['items']
        random.shuffle(tracks)

        available_tracks = [track for track in tracks if track['id'] not in played_tracks]

        if not available_tracks:
            print("All tracks have been played. Resetting the list.")
            played_tracks.clear()
            available_tracks = tracks

        for track in available_tracks:
            preview_url = track['preview_url']
            if preview_url:
                image_url = track['album']['images'][0]['url']
                print(f"Playing track: {track['name']} by {track['artists'][0]['name']}")

                current_track.update({
                    "name": track['name'],
                    "artist": track['artists'][0]['name'],
                    "image_url": image_url,
                    "mood": emotion,
                    "frame": current_track.get("frame")  # Make sure the frame is the latest one
                })

                # Save the current track to history
                song_history.insert(0, current_track.copy())
                # Limit history to the latest 10 entries
                if len(song_history) > 10:
                    song_history.pop()

                played_tracks.add(track['id'])
                play_track(preview_url, image_url)
                return

        print("No tracks with a preview URL were found for the selected emotion.")
    else:
        print("No tracks found for your selected emotion.")

# Function to capture frames and detect emotions
def capture_and_detect_emotions():
    cascade_path = "haarcascade_frontalface_default.xml"

    if not os.path.exists(cascade_path):
        raise FileNotFoundError(f"Haar cascade file not found at path: {cascade_path}")

    detector = FER(mtcnn=False, cascade_file=cascade_path)
    cap = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                print("Failed to capture image")
                continue

            result = detector.detect_emotions(frame)
            if result:
                face = result[0]
                emotions = face["emotions"]
                emotion = max(emotions, key=emotions.get)
                print(f"Detected emotion: {emotion} with confidence {emotions[emotion]}")

                # Save the frame with a timestamp to ensure a new frame each time
                timestamp = int(time.time())
                frame_path = f"static/frame_{timestamp}.jpg"
                cv2.imwrite(frame_path, frame)

                # Update the current track with the new frame path and detected mood
                current_track.update({
                    "frame": frame_path,
                    "mood": emotion
                })

                # Play a track based on the detected emotion
                search_and_play_random_track(emotion)

            time.sleep(10)

    finally:
        cap.release()

# HTTP server to handle client requests
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        elif self.path == '/update':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "current": current_track,
                "history": song_history
            }).encode())
        else:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length).decode('utf-8')

        if "Pause" in post_data:
            pygame.mixer.music.pause()
        elif "Next" in post_data:
            pygame.mixer.music.stop()
            search_and_play_random_track("neutral")
        elif "mood" in post_data:
            mood = post_data.split('=')[1]
            pygame.mixer.music.stop()
            search_and_play_random_track(mood)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

def run_server():
    PORT = 8000
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

# Start the emotion detection in a separate thread
threading.Thread(target=capture_and_detect_emotions, daemon=True).start()

# Start the server
run_server()
