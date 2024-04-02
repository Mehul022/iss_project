from flask import Flask, render_template, flash,session, request, redirect, url_for,jsonify,send_file,send_from_directory
import mysql.connector
import hashlib
import os
import base64
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import mysql.connector
import moviepy.editor as mp
from moviepy.editor import VideoFileClip, concatenate_audioclips, AudioFileClip
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.fadein import fadein
import os
import shutil


app = Flask(__name__)
app.secret_key = 'your_secret_key' 
#MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mehul201472'
app.config['MYSQL_DB'] = 'Project_ISS'
app.config['UPLOAD_FOLDER']='static/UPLOADS'
def connect_to_mysql():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Mehul201472",
  database="Project_ISS"
)
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mehul201472',
    'database': 'Project_ISS',
}  
@app.route('/')
def home():
    if 'email' in session:
        return render_template('auto_login.html')
    else:
        return render_template('index2.html')

UPLOAD_FOLDER = 'static/UPLOADS'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

files_to_remove=[]

def save_images_to_database(image_info_list, user_id):
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor()

    try:
        for image_info in image_info_list:
            image_path = os.path.join(UPLOAD_FOLDER, image_info['filename'])
            cursor.execute("INSERT INTO images (size, extension, filename, image_path, user_id, image_data,imageduration) VALUES (%s,%s, %s, %s, %s, %s, %s)",
                           (image_info['size'], image_info['extension'], image_info['filename'], image_path, user_id, image_info['blob_data'],image_info['duration']))

    except mysql.connector.Error as error:
        print(f"Error saving images to database: {error}")
        connection.rollback()
        return False
    else:
        connection.commit()
        return True
    finally:
        cursor.close()
        connection.close()

@app.route('/save_video_info', methods=['POST'])
def save_video_info():
    # Connect to the database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mehul201472",
        database="Project_ISS"
    )
    
    try:
        # Delete existing data from the video_info table
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM video_info")
            connection.commit()

        # Extract data from the request
        video_quality = request.json.get('videoQuality')
        transition = request.json.get('transition')

        # Insert new data into the video_info table
        with connection.cursor() as cursor:
            sql = "INSERT INTO video_info (video_quality, transition) VALUES (%s, %s)"
            cursor.execute(sql, (video_quality, transition))
            connection.commit()

        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        # Close the database connection
        connection.close()


@app.route('/upload', methods=['POST'])
def upload():
    if 'files[]' in request.files:
        images = request.files.getlist('files[]')
        durations = request.form.getlist('durations[]')
        image_info_list = []
        for i,image in enumerate(images):
            if image.filename != '':
                blob_data = image.read()
                blob_size = len(blob_data)
                image_extension = image.filename.split('.')[-1].lower()
                image_duration = durations[i]
                image_info_list.append({'size': blob_size, 'extension': image_extension, 'filename': image.filename, 'blob_data': blob_data,'duration': image_duration})

        if image_info_list:
            if save_images_to_database(image_info_list,session['email']):
                redirect(url_for('animate'))
                return '' ,200
            else:
                return 'Failed to upload images to the database',500
    return 'No images uploaded'

def hash_password(password):
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256()
    hash_object.update(password_bytes)
    hashed_password = hash_object.hexdigest()
    return hashed_password

