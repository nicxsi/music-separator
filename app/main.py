import asyncio
import os
import shutil
import subprocess
from functools import partial

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

# The folder where we will temporarily store the uploaded files
UPLOAD_DIR = "../uploads"   # we accept files from the user here
OUTPUT_DIR = "../outputs"   # this is where demucs puts the result
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac"}


app = FastAPI()


@app.get("/")
def read_root():
    html_content = "<h2>Music Separator</h2>"
    return HTMLResponse(content=html_content)


@app.post("/separate")
async def separate(file: UploadFile = File(...)):
    """
    Upload user file and save to storage.
    """

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    # Open a clean file on the server to write "wb" (write binary)
    with open(file_path, "wb") as buffer:
        # Copy the contents of the uploaded file to our file on the server
        shutil.copyfileobj(file.file, buffer)

    print(f"[DEBUG] Запускаю demucs для: {file_path}")

    loop = asyncio.get_event_loop()
    with open("demucs.log", "w") as log:
        result = await loop.run_in_executor(
            None,
            partial(
                subprocess.run,
                ["demucs", "-o", OUTPUT_DIR, file_path, "--mp3"],
                stdout=log,
                stderr=log
            )
        )

    # We are waiting for completion by transferring control back to the event loop
    stem_name = os.path.splitext(file.filename)[0]

    if result.returncode == 0:
        return {"message": "Success", "job_id": stem_name}
    else:
        raise HTTPException(
            status_code=500, 
            detail="Demucs separation failed. Check demucs.log for details."
        )
