from flask import Flask, Response, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import os
import time
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# 允许来自 Nuxt 开发服务器 (通常是 http://localhost:3000) 的跨域请求
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# --- 配置 ---
# 注意：这里的路径是相对于 server.py 文件的。
# 如果您想指定 D:\desktop\PYProject\photos 这样的绝对路径，请修改 UPLOAD_FOLDER
# 例如: UPLOAD_FOLDER = r'D:\desktop\PYProject\photos'
UPLOAD_FOLDER = 'photos'
if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
        logging.info(f"Created photos directory at: {os.path.abspath(UPLOAD_FOLDER)}")
    except OSError as e:
        logging.error(f"Error creating directory {UPLOAD_FOLDER}: {e}")
        # 如果无法创建目录，后续保存会失败，这里可以考虑退出或使用备用路径

camera_index = 0 # 默认使用第一个摄像头 (索引为 0)
camera = None

def initialize_camera():
    global camera
    if camera is not None:
        camera.release() # 释放之前的摄像头对象
    logging.info(f"Attempting to open camera with index {camera_index}")
    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        logging.error(f"Error: Could not open camera with index {camera_index}.")
        # 这里可以尝试其他摄像头索引，或者返回错误状态
        return False
    logging.info(f"Camera {camera_index} opened successfully.")
    # 可以设置摄像头分辨率等参数 (如果需要)
    # camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    return True

@app.route('/video_feed')
def video_feed():
    if camera is None or not camera.isOpened():
        if not initialize_camera():
             return Response("Error: Camera not available.", status=500)

    def generate():
        while True:
            success, frame = camera.read()
            if not success:
                logging.warning("Could not read frame from camera.")
                # 可以尝试重新初始化摄像头或等待
                time.sleep(0.1)
                # 如果持续失败，可能需要跳出循环或发送错误信号
                # break # 暂时不跳出，让它继续尝试
                continue # 跳过当前帧处理
            else:
                # 可以在这里添加图像处理逻辑 (来自 OpenCV)
                # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # 例如：转灰度

                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80]) # 压缩质量为80
                if not ret:
                    logging.warning("Could not encode frame.")
                    continue
                frame_bytes = buffer.tobytes()
                # 使用 multipart/x-mixed-replace 格式发送视频流
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            # 加一点小的延时，避免CPU占用过高，根据实际情况调整
            time.sleep(0.03) # 大约 30 FPS

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture_photo', methods=['POST'])
def capture_photo():
    if camera is None or not camera.isOpened():
        logging.error("Capture failed: Camera not available.")
        return jsonify({'error': 'Camera not available'}), 503 # Service Unavailable

    data = request.json
    tooth_position = data.get('tooth')  # 获取牙位编号 (例如 1, 2, ..., 32)
    if not tooth_position:
        logging.warning("Capture failed: 'tooth' position missing in request.")
        return jsonify({'error': 'Tooth position missing'}), 400

    # 从摄像头读取当前帧
    success, frame = camera.read()
    if success:
        # 构建保存图片的文件夹路径 (例如 photos/1, photos/2 等)
        folder_path = os.path.join(UPLOAD_FOLDER, str(tooth_position))
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path)
                logging.info(f"Created directory for tooth {tooth_position}: {folder_path}")
            except OSError as e:
                 logging.error(f"Error creating directory {folder_path}: {e}")
                 return jsonify({'error': f"Could not create directory for tooth {tooth_position}"}), 500

        # 生成文件名 (使用时间戳确保唯一性)
        filename = f"{int(time.time() * 1000)}.jpg" # 毫秒级时间戳
        filepath = os.path.join(folder_path, filename)

        try:
            # 保存图片
            # 可以设置保存质量 cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            cv2.imwrite(filepath, frame)
            logging.info(f"Photo saved successfully to: {filepath}")
            # 返回成功信息和文件名
            return jsonify({'message': 'Photo saved', 'filename': filename, 'tooth': tooth_position, 'path': filepath})
        except Exception as e:
            logging.error(f"Error saving photo to {filepath}: {e}")
            return jsonify({'error': f"Failed to save photo: {e}"}), 500
    else:
        logging.error("Capture failed: Could not read frame from camera.")
        return jsonify({'error': 'Failed to capture image from camera'}), 500