# MySQL connection configuration
@app.route('/retrieve_images')
def retrieve_images():
    try:
        user_id=session['email']
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mehul201472",
            database="Project_ISS"
        )
        # conn = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT image_data,imageduration FROM images where user_id=%s",(session['email'],))  
        images = cursor.fetchall()
        cursor.close()
        connection.close()
        # print(images)
        image_data_list = []

        # Iterate through the images and encode the image data as base64
        for image in images:
            image_data = image[0]
            filename=image[1]
            # Encode the image data to base64 string
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            image_data_list.append({'data': encoded_image, 'imageduration': filename})

        return jsonify(image_data_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_audio_files')
def get_audio_files():
    # print("dropbox")
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mehul201472",
            database="Project_ISS"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT title FROM audio_library")
        audio=cursor.fetchall()
        audio_files=[]
        for r in audio:
            audio_files.append(r)
        cursor.close()
        connection.close()
        
        # Prepare a list of dictionaries with 'title' keys
        audio_files_list = [{'title': title} for title in audio_files]

        return jsonify(audio_files_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login_submit', methods=['POST'])
def login_submit():
    if request.method == 'POST':
        email_id = request.form['email']
        hashed_password = request.form['password']
        if email_id=="Admin@admin.com" and hashed_password=="Admin" :
            return render_template('adminpage.html')
        # Check if the entered email and password match in the database
        if check_user_in_database(email_id, hashed_password):
            session['email'] = email_id
            return render_template('redirect_login.html')
        else:
            return render_template('login_success.html')

    return render_template('login.html')

def check_user_in_database(email, password):
    try:
        connection = connect_to_mysql()
        cursor = connection.cursor(dictionary=True)

        # Fetch user details from the 'users' table based on the entered email
        query = "SELECT * FROM users WHERE email_id = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        # Check if the user exists and the entered password matches
        if user:
            entered_password_hashed = hash_password(password)
            if user['hashed_password'] == entered_password_hashed:
                return True
        else:
            return False
    except mysql.connector.Error as error:
        print(f"Failed to check user in database: {error}")
        return False
    finally:
        # Close the cursor and database connection
        cursor.close()
        connection.close()
        
def check_user(email):
    try:
        connection = connect_to_mysql()
        cursor = connection.cursor(dictionary=True)

        # Fetch user details from the 'users' table based on the entered email
        query = "SELECT * FROM users WHERE email_id = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        if user:
            return True
        else:
            return False
    except mysql.connector.Error as error:
        print(f"Failed to check user in database: {error}")
        return False
    finally:
        # Close the cursor and database connection
        cursor.close()
        connection.close()
       
# Function to fetch audio files from the database

@app.route('/play/<audio_title>')
def play_audio(audio_title):
    # Assuming audio files are stored in a folder named "static/audio"
    audio_path = f'static/audio/{audio_title}'
    return audio_path

def hash_password(password):
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256()

    # Update the hash object with the password bytes
    hash_object.update(password_bytes)

    # Get the hexadecimal representation of the hashed password
    hashed_password = hash_object.hexdigest()

    return hashed_password
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email_id = request.form['email']
        hashed_password = request.form['password']
        passo = request.form['confirm_password']
        if check_user(email_id):
            return render_template('redirect_signup.html')
        if(hashed_password != passo):
            return render_template('password_fail.html')
        if store_user_in_database(email_id,hashed_password):
            session['email'] = email_id
            return render_template('signup_success.html')

    return render_template('Signup.html')


def store_user_in_database(email, password):

    try:
        connection = connect_to_mysql()
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        # Insert user details into the 'users' table
        query = "INSERT INTO users (email_id, hashed_password) VALUES (%s, %s)"
        cursor.execute(query, (email,hashed_password))

        # Commit the transaction
        connection.commit()
        return True
    finally:
        cursor.close()
        connection.close()

def save_audio_to_database(audio_info_list):
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor()
    try:
        for audio_info in audio_info_list:
            cursor.execute("INSERT INTO audio2 (audio_name, file_path, duration,user_id) VALUES (%s, %s, %s,%s)",
                           (audio_info['audio_title'], audio_info['filepath'], audio_info['duration'],session['email']))

    except mysql.connector.Error as error:
        print(f"Error saving audio to database: {error}")
        connection.rollback()
        return False
    else:
        connection.commit()
        return True
    finally:
        cursor.close()
        connection.close() 

@app.route('/upload_audio_blob2', methods=['POST'])
def upload_audio_blob2():
    # audio_titles = request.form.getlist('audio_title')  
    durations = request.form.getlist('durations')
    # print(audio_titles)
    # print(durations)
    connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mehul201472",
            database="Project_ISS"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT audio_name,file_path FROM audio")
    audio=cursor.fetchall()
    cursor.close()
    connection.close()
    audio_list = [list(row) for row in audio]
    audio_info_list = []
    for i, audio_file in enumerate(audio_list):
        # print(audio_file)
        # file_path="static/audio/"+audio_file
        # print(file_path)
        audio_info = {
            'audio_title': audio_file[0],
            'duration': durations[i],
            'filepath': audio_file[1]
        }
        # print(file_path)
        audio_info_list.append(audio_info)

    # Optionally, save audio information to the database
    if audio_info_list:
        save_audio_to_database(audio_info_list)

    return jsonify({'message': 'Audio files uploaded successfully'})

        # mycursor = mydb.cursor()
        # sql = "INSERT INTO audio (audio_name, file_path, duration) VALUES (%s, %s, %s)"
        # val = (audio, file_path, duration[i])
        # mycursor.execute(sql, val)
        # mydb.commit()
        # return jsonify({'message': 'Audio file uploaded successfully'}), 200

@app.route('/upload_audio_blob', methods=['POST'])
def upload_audio_blob():
    UPLOAD_FOLDER = 'static/UPLOADS'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    audio_file = request.files['audio']
    audio_title = request.form['audio_title']  
    duration = request.form['duration']
    if audio_file:
        filename = audio_file.filename
        file_path = f'static/audio/{filename}'
        audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        mycursor = mydb.cursor()
        sql = "INSERT INTO audio (audio_name, file_path, duration) VALUES (%s, %s, %s)"
        val = (audio_title, file_path, duration)
        mycursor.execute(sql, val)
        mydb.commit()
        return jsonify({'message': 'Audio file uploaded successfully'}), 200
    else:
        return jsonify({'error': 'No audio file found'}), 400

@app.route('/play2/<audioTitle>')
def play2_audio(audioTitle):
    # Assuming the audio files are stored in a folder named 'audio_files'
    audio_path = f'static/audio/{audioTitle}'
    with open(audio_path, 'rb') as audio_file:
        audio_data = audio_file.read()
    return audio_data

# Function to authenticate user credentials
@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    duration=request.form['duration']
    if 'audio' in request.files:
        audio_files = request.files.getlist('audio')
        for audio in audio_files:
            if audio.filename != '':
                filename = secure_filename(audio.filename)
                
                audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                audio.save(audio_path)
                # print(filename)
                # print(audio_path)  # Save the file to the UPLOADS folder
                # Additional processing or saving to the database can be done here if needed
                mycursor = mydb.cursor()
                sql = "INSERT INTO audio (audio_name, file_path, duration) VALUES (%s, %s, %s)"
                val=(filename,audio_path,duration)
                mycursor.execute(sql,val)
                mydb.commit()
        return 'Audio files uploaded successfully!'
    return 'No audio files uploaded'



@app.route('/home_login_delete')
def home_login_delete():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mehul201472",
        database="Project_ISS"
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM video_info")
            connection.commit()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM audio")
            connection.commit()
            audio_folder = "static/UPLOADS/"  # Replace with the actual path
            for filename in os.listdir(audio_folder):
                file_path = os.path.join(audio_folder, filename)
                os.remove(file_path)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM audio2")
            connection.commit()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM images")
            connection.commit()
            return render_template('home_login.html')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Function to authenticate user credentials

@app.route('/Signup')
def Signup():
    return render_template('Signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/Logout')
def Logout():
    session.pop('email', None)
    return render_template('index2.html')
@app.route('/video_page')
def video_page():
    return render_template('video_page.html')

@app.route('/video_preview')
def video_preview():
            return render_template('redirect_preview.html')
    # if request.method == 'POST':
@app.route('/video_preview2')
def video_preview2():
            connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mehul201472",
            database="Project_ISS"
            )
            cursor = connection.cursor()
            # Retrieve image data and duration from the database
            cursor.execute("SELECT image_data, imageduration FROM images")
            image_records = cursor.fetchall()

            # Retrieve audio paths and durations from the audio library
            cursor.execute("SELECT file_path, duration FROM audio2")
            audio_records = cursor.fetchall()

            cursor.execute("SELECT video_quality, transition FROM video_info")
            video_info = cursor.fetchone()

            video_quality, transition = video_info


            # Close the database connection
            # cursor.close()
            connection.close()

            # Define video parameters

            if video_quality=='720p':
                frame_width = 1280
                frame_height = 720
            elif video_quality=='1080p':
                frame_width = 1920
                frame_height = 1080
            elif video_quality=='360p':
                frame_width = 854
                frame_height = 480
            fps = 60

            # Create a list to store video frames
            video_frames = []

            # Create a list to store segment durations
            segment_durations = []

            # Iterate through each image record
            for image_data, image_duration in image_records:
                # Decode image data
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is not None:
                    img = cv2.resize(img, (frame_width, frame_height))
                    
                    # Repeat each frame for the specified duration
                    for _ in range(int(fps * image_duration)):
                        video_frames.append(img)
                        
                    # Add image duration to segment durations
                    segment_durations.append(image_duration)

            # Write video frames to a file
            output_video_path = 'output_video.mp4'
            out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))
            for frame in video_frames:
                out.write(frame)
            out.release()

            # Load background audio clips from the audio library
            background_audio_clips = []
            total_audio_duration = 0
            for audio_path, duration in audio_records:
                background_audio_clip = AudioFileClip(audio_path)
                background_audio_clip = background_audio_clip.subclip(0, duration)  # Trim audio clip to specified duration
                total_audio_duration += background_audio_clip.duration
                background_audio_clips.append(background_audio_clip)

            # Calculate the total video duration
            video_duration = len(video_frames) / fps

            if total_audio_duration > video_duration:
                excess_duration = total_audio_duration - video_duration
                for i, audio_clip in enumerate(reversed(background_audio_clips)):
                    if excess_duration > 0:
                        trim_duration = min(excess_duration, audio_clip.duration)
                        background_audio_clips[len(background_audio_clips) - i - 1] = audio_clip.subclip(trim_duration)
                        excess_duration -= trim_duration
                    else:
                        break

            # Concatenate all audio clips into a single composite audio clip
            final_audio_clip = concatenate_audioclips(background_audio_clips)

            # Repeat the composite audio clip if its duration is shorter than the video duration
            repetitions = int(np.ceil(video_duration / final_audio_clip.duration))
            final_audio_clip = concatenate_audioclips([final_audio_clip] * repetitions)

            # Trim the combined audio to match the video duration
            final_audio_clip = final_audio_clip.subclip(0, video_duration)

            # Load video clip
            video_clip = VideoFileClip(output_video_path)

            # Set composite audio for the video clip
            video_clip = video_clip.set_audio(final_audio_clip)

            # Save final video with composite audio
            final_output_path = 'final_output_video.mp4'
            video_clip.write_videofile(final_output_path, codec="libx264", fps=fps)

            # Load the initial video clip
            clip = mp.VideoFileClip(final_output_path)

            # Calculate the total duration of the video clip
            total_duration = sum(segment_durations)

            # Initialize a list to store the processed clips
            processed_clips = []

            # Iterate over each segment
            if transition=='Fade-In And Fade-Out':
                start_time = 0
                for duration in segment_durations:
                    # Select the segment and apply fade-in and fade-out effects
                    segment = clip.subclip(start_time, start_time + duration)
                    segment_with_fadein = segment.fx(fadein, duration=1)
                    segment_with_fadein_and_out = segment_with_fadein.fx(fadeout, duration=1)
                    
                    # Add the processed segment to the list
                    processed_clips.append(segment_with_fadein_and_out)
                    
                    # Update start time for the next segment
                    start_time += duration
                    
            elif transition=='Fade-In':
                start_time = 0
                for duration in segment_durations:
                    # Select the segment and apply fade-in and fade-out effects
                    segment = clip.subclip(start_time, start_time + duration)
                    segment_with_fadein = segment.fx(fadein, duration=1)
                    # Add the processed segment to the list
                    processed_clips.append(segment_with_fadein)
                    # Update start time for the next segment
                    start_time += duration
            elif transition=='Fade-Out':
                start_time = 0
                for duration in segment_durations:
                    # Select the segment and apply fade-in and fade-out effects
                    segment = clip.subclip(start_time, start_time + duration)
                    segment_with_fadeout = segment.fx(fadeout, duration=1)
                    # Add the processed segment to the list
                    processed_clips.append(segment_with_fadeout)
                    # Update start time for the next segment
                    start_time += duration
            elif transition=='Normal':
                start_time = 0
                for duration in segment_durations:
                    # Select the segment and apply fade-in and fade-out effects
                    segment = clip.subclip(start_time, start_time + duration)
                    # Add the processed segment to the list
                    processed_clips.append(segment)
                    # Update start time for the next segment
                    start_time += duration

            # Concatenate the processed clips without any transition
            final_clip = mp.concatenate_videoclips(processed_clips, method="compose")

            # Save the final output video
            output_path = 'output_video_with_fade.mp4'
            final_clip.write_videofile(output_path, codec="libx264", fps=clip.fps)
            static_audio_folder = 'static/videos'

            if os.path.exists(output_path):
                shutil.move(output_path, os.path.join(static_audio_folder, os.path.basename(output_path)))


            # Close the clips
            video_clip.close()
            final_audio_clip.close()
            final_clip.close()
            
        # except mysql.connector.Error as error:
        #     print(f"Error: {error}")
        #     return jsonify({'success': False, 'error': str(error)}), 500
            video_url = '/static/videos/output_video_with_fade.mp4'

            return render_template('video_preview.html', video_url=video_url) 
            # return render_template('video_preview.html')


@app.route('/retrieve_audios')
def retrieve_audios():
    try:
        # Fetch audio data from the database
        # audiodatalist = Audio.query.all()
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mehul201472",
            database="Project_ISS"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT audio_name,file_path,duration FROM audio2")
        audiodatalist=cursor.fetchall()
        # Convert the query result to a list of dictionaries
        audios = [{'filename': audio[0], 'filepath': audio[1], 'duration': audio[2]} for audio in audiodatalist]
        # print(audios)
        return jsonify(audios)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@app.route('/reset_images', methods=['POST'])
def reset_images():
    connection=connect_to_mysql()
    try:
        with connection.cursor() as cursor:
            # Delete all images from the database
            cursor.execute('DELETE FROM images')
        connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
@app.route('/home_login')
def home_login():
    return render_template('home_login.html')

@app.route('/dropbox')
def dropbox():
    return render_template('imagesel.html')

@app.route('/animate')
def animate():
    return render_template('animate.html')
# Route to render the success page
@app.route('/success')
def success():
    return render_template('home_login.html')

if __name__ == '__main__':
    app.run(debug=True)