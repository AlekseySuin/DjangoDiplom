import os
import cv2
import ffmpeg
import whisper
import tempfile
from pyannote.audio import Pipeline
from deepface import DeepFace
from collections import defaultdict
from django.conf import settings


def extract_audio(input_video, output_audio):
    (
        ffmpeg
        .input(input_video)
        .output(output_audio, ac=1, ar=16000)
        .run(quiet=True)
    )


def diarize_audio(audio_file):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=settings.HF_TOKEN
    )
    return pipeline(audio_file)


def recognize_speakers(video_file, diarization):
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file {video_file}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    speaker_faces = defaultdict(list)

    for segment, _, speaker in diarization.itertracks(yield_label=True):
        frame_time = (segment.start + segment.end) / 2
        frame_pos = int(frame_time * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
        ret, frame = cap.read()

        if not ret:
            continue

        try:
            faces = DeepFace.extract_faces(frame, detector_backend="opencv")
            if faces:
                speaker_faces[speaker].append(faces[0]["face"])
        except Exception as e:
            print(f"Face detection error: {e}")

    cap.release()
    return speaker_faces


def map_speakers_to_names(speaker_faces):
    speaker_names = {}
    used_names = set()
    known_faces_path = getattr(settings, 'KNOWN_FACES_PATH', None)

    for speaker, faces in speaker_faces.items():
        if not faces:
            speaker_names[speaker] = speaker
            continue

        face = faces[0]
        try:
            if known_faces_path and os.path.exists(known_faces_path):
                recognition = DeepFace.find(
                    face,
                    db_path=known_faces_path,
                    enforce_detection=False
                )
                if recognition and not recognition[0].empty:
                    name = recognition[0].iloc[0]["identity"]
                    name = os.path.basename(name).split(".")[0]

                    if name in used_names:
                        suffix = 2
                        while f"{name}_{suffix}" in used_names:
                            suffix += 1
                        name = f"{name}_{suffix}"

                    speaker_names[speaker] = name
                    used_names.add(name)
                else:
                    speaker_names[speaker] = speaker
            else:
                speaker_names[speaker] = speaker
        except Exception as e:
            print(f"Face recognition error: {e}")
            speaker_names[speaker] = speaker

    return speaker_names


def transcribe_with_names(audio_file, diarization, speaker_names):
    model = whisper.load_model(getattr(settings, 'WHISPER_MODEL', 'medium'))
    transcription = []

    for segment, _, speaker in diarization.itertracks(yield_label=True):
        audio_segment = whisper.load_audio(audio_file)
        audio_segment = audio_segment[int(segment.start * 16000): int(segment.end * 16000)]

        text = model.transcribe(audio_segment, language="ru")["text"]
        name = speaker_names.get(speaker, speaker)
        transcription.append((name, segment.start, segment.end, text))

    return transcription


def process_video(input_video):
    try:
        # Создаем временный аудиофайл
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_temp:
            audio_path = audio_temp.name

        # Обработка
        extract_audio(input_video, audio_path)
        diarization = diarize_audio(audio_path)
        speaker_faces = recognize_speakers(input_video, diarization)
        speaker_names = map_speakers_to_names(speaker_faces)
        transcription = transcribe_with_names(audio_path, diarization, speaker_names)

        return transcription

    finally:
        if 'audio_path' in locals() and os.path.exists(audio_path):
            os.unlink(audio_path)