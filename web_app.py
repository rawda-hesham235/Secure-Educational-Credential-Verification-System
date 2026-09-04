from flask import Flask, render_template, request, redirect, url_for
from blockchain import Blockchain
import os
import hashlib
import torch
from torchvision import transforms
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
blockchain = Blockchain()

# Load AI model
model = torch.jit.load('colab/model_scripted.pt', map_location=torch.device('cpu'))
model.eval()

# Load labels
with open('colab/label.txt', 'r') as f:
    labels = [line.strip() for line in f.readlines()]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('verify.html', error="No file uploaded")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('verify.html', error="No file selected")
        
        try:
            file_data = file.read()
            block = blockchain.check_file(file_data)
            return render_template('verify.html', block=block, filename=file.filename)
        except Exception as e:
            return render_template('verify.html', error=str(e))
    
    return render_template('verify.html')

@app.route('/signature-check', methods=['GET', 'POST'])
def signature_check():
    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template('signature.html', error="No image uploaded")
        
        image = request.files['image']
        if image.filename == '':
            return render_template('signature.html', error="No image selected")
        
        try:
            # Save uploaded image
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(img_path)
            
            # Preprocess image
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize( mean=[0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225])
            ])

            img = Image.open(img_path).convert('RGB')
            img_tensor = transform(img).unsqueeze(0)

            # Make prediction
            with torch.no_grad():
                output = model(img_tensor)
                _, pred = torch.max(output, 1)
                result = labels[pred.item()]
            
            return render_template('signature.html', 
                                 result=result,
                                 img_path=img_path)
       
        except Exception as e:
            return render_template('signature.html', error=str(e))

    return render_template('signature.html')

if __name__ == '__main__':
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        app.run(debug=True, port=4000)           