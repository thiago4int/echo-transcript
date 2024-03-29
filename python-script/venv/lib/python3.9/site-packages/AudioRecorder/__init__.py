import pyaudio
import wave
import threading


class AudioRecorder:
    try:
        def __init__(self, file_name='Audorecoder'):
            self.file_name = file_name

            # Create an event to signal the loop to stop
            self.stop_event = threading.Event()

        def start_recording(self):
            # Open the audio file using PyAudio
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True)
            self.frames = []
            # Start a new thread to record audio
            self.recording_thread = threading.Thread(target=self.record_audio)
            self.recording_thread.start()


        def record_audio(self):
            while not self.stop_event.is_set():
                self.frames.append(self.stream.read(1024))

        def stop_recording(self):
            # Set the event to stop the loop
            self.stop_event.set()
            # Wait for the recording thread to finish
            self.recording_thread.join()
            # Stop the stream and close the file
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            # Save the recorded audio to a file
            wf = wave.open(f"{self.file_name}.wav", "wb")
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))
            wf.close()
    except Exception:
        print("Sum Error")

