import fitz  # PyMuPDF
from google.cloud import storage
from flask import Flask, request, jsonify
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer
import nltk
import os

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

app = Flask(__name__)

# Set the path to your service account key file
key_file_path = "fifth-compass-415612-76f634511b19.json"

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path

# Function to preprocess text
def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text)
    # Remove punctuation and lowercase the tokens
    tokens = [word.lower() for word in tokens if word.isalpha()]
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

# Function to calculate similarity score
def calculate_similarity(context_keywords, resume_text):
    # Preprocess resume text
    resume_tokens = preprocess_text(resume_text)
    # Calculate frequency distribution of resume tokens
    resume_freq_dist = FreqDist(resume_tokens)
    # Calculate similarity score based on intersection of context keywords and resume tokens
    intersection = len(set(context_keywords) & set(resume_tokens))
    score = intersection / len(context_keywords)
    return score

@app.route('/process-resumes', methods=['POST'])
def process_resumes():
    try:
        # Get JSON data from request
        data = request.json
        # Extract parameters from JSON data
        context = data.get("context")
        num_matches = int(data.get("noOfMatches"))
        input_path = data.get("inputPath")
        
        # Extract context keywords
        context_tokens = preprocess_text(context)
        
        # Initialize Google Cloud Storage client
        storage_client = storage.Client()
        bucket_name = "hackathontestdata2024"
        bucket = storage_client.bucket(bucket_name)
        
        # Get list of blobs (PDF files) in the specified path
        blobs = bucket.list_blobs()
        
        # Process each resume and calculate similarity score
        results = []
        file_count = 0  # Counter to track the number of files downloaded
        for blob in blobs:
            if blob.name.endswith(".pdf"):  # Ensure it's a PDF file
                pdf_content = blob.download_as_string()
                # Extract text from PDF content
                text = ""
                with fitz.open(stream=pdf_content, filetype="pdf") as doc:
                    for page in doc:
                        text += page.get_text()
                
                # Calculate similarity score
                score = calculate_similarity(context_tokens, text)
                
                # Append results
                results.append({"id": blob.name, "score": score, "path": blob.name})
                # file_count += 1  # Increment file count
                
         # Sort results by score in descending order
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Select top matches
        top_matches = results[:num_matches]
        
        # Create response
        response = {
            "status": "success",
            "count": len(top_matches),
            "metadata": {
                "confidenceScore": top_matches[0]['score'] if top_matches else 0  # Confidence score of top match
            },
            "results": top_matches
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Import the test class
import testClass

if __name__ == '__main__':
    app.run(debug=True)
