import time
import PyPDF2
from flask import Flask, render_template, request, url_for,redirect
from flask_bootstrap import Bootstrap5
import boto3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Bootstrap5(app)

os.makedirs(UPLOAD_FOLDER,exist_ok=True)

def text_to_mp3(text,filename):
    session = boto3.Session(
        aws_access_key_id="AKIATJID4B7H3IL66NPC",
        aws_secret_access_key="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",
        region_name="us-east-1",
    )

    polly = session.client('polly')

    response = polly.synthesize_speech(
        Text= text,
        OutputFormat = "mp3",
        VoiceId ="Brian"
    )

    output_path = os.path.join('static','uploads',filename)

    with open(output_path,'wb') as file:
        file.write(response['AudioStream'].read())




def extract_text(pdf_file):
    with open(pdf_file,'rb') as pdf:
        reader = PyPDF2.PdfReader(pdf,strict=False)
        pdf_text =[]
        for page in reader.pages:
            content = page.extract_text()
            pdf_text.append(content)

        return pdf_text


pdf_file = []
mp3_file=[]

@app.route('/')
def home():
    if mp3_file:
        name_file = mp3_file[len(mp3_file)-1]
        return render_template('index.html', audio=f"static/uploads/{name_file}")
    else:
        return render_template('index.html', audio=None)



@app.route('/upload', methods=['POST'])
def upload_file():
    mp3_file.append(request.form['output'])
    if 'file' not in request.files:
        return 'No file part in the form.'
    file = request.files['file']
    print(file)
    if file.filename == '':
        return 'No file selected.'
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    pdf_file.append(file.filename)
    text_to_extract = extract_text(f"uploads/{pdf_file[len(pdf_file)-1]}")
    for text_to_speech in text_to_extract:
        text = text_to_speech
        filename = request.form['output']
        text_to_mp3(text, filename)
    time.sleep(1)
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug= True)