@app.route('/list_photos', methods=['GET'])
def list_photos():
    # 检查照片根目录是否存在
    if not os.path.exists(UPLOAD_FOLDER) or not os.path.isdir(UPLOAD_FOLDER):
        logging.warning(f"Photos directory '{UPLOAD_FOLDER}' not found.")
        return jsonify({}) # 返回空对象，表示没有照片

    result = {}
    try:
        # 遍历 photos 目录下的每个子文件夹 (代表牙位)
        for tooth_folder in os.listdir(UPLOAD_FOLDER):
            tooth_folder_path = os.path.join(UPLOAD_FOLDER, tooth_folder)
            # 确保是文件夹并且文件夹名是数字 (代表牙位)
            if os.path.isdir(tooth_folder_path) and tooth_folder.isdigit():
                photos_in_folder = []
                # 遍历牙位文件夹下的所有文件
                for filename in os.listdir(tooth_folder_path):
                    # 简单检查是否是图片文件 (可以根据需要添加更严格的检查)
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        photos_in_folder.append(filename)
                # 如果该牙位下有照片，则添加到结果中
                if photos_in_folder:
                    result[tooth_folder] = sorted(photos_in_folder) # 按文件名排序
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error listing photos from {UPLOAD_FOLDER}: {e}")
        return jsonify({'error': f'Failed to list photos: {e}'}), 500

@app.route('/delete_photos', methods=['POST'])
def delete_photos():
    data = request.json
    photos_to_delete = data.get('photos', []) # 期望格式: [{'tooth': '1', 'filename': '123.jpg'}, ...]

    if not photos_to_delete:
        return jsonify({'message': 'No photos specified for deletion'}), 400

    deleted_count = 0
    errors = []
    for photo_info in photos_to_delete:
        tooth = str(photo_info.get('tooth')) # 确保 tooth 是字符串
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
    status_code = 200 if not errors else 404 # 如果有错误，返回 404 Not Found 可能不太合适，207 Multi-Status 或 200 加上错误列表更好
    return jsonify(response), status_code


# 提供访问照片文件的路由
@app.route('/photos/<path:filepath>')
def get_photo(filepath):
    # filepath 期望是 'tooth/filename.jpg' 的形式
    # 例如 /photos/1/1714392022.jpg
    directory = os.path.abspath(UPLOAD_FOLDER)
    logging.debug(f"Serving photo from directory: {directory}, requested path: {filepath}")
    try:
        # send_from_directory 会处理路径安全问题
        return send_from_directory(directory, filepath, as_attachment=False)
    except FileNotFoundError:
         logging.warning(f"Photo not found at path: {filepath}")
         return jsonify({'error': 'Photo not found'}), 404
    except Exception as e:
        logging.error(f"Error serving photo {filepath}: {e}")
        return jsonify({'error': 'Server error serving photo'}), 500

if __name__ == '__main__':
    # 首次运行时初始化摄像头
    if not initialize_camera():
        logging.warning("Initial camera initialization failed. Will retry on first request.")
    # 运行 Flask 应用
    # host='0.0.0.0' 让局域网内其他设备可以通过你的 IP 地址访问
    # debug=True 开启调试模式，代码修改后服务器会自动重启，并提供更详细的错误信息
    # use_reloader=False 在 debug 模式下防止 Flask 启动两个进程导致摄像头初始化问题
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

    # 程序退出时确保释放摄像头资源
    if camera and camera.isOpened():
        camera.release()
        logging.info("Camera released.")