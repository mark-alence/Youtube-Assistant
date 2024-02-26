from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS
import os
from openai import OpenAI
from pytube import YouTube
import os
import whisper
import pandas as pd
import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")



app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set the OpenAI API key
os.environ["OPENAI_API_KEY"] = "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"



def simplify_text(text):
    doc = nlp(text)
    simplified_sentences = []
    for sentence in doc.sents:
        simplified_sentences.append(' '.join(token.text for token in sentence if not token.is_stop and not token.is_punct))
    return ' '.join(simplified_sentences)

def download_audio(url, mp3_file):
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()

    # Print details about the audio stream
    print("Audio Stream Details:", audio_stream)

    # Create temp directory if it doesn't exist
    temp_directory = 'temp'
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)

    # Download the audio stream
    try:
        output_path = audio_stream.download(output_path=temp_directory, filename='temp_audio')
        print("Downloaded to:", output_path)
    except Exception as e:
        raise Exception(f"An error occurred while downloading audio: {e}")

    # Check if the file exists
    if not os.path.exists(output_path):
        raise Exception(f"Failed to download audio. File at {output_path} does not exist.")

    # Rename the file to MP3
    os.rename(output_path, mp3_file)


def transcribe_mp3(file_path, tsv_file_path):
    # Load the model
    model = whisper.load_model("base")

    # Process the audio file and generate the transcript
    result = model.transcribe(file_path)
    print(result, 'yeeee')

    # Prepare data for the CSV file
    data = [{
        'start_time': segment['start'],
        'end_time': segment['end'],
        'text_snippet': segment['text']
    } for segment in result['segments']]

    # Save the segments to a CSV file
    df = pd.DataFrame(data)
    df.to_csv(tsv_file_path, sep=',', index=False, encoding='utf-8')

    # Save the full transcript to a text file
    with open("output.txt", "w", encoding='utf-8') as text_file:
        text_file.write(result["text"])

    # Return the full transcript
    return result["text"]


# URL of the YouTube video
# url = 'https://www.youtube.com/watch?v=Nh1Atlw8iXs'
#
# Path for the output MP3 file
# mp3_path = 'output_audio.mp3'

# Download and convert to MP3
# try:
#     download_audio(url, mp3_path)
#     print("Conversion complete. MP3 file saved as:", mp3_path)
# except Exception as e:
#     print(e)


@app.route('/create_thread', methods=['GET'])
def create_thread():

    try:
        url = request.args.get('url', '')
        client = OpenAI()
        mp3_path = 'output_audio.mp3'
        download_audio(url, mp3_path)

        try:
            transcript = transcribe_mp3(mp3_path, 'output.csv')
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 500

        file = client.files.create(
            file=open("output.csv", "rb"),
            purpose='assistants'
        )
        file2 = client.files.create(
            file=open("output.txt", "rb"),
            purpose='assistants'
        )

        assistant = client.beta.assistants.create(
            name="Youtube Guide",
instructions = """
    You are an assistant tasked with assisting users in summarizing, understanding, and navigating through information from YouTube videos, supported by the output.csv file detailing segments within the video. The file has columns "start_time, end_time, and text_snippet" .

    When a user requests where in the video a topic is brought up, come up with relevant search terms and analyze the .csv file content to identify relevant video segments. Content is in the text_snippet column. Handle timestamps in decimal form by rounding down to the nearest whole number.

    For each identified timestamp, present a clickable link directing the user to that specific time in the video. Format the link as follows: [start_time_in_seconds]({url}&t=start_time_in_seconds), where "start_time_in_seconds" is an integer of the rounded-down timestamp.

    Accompany each link with a brief context from the "text_snippet" column, summarizing the segment's content in a concise manner. Ensure the context provided is clear and directly related to the user's query.

    Example response format:
    - "Brief context of the segment": [6]({url}&t=6)

    Ensure links and context are presented clearly and concisely, making it easy for users to navigate directly to the relevant parts of the video.



    When a user asks about the content of the video, use output.txt to provide a summary of the video content. The summary should be concise and informative, providing a clear understanding of the video's content.
    Do not mention the existence of any of the files in the response.

    Note in  your response, you are responding to the user watching the youtube video. The user does not know about any of the files, so do not mention them.
    """.format(url=url),

            tools=[{"type": "code_interpreter"}],
            model="gpt-4-turbo-preview",
            file_ids=[file.id, file2.id]

        )

        thread = client.beta.threads.create()
        print(thread.id, assistant.id)
        return jsonify({"thread_id": thread.id, "assistant_id": assistant.id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
