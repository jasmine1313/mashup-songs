from flask import Flask, request, render_template
import re
import urllib.request
import pandas as pd
import random
from pytube import YouTube
from pydub import AudioSegment
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pydub import AudioSegment

# Set the path to the FFmpeg executable
AudioSegment.ffmpeg = "C:/ffmpeg/ffmpeg-6.0.tar.xz"  # Specify the correct path to ffmpeg executable

# Rest of your code

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/result', methods=['POST'])
def result():
    singer_name = request.form['singer_name']
    number_of_videos = int(request.form['number_of_videos'])
    duration = int(request.form['duration'])
    file_name = request.form['file_name']
    email = request.form['email']

    singer_name = singer_name.lower()
    singer_name = singer_name.replace(" ", "") + "videosongs"

    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + singer_name)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

    l = len(video_ids)
    url = []
    for i in range(number_of_videos):
        url.append("https://www.youtube.com/watch?v=" + video_ids[random.randint(0, l - 1)])

    final_aud = AudioSegment.empty()
    for i in range(number_of_videos):
        audio = YouTube(url[i]).streams.filter(only_audio=True).first()
        audio.download(filename='Audio-' + str(i) + '.mp3')
        aud_file = str(os.getcwd()) + "/Audio-" + str(i) + ".mp3"
        file1 = AudioSegment.from_file(aud_file)
        extracted_file = file1[:duration * 60 * 1000] #minutes
        final_aud += extracted_file
        final_aud.export(file_name, format="mp3")
    
        
    msg = MIMEMultipart()
    msg['From'] = "xyz@gmail.com"
    msg['To'] = email
    msg['Subject'] = "Audio File"
    #msg.attach(MIMEText("Here is the extracted audio file as a zip."))
    part = MIMEBase('application', "zip")
    part.set_payload(open(file_name, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', file_name=file_name)
    msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login("youremail@gmail.com", "password") #confidential
        server.sendmail("youremail@gmail.com", email, msg.as_string())
        server.quit()
        print("Audio file sent successfully!")
    except Exception as e:
        print("Error:", e)
    return render_template('result.html', singer_name=singer_name, number_of_videos=number_of_videos, duration=duration, file_name=file_name)

if __name__ == '__main__':
    app.run(debug=True)

