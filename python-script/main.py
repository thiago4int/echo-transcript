import sounddevice as sd
import numpy as np
import time
import wave
import requests
import logging
import argparse
import signal

# Argument parsing setup
parser = argparse.ArgumentParser(description='Record audio and send it to a server for processing.')
parser.add_argument('-u', '--base-url', type=str, required=True, help="The base URL to which the recordings are sent.")
parser.add_argument('-t', '--token', type=str, required=False, default='', help="API token for server authentication.")
parser.add_argument('-s', '--seconds', type=int, default=30, help="Duration of each recording segment in seconds.")
parser.add_argument('-l', '--save', action='store_true', help="Save recordings locally.")
parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output for debugging.")
args = parser.parse_args()

# Logging setup
logger = logging.getLogger('AudioRecorder')
logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Global flag to control recording state
is_recording = True

def signal_handler(sig, frame):
    global is_recording
    print('Stopping recording...')
    is_recording = False

signal.signal(signal.SIGINT, signal_handler)

def get_wav_filename():
    return 'recording{}.wav'.format(int(time.time()) if args.save else '')

def get_base_url():
    return args.base_url.rstrip('/')

def store_sound(data):
    filename = get_wav_filename()
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 2 bytes for FORMAT = np.int16
        wf.setframerate(16000)
        wf.writeframes(b''.join(data))

    if args.save:
        logger.info(f"Audio saved locally as {filename}")

    # Sending the file to the server
    with open(filename, 'rb') as f:
        files = {'audio_file': (filename, f, 'audio/wav')}
        try:
            response = requests.post(f'{get_base_url()}/asr?output=json', files=files, headers={'Authorization': f'Bearer {args.token}'}, timeout=540)
            logger.info(f"Server response: {response.text}")
            print(f"Server response JSON: {response.json()}")
        except requests.RequestException as e:
            logger.error(f"Failed to send audio to server: {e}")

def record_audio():
    global is_recording
    logger.info('Recording...')
    audio_frames = []

    with sd.InputStream(channels=1, samplerate=16000, dtype='int16') as stream:
        start_time = time.time()
        while is_recording and (time.time() - start_time) < args.seconds:
            data, _ = stream.read(1024)
            audio_frames.append(data)
            if not is_recording:
                break

    store_sound(audio_frames)

def main():
    print("Starting audio recording and processing script...")
    record_audio()

if __name__ == '__main__':
    main()
