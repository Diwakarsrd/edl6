# Face Similarity Detector with Gemini AI

This application uses Google's Gemini API to compare face images and determine if they show the same person.

## Setup Instructions

1. Get a Google AI API key from [Google AI Studio](https://aistudio.google.com/)
2. Set the API key as an environment variable:
   ```bash
   # On Windows (PowerShell)
   $env:GOOGLE_API_KEY="your-api-key-here"
   
   # On macOS/Linux
   export GOOGLE_API_KEY="your-api-key-here"
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```

## How to Use

1. Open your browser and go to `http://localhost:5000`
2. Upload two face images using the upload sections
3. Click "Compare Faces" to analyze the images
4. View the similarity results and AI-generated analysis

## How It Works

This application uses Google's Gemini AI to analyze facial features and determine similarity between two face images. The AI provides:
- Descriptions of each face
- A similarity score (0-100)
- Confidence level in the assessment
- Explanation of the reasoning
- Final verdict on whether the faces are the same person

## Dependencies

- Flask: Web framework
- Google Generative AI: For Gemini API access
- NumPy: For numerical operations
- Werkzeug: For utility functions

## Note

You need a valid Google AI API key for this application to work. The API key is not included in this repository for security reasons.