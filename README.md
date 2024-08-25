# Web-Based Emotion-Driven Music Player

This project is a web-based music player that detects your emotions through a webcam feed and plays songs accordingly. It supports both mood-based playlists and user authentication. The application allows you to log in, view your current mood, and listen to music that matches your detected emotion.

## Features

- **Emotion Detection**: Uses your webcam to detect your current emotion and select music that matches your mood.
- **Spotify Integration**: Retrieves songs from Spotify based on the detected mood.
- **Song History**: Displays a history of songs played along with the mood detected at the time.
- **User Authentication**: Login system to authenticate users before accessing the music player.
- **Responsive UI**: A simple and user-friendly interface built with Bootstrap.

## Installation

1. **Clone the repository:**

   ```bash
   https://github.com/starlord78275/mpfer-music-player-using-facial-emotion-recognition-.git
   cd emotion-driven-music-player

**pip install -r requirements.txt**

Download the Haar Cascade file for face detection:

Download the haarcascade_frontalface_default.xml file and place it in the root directory of the project. You can get it from OpenCV's GitHub repository.

Set up Spotify API credentials:

You need to register your application with Spotify to get the client_id and client_secret. Once you have them, update the credentials in the Python script:

client_id = 'your_spotify_client_id'
client_secret = 'your_spotify_client_secret'

emotion-driven-music-player/
├── static/
│  
└── frame_latest.jpg   # Placeholder for the latest captured frame
├── templates/
│
├── index.html         # Main application interface
├── styles.css             # Custom CSS for the project
├── main.py                # Main Python script for running the server
└── README.md              # Project documentation (this file)


**Changing Genres:
**The emotion-to-genre mapping can be modified in the emotion_to_genre dictionary in 

emotion_to_genre = {
    "happy": "pop",
    "sad": "blues",
    "angry": "rock",
    "fear": "ambient",
    "disgust": "alternative",
    "surprise": "electronic",
    "neutral": "chill"
}
