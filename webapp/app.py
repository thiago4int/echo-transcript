from flask import Flask, request, jsonify
import psycopg2
import mistral

app = Flask(__name__)

@app.route('/audio-processing-endpoint', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily, or process in memory
    filename = "/path/to/save/" + file.filename
    file.save(filename)

    # Transcribe the audio using Mistral
    transcript = mistral.transcribe(filename)

    # Connect to PostgreSQL and insert the transcription
    conn = psycopg2.connect("dbname=mydatabase user=user password=password host=db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transcriptions (content) VALUES (%s)", (transcript,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
