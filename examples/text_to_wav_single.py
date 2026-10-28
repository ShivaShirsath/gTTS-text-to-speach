from gtts import gTTS
from pydub import AudioSegment
import os

# Replace this text with the text you want to convert
text = "Football"

# Specify the custom path and filename for the output WAV file
output_wav_path = "~/Desktop/audio.wav"

# Ensure the directory exists
os.makedirs(os.path.dirname(output_wav_path), exist_ok=True)

# Temporary MP3 file path (can also be customized if needed)
temp_mp3_path = "temp_output.mp3"

# Generate speech and save as a temporary MP3 file
tts = gTTS(text=text, lang='en')
tts.save(temp_mp3_path)

# Convert MP3 to WAV and save to the custom path
sound = AudioSegment.from_mp3(temp_mp3_path)
silence = AudioSegment.silent(duration=400, frame_rate=sound.frame_rate)
sound = silence + sound
sound.export(output_wav_path, format="wav", parameters=["-filter:a", "atempo=0.9"])

# Optionally, remove the temporary MP3 file
os.remove(temp_mp3_path)

print(f"Conversion complete. The WAV file is saved as '{output_wav_path}'.")
