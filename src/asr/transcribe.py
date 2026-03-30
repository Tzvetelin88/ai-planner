from __future__ import annotations

import tempfile
from pathlib import Path

try:
    from faster_whisper import WhisperModel
except ImportError:  # pragma: no cover
    WhisperModel = None

try:
    from vosk import KaldiRecognizer, Model
except ImportError:  # pragma: no cover
    KaldiRecognizer = None
    Model = None


class SpeechTranscriber:
    def __init__(self, *, whisper_model_size: str = "small", vosk_model_path: str | None = None) -> None:
        self.whisper_model_size = whisper_model_size
        self.vosk_model_path = vosk_model_path

    def transcribe_bytes(self, audio_bytes: bytes, filename: str) -> str:
        suffix = Path(filename).suffix or ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
            handle.write(audio_bytes)
            temp_path = Path(handle.name)

        try:
            return self.transcribe_file(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def transcribe_file(self, audio_path: str | Path) -> str:
        audio_path = Path(audio_path)
        if WhisperModel is not None:
            model = WhisperModel(self.whisper_model_size, device="cpu", compute_type="int8")
            segments, _ = model.transcribe(str(audio_path))
            transcript = " ".join(segment.text.strip() for segment in segments).strip()
            if transcript:
                return transcript

        if Model is not None and KaldiRecognizer is not None and self.vosk_model_path:
            raise NotImplementedError("Vosk fallback is reserved for local model setups and is not wired by default.")

        raise RuntimeError(
            "No speech transcription backend is available. Install the 'asr' optional dependencies to enable voice input."
        )
