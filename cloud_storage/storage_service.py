from google.cloud import storage
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/upload-screenshot")
def upload_screenshot(file_path: str, bucket_name: str):
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_path.split("/")[-1])
        blob.upload_from_filename(file_path)
        return {"message": "Screenshot uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
