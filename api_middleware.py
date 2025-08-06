import os
import shutil
import uuid
import httpx # Library for HTTP Request Asynchronous
import sys

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

# Configuration
sys.path.append(".")

# Initialize API
app = FastAPI(
    title="Ling Tien Kung HAR Middleware API",
    description="Middleware API to forward video processing",
    version="1.0.0"
)

# COLAB WORKER CONFIG
# NOTE : PLEASE CHANGE THE ADDRESS BASED ON NGROK OUTPUT ON YOUR COLAB
COLAB_WORKER_URL = "http://localhost:8001"
PROCESS_ENDPOINT = "/process_video/" # Endpoint

TEMP_DIR = "temp_middleware_files"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/predict_activity/")
async def predict_activity(video_file: UploadFile = File(...)):
    if not video_file.filename.endswith(('.mp4', '.avi', '.mov')):
        raise HTTPException(status_code=400, detail="Hanya video berformat MP4, AVI, atau MOV")
    
    # Save video
    unique_id = str(uuid.uuid4())
    input_video_path = os.path.join(TEMP_DIR, f"{unique_id}_{video_file.filename}")

    try:
        with open(input_video_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        print(f"Video temporary saved in middleware : {input_video_path}")

        # Pass the video into colab worker
        print(f"Send video into Colab Worker with URL {COLAB_WORKER_URL}{PROCESS_ENDPOINT}")
        async with httpx.AsyncClient(timeout=300.0) as client : # Timeout if connection not success
            with open(input_video_path, "rb") as f:
                files = {
                    'video_file': (
                        video_file.filename, f, video_file.content_type
                    )
                }
                response = await client.post(f"{COLAB_WORKER_URL}{PROCESS_ENDPOINT}", files=files)
        # HTTP Exception Status will be shown if status code 4xx or 5xx
        response.raise_for_status()

        # Saved video from colab worker
        output_filename = f"annotated_{video_file.filename}"
        output_video_path = os.path.join(TEMP_DIR, output_filename)

        with open(output_video_path, "wb") as buffer:
            buffer.write(response.content)
        print(f"Video Accepted from Google Colab Worker and saved in : {output_video_path}")

        # Response video to user
        return FileResponse(output_video_path, media_type="video/mp4", filename=output_filename)

    except httpx.HTTPStatusError as e:
        print(f"Error from Colab Worker : {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from Colab Worker: {e.response.text}")
    except httpx.RequestError as e:
        print(f"Connection failed to Colab Worker : {e}")
        raise HTTPException(status_code=503, detail=f"Connection failed into video process service. Please check if the server active or URL is correct!")
    except Exception as e:
        print(f"An error occured in middleware : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error")
    finally:
        # Delete temporary data to make storage not full
        if os.path.exists(input_video_path):
            os.remove(input_video_path)
        # Delete output video (annotated video)
        if os.path.exists(output_video_path):
            os.remove(output_video_path)
        print("Temporary file has been deleted in middleware.")

            