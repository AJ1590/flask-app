from flask import Flask, request, jsonify, render_template
import openai
from youtube_transcript_api import YouTubeTranscriptApi

# Initialize the Flask app
app = Flask(__name__)

# Set OpenAI API key (Replace with your actual OpenAI API key for Chat GPT Mini 4)
import os
openai.api_key = os.getenv("OPENAI_API_KEY")
# Function to fetch YouTube transcript
def fetch_transcript(video_id):
    try:
        # Fetch the transcript from YouTube using the video ID
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([item['text'] for item in transcript])
        return full_transcript
    except Exception as e:
        return None

# Function to generate YouTube metadata using GPT-4 Chat Completion API (Chat GPT Mini 4)
def chatgpt_generate(transcript):
    try:
        # Make the API call to Chat GPT Mini 4
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Use the mini version of GPT-4
            messages=[
                {"role": "system", "content": "You are an assistant that helps generate metadata for YouTube videos."},
                {"role": "user", "content": f"Generate YouTube headline, tags, description, and timestamps from this transcript:\n\n{transcript}"}
            ],
            max_tokens=500
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return str(e)

# Route to serve the frontend (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle transcript generation and metadata creation
@app.route('/generate', methods=['POST'])
def generate():
    youtube_url = request.json['youtube_url']

    # Extract video ID from the YouTube URL
    video_id = youtube_url.split("v=")[1] if "v=" in youtube_url else youtube_url.split("/")[-1]

    # Fetch the transcript using YouTube API
    transcript = fetch_transcript(video_id)
    if transcript:
        # Generate metadata using GPT-4 Mini
        gpt_output = chatgpt_generate(transcript)
        return jsonify({'success': True, 'gpt_output': gpt_output})
    else:
        return jsonify({'success': False, 'message': 'Transcript not available for this video or video has no captions enabled.'})

if __name__ == '__main__':
    app.run(debug=True)
