import requests
from django.conf import settings
import json
import time
from urllib.parse import urljoin
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError
from speechmatics.models import ConnectionSettings

API_KEY = settings.SPEECHMATICS_API_KEY

LANGUAGE = "ru"

settings = ConnectionSettings(
    url="https://eu.asr.api.speechmatics.com/v2",
    auth_token=API_KEY,
)

# Define transcription parameters
conf = {
    "type": "transcription",
    "transcription_config": {
        "language": LANGUAGE,
        "diarization": "speaker"}
}
def transcribe_audio(file_path):
    with BatchClient(settings) as client:
        try:
            job_id = client.submit_job(
                audio=file_path,
                transcription_config=conf,
            )
            print(f'job {job_id} submitted successfully, waiting for transcript')

            transcript = client.wait_for_completion(job_id, transcription_format='txt')
        except HTTPStatusError as e:
            if e.response.status_code == 401:
                print('Invalid API key - Check your API_KEY at the top of the code!')
            elif e.response.status_code == 400:
                print(e.response.json()['detail'])
            else:
                raise e
        print(transcript)
        return transcript