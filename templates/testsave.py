from flask import Flask, render_template, jsonify, send_file
import mysql.connector
import base64
from io import BytesIO

app = Flask(__name__)

# Connect to MySQL database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mehul201472",
    database="Project_ISS"
)

def get_db_connection():
    return connection

@app.route('/')
def home():
    return render_template('animate.html')

@app.route('/retrieve_images')
def retrieve_images():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT image_data FROM images")  
        images = cursor.fetchall()
        cursor.close()

        # Prepare a list to store the image data
        image_data_list = []

        # Iterate through the images and encode the image data as base64
        for image in images:
            image_data = image[0]
            # Encode the image data to base64 string
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            image_data_list.append(encoded_image)

        return jsonify(image_data_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_audio_files')
def get_audio_files():
    try:
        # Retrieve all audio files from the database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT title FROM audio_library")
        audio_files = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        # Prepare a list of dictionaries with 'title' keys
        audio_files_list = [{'title': title} for title in audio_files]

        return jsonify(audio_files_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Route to retrieve and play an audio file
@app.route('/play/<title>')
def play_audio(title):
    try:
        # Retrieve audio file from the database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT audio_data FROM audio_library WHERE title = %s", (title,))
        audio_data = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        # Send the audio file for playback
        return send_file(BytesIO(audio_data), mimetype='audio/mp3', as_attachment=True, download_name=f'{title}.mp3')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
