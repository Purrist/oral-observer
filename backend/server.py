from flask import Flask, Response, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# Allow cross-origin requests from any origin (for development/debugging)
# WARNING: Change this to specific origins in production!
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Configuration ---
# Note: This path is relative to the server.py file.
# If you want to specify an absolute path like D:\desktop\PYProject\photos, modify UPLOAD_FOLDER
UPLOAD_FOLDER = 'photos'
if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
        logging.info(f"Created photos directory at: {os.path.abspath(UPLOAD_FOLDER)}")
    except OSError as e:
        logging.error(f"Error creating directory {UPLOAD_FOLDER}: {e}")
        # If directory creation fails, saving will fail later. Consider exiting or using an alternative path.

camera_index = 0 # Default camera index (usually 0)
camera = None

def initialize_camera():
    global camera
    # Release previous camera object if it exists
    if camera is not None:
        camera.release()
    logging.info(f"Attempting to open camera with index {camera_index}")
    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        logging.error(f"Error: Could not open camera with index {camera_index}.")
        # You might try other camera indices or return an error status here
        return False
    logging.info(f"Camera {camera_index} opened successfully.")
    # You can set camera resolution or other parameters here if needed
    # camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    return True

# Route for video streaming
@app.route('/video_feed')
def video_feed():
    # Initialize camera if it's not already connected
    if camera is None or not camera.isOpened():
        if not initialize_camera():
             return Response("Error: Camera not available.", status=500) # Service Unavailable

    def generate():
        # Keep generating frames while the camera is connected
        while True:
            success, frame = camera.read()
            if not success:
                logging.warning("Could not read frame from camera.")
                # You might try re-initializing the camera or wait
                time.sleep(0.1)
                # If it continuously fails, you might break the loop or send an error signal
                continue # Skip current frame processing
            else:
                # You can add image processing logic here using OpenCV
                # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Example: Convert to grayscale

                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80]) # Compress with 80% quality
                if not ret:
                    logging.warning("Could not encode frame.")
                    continue
                frame_bytes = buffer.tobytes()
                # Yield frame in multipart/x-mixed-replace format for streaming
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\r\n') # Fixed an extra carriage return here

            # Add a small delay to prevent high CPU usage, adjust as needed
            time.sleep(0.03) # Approximately 30 FPS

        logging.warning("Video stream generator stopped.") # Log when the generator finishes

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route for capturing a photo
@app.route('/capture_photo', methods=['POST'])
def capture_photo():
    # Check if camera is available
    if camera is None or not camera.isOpened():
        logging.error("Capture failed: Camera not available.")
        return jsonify({'error': 'Camera not available'}), 503

    # Get tooth position from request JSON data
    data = request.json
    tooth_position = data.get('tooth')
    if not tooth_position:
        logging.warning("Capture failed: 'tooth' position missing in request.")
        return jsonify({'error': 'Tooth position missing'}), 400

    # Read the current frame from the camera
    success, frame = camera.read()
    if success:
        # Construct the folder path for saving the photo (e.g., photos/1, photos/2 etc.)
        folder_path = os.path.join(UPLOAD_FOLDER, str(tooth_position))
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                logging.info(f"Created directory for tooth {tooth_position}: {folder_path}")
            except OSError as e:
                 logging.error(f"Error creating directory {folder_path}: {e}")
                 return jsonify({'error': f"Could not create directory for tooth {tooth_position}"}), 500

        # Generate a unique filename (using millisecond timestamp)
        filename = f"{int(time.time() * 1000)}.jpg"
        filepath = os.path.join(folder_path, filename)

        try:
            # Save the image frame to the file
            # cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 90]) # Optional: set quality
            cv2.imwrite(filepath, frame)
            logging.info(f"Photo saved successfully to: {filepath}")
            # Return success message and photo details
            return jsonify({'message': 'Photo saved', 'filename': filename, 'tooth': tooth_position, 'path': filepath})
        except Exception as e:
            logging.error(f"Error saving photo to {filepath}: {e}")
            return jsonify({'error': f"Failed to save photo: {e}"}), 500
    else:
        logging.error("Capture failed: Could not read frame from camera.")
        return jsonify({'error': 'Failed to capture image from camera'}), 500

