import json

from flask import Flask, request, redirect, url_for
import boto3
from doc_processor import process_document

app = Flask(__name__)

S3_BUCKET = "claim-documents-poc-yit"
s3_client = boto3.client("s3")

@app.route("/")
def home():
    return '''
        <h2>Upload Document to S3</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Upload</button>
        </form>
    '''

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        return "No file selected", 400
    s3_client.upload_fileobj(file, S3_BUCKET, file.filename)
    return f'''
        <p>Uploaded <b>{file.filename}</b> to s3://{S3_BUCKET}/</p>
        <form action="/process/{S3_BUCKET}/{file.filename}" method="get">
            <button type="submit">Process Document</button>
        </form>
        <a href="/">Upload another</a>
    '''

@app.route("/process/<string:bucket>/<string:key>")
def process_documents(bucket, key):
    result = process_document(bucket, key)
    return f'''
        <h2>Processing Result</h2>
        <pre>{json.dumps(result, indent=2)}</pre>
        <a href="/">Back</a>
    '''


if __name__ == "__main__":
    app.run(debug=True, port=5001)
