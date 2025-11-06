#!/usr/bin/env python3
"""
Face Similarity Detection Application
This application uses Google's Gemini API to compare face images,
without traditional ML models.
"""

import os
import base64
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

# Configure Gemini API with provided key
genai.configure(api_key='AIzaSyABNw_BGiTGp6rFsrD2ksWKa8dQ6qRUW_Y')

app = Flask(__name__)

# Use absolute path for upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_path):
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def compare_faces_with_gemini(image1_path, image2_path):
    """Compare two faces using Gemini API"""
    import json
    import re
    
    # Encode both images
    image1_base64 = encode_image(image1_path)
    image2_base64 = encode_image(image2_path)
    
    # Create the model
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Prepare the prompt
    prompt = """
    You are an expert at analyzing facial images for biometric comparison. I'm providing you with two face images.
    Please analyze both images and determine if they show the same person.
    
    Focus on:
    1. Facial structure (jawline, cheekbones, forehead)
    2. Eye shape and placement
    3. Nose shape and size
    4. Mouth and lip characteristics
    5. Facial proportions
    
    IMPORTANT: Respond ONLY with a valid JSON object in this exact format:
    {"image1_description": "Brief description of face in image 1", "image2_description": "Brief description of face in image 2", "similarity_score": 75, "confidence": "high", "explanation": "Brief explanation of your reasoning", "verdict": "Same Person"}
    
    The similarity_score should be a number from 0-100 where:
    - 0-30: Very different faces
    - 31-50: Probably different faces
    - 51-70: Possibly the same person
    - 71-85: Likely the same person
    - 86-100: Very likely the same person
    
    Do not include any other text, markdown, or formatting. Only return the JSON object.
    """
    
    # Send request to Gemini
    response = model.generate_content([
        prompt,
        {
            "mime_type": "image/jpeg",
            "data": image1_base64
        },
        {
            "mime_type": "image/jpeg", 
            "data": image2_base64
        }
    ])
    
    # Parse the response
    try:
        # Extract JSON from response
        import json
        import re
        
        # Try to find JSON in the response text
        response_text = response.text.strip()
        
        # Look for JSON object in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            return result
        else:
            # If no JSON found, return the raw response
            return {
                "error": "Failed to parse Gemini response - no JSON found",
                "raw_response": response_text
            }
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return the raw response
        return {
            "error": f"Failed to parse Gemini response as JSON: {str(e)}",
            "raw_response": response.text
        }
    except Exception as e:
        # Handle any other exceptions
        return {
            "error": f"Error processing Gemini response: {str(e)}",
            "raw_response": response.text if hasattr(response, 'text') else str(response)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Log request details for debugging
        print(f"Request files: {list(request.files.keys())}")
        print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
        print(f"Upload folder exists: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in request'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) if file.filename else 'unnamed'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure the upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            print(f"Saving file to: {filepath}")
            file.save(filepath)
            
            # Verify file was saved
            if os.path.exists(filepath):
                return jsonify({'filename': filename, 'uploaded': True})
            else:
                return jsonify({'error': 'File was not saved successfully'}), 500
        
        return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        # Log the full error for debugging
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Ensure we always return JSON even in case of errors
        return jsonify({'error': f'Error uploading file: {str(e)}'}), 500

@app.route('/compare', methods=['POST'])
def compare_images():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        image1 = data.get('image1')
        image2 = data.get('image2')
        
        if not image1 or not image2:
            return jsonify({'error': 'Both image1 and image2 are required'}), 400
        
        # Check if both images exist
        image1_path = os.path.join(app.config['UPLOAD_FOLDER'], image1)
        image2_path = os.path.join(app.config['UPLOAD_FOLDER'], image2)
        
        if not os.path.exists(image1_path) or not os.path.exists(image2_path):
            return jsonify({'error': 'One or both images not found'}), 404
        
        # Compare faces using Gemini API
        result = compare_faces_with_gemini(image1_path, image2_path)
        
        # Format the response
        if 'error' in result:
            return jsonify(result), 400
        
        # Add image names to the result
        result['image1'] = image1
        result['image2'] = image2
        
        # Convert similarity score to percentage if it's not already
        if 'similarity_score' in result and isinstance(result['similarity_score'], (int, float)):
            result['percentage'] = result['similarity_score']
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Error comparing images with Gemini: {str(e)}'}), 500

@app.route('/uploads')
def list_uploads():
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            return jsonify({'images': []})
        
        images = []
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                images.append(filename)
        
        return jsonify({'images': images})
    except Exception as e:
        return jsonify({'error': f'Error listing uploads: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        # Ensure the file exists
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': f'File {filename} not found'}), 404
        
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({'error': f'Error serving file {filename}: {str(e)}'}), 500

@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        file_deleted = False
        
        # Remove file from uploads directory
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            file_deleted = True
        
        if file_deleted:
            return jsonify({'message': f'File {filename} deleted successfully'})
        else:
            return jsonify({'error': f'File {filename} not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error deleting file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)