# Route for listing all photos
@app.route('/list_photos', methods=['GET'])
def list_photos():
    # Check if the photos root directory exists and is a directory
    if not os.path.exists(UPLOAD_FOLDER) or not os.path.isdir(UPLOAD_FOLDER):
        logging.warning(f"Photos directory '{UPLOAD_FOLDER}' not found.")
        return jsonify({}) # Return empty object if no photos directory

    result = {}
    try:
        # Iterate through each subdirectory in the UPLOAD_FOLDER (representing tooth positions)
        for tooth_folder in os.listdir(UPLOAD_FOLDER):
            tooth_folder_path = os.path.join(UPLOAD_FOLDER, tooth_folder)
            # Ensure it's a directory and the name is a digit (valid tooth position)
            if os.path.isdir(tooth_folder_path) and tooth_folder.isdigit():
                photos_in_folder = []
                # Iterate through all files in the tooth folder
                for filename in os.listdir(tooth_folder_path):
                    # Simple check if it's an image file (add more robust checks if needed)
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        photos_in_folder.append(filename)
                # If there are photos in this tooth folder, add them to the result
                if photos_in_folder:
                    result[tooth_folder] = sorted(photos_in_folder) # Sort filenames
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error listing photos from {UPLOAD_FOLDER}: {e}")
        return jsonify({'error': f'Failed to list photos: {e}'}), 500

# Route for deleting selected photos
@app.route('/delete_photos', methods=['POST'])
def delete_photos():
    data = request.json
    photos_to_delete = data.get('photos', []) # Expected format: [{'tooth': '1', 'filename': '123.jpg'}, ...]

    if not photos_to_delete:
        return jsonify({'message': 'No photos specified for deletion'}), 400

    deleted_count = 0
    errors = []
    for photo_info in photos_to_delete:
        tooth = str(photo_info.get('tooth')) # Ensure tooth is a string
        filename = photo_info.get('filename')

        if not tooth or not filename:
            errors.append(f"Missing 'tooth' or 'filename' in item: {photo_info}")
            continue

        file_path = os.path.join(UPLOAD_FOLDER, tooth, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logging.info(f"Deleted photo: {file_path}")
                deleted_count += 1
            except OSError as e:
                logging.error(f"Error deleting photo {file_path}: {e}")
                errors.append(f"Could not delete {filename} for tooth {tooth}: {e}")
        else:
            logging.warning(f"Photo not found for deletion: {file_path}")
            errors.append(f"Photo not found: {filename} for tooth {tooth}")

    response = {
        'message': f'Deletion process completed. Deleted {deleted_count} photos.',
        'errors': errors if errors else None
    }
    # Return 200 even if there were some errors, listing them in the response body
    status_code = 200
    return jsonify(response), status_code


# Route for serving photo files
@app.route('/photos/<path:filepath>')
def get_photo(filepath):
    # filepath is expected in the format 'tooth/filename.jpg'
    # Example: /photos/1/1714392022.jpg
    directory = os.path.abspath(UPLOAD_FOLDER)
    # logging.debug(f"Serving photo from directory: {directory}, requested path: {filepath}") # Avoid spamming logs in development
    try:
        # send_from_directory handles path security checks
        return send_from_directory(directory, filepath, as_attachment=False)
    except FileNotFoundError:
         logging.warning(f"Photo not found at path: {filepath}")
         return jsonify({'error': 'Photo not found'}), 404
    except Exception as e:
        logging.error(f"Error serving photo {filepath}: {e}")
        return jsonify({'error': 'Server error serving photo'}), 500

# --- App Run ---
if __name__ == '__main__':
    # Attempt to initialize the camera on script run
    if not initialize_camera():
        # If initial camera initialization fails, log a warning.
        # The /video_feed route will attempt to re-initialize on the first request if needed.
        logging.warning("Initial camera initialization failed. The /video_feed route will attempt to retry on the first request.")

    # Run the Flask application
    # host='0.0.0.0' makes the server accessible from other devices on the local network
    # port=5000 sets the backend port
    # debug=True enables debugging features, such as automatic code reloading (use_reloader=False disables this to prevent camera issues)
    # use_reloader=False is important when dealing with resources like cameras or serial ports to prevent them from being opened multiple times.
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

    # Ensure the camera resource is released when the application exits
    if camera and camera.isOpened():
        camera.release()
        logging.info("Camera released on application exit.")