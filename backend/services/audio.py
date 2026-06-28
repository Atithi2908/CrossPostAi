import os
import subprocess
from core.logger import setup_logger
from core.config import settings

logger = setup_logger("audio_service")

class AudioService:
    def extract_audio(self, video_path: str) -> str:
        logger.info(f"Extracting audio from {video_path}")
        
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        audio_path = os.path.join(settings.CACHE_DIR, f"{base_name}.mp3")
        
        if os.path.exists(audio_path):
            audio_size = os.path.getsize(audio_path)
            logger.info(f"Using cached audio\nAudio Path: {audio_path}\nAudio Size: {audio_size} bytes")
            return audio_path
            
        try:
            ffmpeg_exe = "ffmpeg"
            
            # Log version before extraction
            version_result = subprocess.run([ffmpeg_exe, "-version"], capture_output=True, text=True)
            ffmpeg_version = version_result.stdout.split("\n")[0] if version_result.returncode == 0 else "Unknown"
            
            command = [
                ffmpeg_exe,
                "-i", video_path,
                "-q:a", "0",
                "-map", "a",
                "-y", # overwrite output
                audio_path
            ]
            
            logger.info(
                f"Starting extraction\n"
                f"FFmpeg Executable: {ffmpeg_exe}\n"
                f"FFmpeg Version: {ffmpeg_version}\n"
                f"Extraction Command: {' '.join(command)}"
            )
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr}")
                raise RuntimeError(f"FFmpeg failed to extract audio: {result.stderr}")
                
            audio_exists = os.path.exists(audio_path)
            audio_size = os.path.getsize(audio_path) if audio_exists else 0
            
            # Run ffprobe for diagnostics
            ffprobe_cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                audio_path
            ]
            
            probe_result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
            probe_info = ""
            if probe_result.returncode == 0:
                import json
                try:
                    probe_data = json.loads(probe_result.stdout)
                    audio_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"), {})
                    fmt = probe_data.get("format", {})
                    
                    codec = audio_stream.get("codec_name", "N/A")
                    sample_rate = audio_stream.get("sample_rate", "N/A")
                    bitrate = fmt.get("bit_rate", "N/A")
                    duration = fmt.get("duration", "N/A")
                    channels = audio_stream.get("channels", "N/A")
                    
                    probe_info = (
                        f"Codec: {codec}\n"
                        f"Sample Rate: {sample_rate} Hz\n"
                        f"Bitrate: {bitrate} bps\n"
                        f"Duration: {duration} s\n"
                        f"Channels: {channels}"
                    )
                except Exception as e:
                    probe_info = f"Failed to parse ffprobe output: {str(e)}"
            else:
                probe_info = f"ffprobe failed: {probe_result.stderr}"
            
            logger.info(
                f"Audio extracted successfully\n"
                f"Audio Path: {audio_path}\n"
                f"Audio Exists: {audio_exists}\n"
                f"Audio Size: {audio_size} bytes\n"
                f"FFmpeg Executable: {ffmpeg_exe}\n"
                f"--- ffprobe diagnostics ---\n"
                f"{probe_info}"
            )
            return audio_path
            
        except Exception as e:
            logger.error(f"Error during audio extraction: {str(e)}")
            raise
