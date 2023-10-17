import pyaudio
import wave
import audioop
import whisper
import os
import clipboard
rate = 512
def record_audio(filename):
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=int(1024/rate))

    frames = []
    silence_frames = 0
    print('Recording...\n')
    try:
        while True:
            data = stream.read(int(1024/rate))
            rms = audioop.rms(data, 2)
            if rms < 200:
                silence_frames += 1
                if silence_frames > 128*rate:
                    print('\nSilence detected, stopping recording.')
                    break
            else:
                silence_frames = 0
            print(" "*80, end="\r")
            print("#" * max(min(int((rms-50)/20), 80), 0) + "-" * max(80-max(int((rms-50)/20), 0), 0)
                  + " | " + str(rms) + " | " + str(silence_frames), end="")

            frames.append(data)
    except KeyboardInterrupt:
        print('\nRecording stopped by user.')
    except Exception as e:
        print(f'Error: {e}')

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(b''.join(frames))
    wf.close()

model = whisper.load_model("base")

audio_file = 'audio.wav'
record_audio(audio_file)

path = os.path.abspath(audio_file)
result = model.transcribe(path)

text_file = audio_file + ".txt"
with open(text_file, "w") as file:
    file.write(result["text"])
clipboard.copy(result["text"])
print(f'Transcription saved to {text_file} and to your clipboard')