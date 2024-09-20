from flask import Flask, request, jsonify, render_template
import openai
from youtube_transcript_api import YouTubeTranscriptApi
import os

# Initialize the Flask app
app = Flask(__name__)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Route to serve the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Function to fetch YouTube transcript
def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([item['text'] for item in transcript])
        return full_transcript
    except Exception as e:
        return None

# Function to generate YouTube metadata using GPT-4 Chat API
def chatgpt_generate(transcript):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Replace with "gpt-4" or "gpt-3.5-turbo" if needed
            messages=[
                {"role": "system", "content": "You are an assistant that helps generate metadata for YouTube videos."},
                {"role": "user", "content": f"Generate YouTube headline, tags, description, and timestamps from this transcript:\n\n{transcript}"}
            ],
            max_tokens=500
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return str(e)

# Route to handle transcript generation
@app.route('/generate', methods=['POST'])
def generate():
    youtube_url = request.json['youtube_url']

    # Extract video ID from the YouTube URL
    video_id = youtube_url.split("v=")[1] if "v=" in youtube_url else youtube_url.split("/")[-1]

    # Fetch the transcript using YouTube API
    transcript = fetch_transcript(video_id)
    if transcript:
        # Generate metadata using GPT-4
        gpt_output = chatgpt_generate(transcript)
        return jsonify({'success': True, 'gpt_output': gpt_output})
    else:
        return jsonify({'success': False, 'message': 'Transcript not available'})

if __name__ == '__main__':
    app.run(debug=True)
