from flask import Flask, jsonify, request
from capture import capture_active_window  # Assuming you have this function defined
import os
import logging

app = Flask(__name__)

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.route('/capture', methods=['POST'])
def capture_screen():
    try:
        data = request.json
        save_path = data.get('save_path', 'screenshot.jpg')

        if not os.path.isdir(os.path.dirname(save_path)):
            return jsonify({"status": "error", "message": "Invalid save path"})

        # Capture the active window and save
        capture_active_window(save_path)
        logger.info(f"Screen captured and saved to {save_path}")

        return jsonify({"status": "success", "message": "Screen captured", "file_path": save_path})

    except Exception as e:
        logger.error(f"Error capturing screen: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(port=5000)
