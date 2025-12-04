"""
Flask Web Application for Poaching Detection System - FIXED VERSION
File: app.py
"""

from flask import Flask, render_template, request, jsonify, send_file, Response, send_from_directory
import cv2
import os
from datetime import datetime
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from werkzeug.utils import secure_filename
import threading
import time
import queue

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'webm', 'mkv'}

# ======================== CONFIGURATION ========================
SENDER_EMAIL = "shlokbam19103@gmail.com"
SENDER_PASSWORD = "elph ygqe uqjs uond"
RECEIVER_EMAIL = "shlok.bam23@vit.edu"
AREA_NAME = "Forest Zone A"

EXCEL_FILE = "detection_log.xlsx"
DETECTED_IMAGES_FOLDER = "detected_images"
# ===============================================================

# Global variables
camera_active = False
detection_active = False
frame_queue = queue.Queue(maxsize=2)
detection_stats = {
    'total_detections': 0,
    'last_detection_time': None,
    'emails_sent': 0,
    'current_fps': 0
}

# Create necessary folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(DETECTED_IMAGES_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def format_detection_items(detected_objects: str) -> str:
    """Format detection items for HTML email."""
    lines = detected_objects.split('\n')
    html_items = ""

    for line in lines:
        if 'Person:' in line:
            status = line.split(':', 1)[1].strip()
            icon = '👤' if status == 'Yes' else '❌'
            html_items += f'''
            <div style="padding: 12px; background: rgba(239, 68, 68, 0.1); border-left: 4px solid #dc2626; margin-bottom: 10px; border-radius: 4px;">
                <div style="font-size: 24px; margin-bottom: 5px;">{icon}</div>
                <div>
                    <strong>Human Detected:</strong> 
                    <span style="color: #dc2626; font-weight: 600;">{status}</span>
                </div>
            </div>
            '''
        elif 'Animals:' in line:
            animals = line.split(':', 1)[1].strip()
            icon = '🦁' if animals != 'None detected' else '❌'
            color = '#16a34a' if animals != 'None detected' else '#64748b'
            html_items += f'''
            <div style="padding: 12px; background: rgba(34, 197, 94, 0.1); border-left: 4px solid {color}; margin-bottom: 10px; border-radius: 4px;">
                <div style="font-size: 24px; margin-bottom: 5px;">{icon}</div>
                <div>
                    <strong>Wildlife Detected:</strong> 
                    <span style="color: {color}; font-weight: 600;">{animals}</span>
                </div>
            </div>
            '''

    return html_items

def send_email_alert(image_path, timestamp, detected_objects):
    """Send email alert with detection details and image."""
    try:
        msg = MIMEMultipart('related')
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = f"⚠️ POACHING ALERT - {AREA_NAME}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background: #f3f4f6; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .alert-box {{ background: #fee2e2; border: 2px solid #dc2626; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .info-row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e5e7eb; }}
                .footer {{ background: #1f2937; color: white; padding: 20px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 28px;">⚠️ POACHING ALERT</h1>
                    <p style="margin: 10px 0 0 0;">Wildlife Protection System</p>
                </div>
                
                <div class="content">
                    <div class="alert-box">
                        <h2 style="margin: 0 0 10px 0; color: #dc2626;">🚨 Immediate Action Required</h2>
                        <p style="margin: 0; color: #475569;">Suspicious human activity detected in protected area.</p>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <div class="info-row">
                            <strong>📍 Location:</strong>
                            <span>{AREA_NAME}</span>
                        </div>
                        <div class="info-row">
                            <strong>🕐 Time:</strong>
                            <span>{timestamp}</span>
                        </div>
                    </div>
                    
                    <h3 style="color: #1e293b; margin: 25px 0 15px 0;">🎯 Detected Objects</h3>
                    {format_detection_items(detected_objects)}
                    
                    <h3 style="color: #1e293b; margin: 25px 0 15px 0;">📸 Captured Image</h3>
                    <img src="cid:detection_image" alt="Detection" style="width: 100%; border-radius: 8px; border: 2px solid #e5e7eb;">
                </div>
                
                <div class="footer">
                    <h3 style="margin: 0 0 10px 0;">🛡️ Automated Wildlife Protection System</h3>
                    <p style="margin: 5px 0; font-size: 14px; opacity: 0.8;">24/7 Monitoring • Real-time Alerts • Instant Response</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, 'html'))

        with open(image_path, 'rb') as f:
            img_data = f.read()
            img_inline = MIMEImage(img_data)
            img_inline.add_header('Content-ID', '<detection_image>')
            img_inline.add_header('Content-Disposition', 'inline', filename=os.path.basename(image_path))
            msg.attach(img_inline)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

        detection_stats['emails_sent'] += 1
        return True

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def log_to_excel(timestamp, person_detected, animals_detected, image_filename):
    """Log detection details to Excel file."""
    try:
        new_entry = {
            'Timestamp': timestamp,
            'Person Detected': 'Yes' if person_detected else 'No',
            'Animals Detected': ', '.join(animals_detected) if animals_detected else 'None',
            'Image Filename': image_filename
        }
        
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        else:
            df = pd.DataFrame([new_entry])
        
        df.to_excel(EXCEL_FILE, index=False)
        return True
        
    except Exception as e:
        print(f"Failed to log to Excel: {str(e)}")
        return False

def save_detection_image(img, timestamp):
    """Save detected image with timestamp."""
    try:
        filename = f"detection_{timestamp.replace(':', '-').replace(' ', '_')}.jpg"
        filepath = os.path.join(DETECTED_IMAGES_FOLDER, filename)
        cv2.imwrite(filepath, img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return filepath, filename
    except Exception as e:
        print(f"Failed to save image: {str(e)}")
        return None, None

def handle_detection_async(img, timestamp, person_detected, animals_detected):
    """Handle detection tasks asynchronously."""
    image_path, image_filename = save_detection_image(img, timestamp)
    
    if image_path:
        threading.Thread(target=log_to_excel, args=(timestamp, person_detected, animals_detected, image_filename), daemon=True).start()
        
        detected_objects = f"Person: Yes\nAnimals: {', '.join(animals_detected) if animals_detected else 'None detected'}"
        threading.Thread(target=send_email_alert, args=(image_path, timestamp, detected_objects), daemon=True).start()
        
        detection_stats['total_detections'] += 1
        detection_stats['last_detection_time'] = timestamp

def process_detection(video_source):
    """Process video/camera for detection."""
    global detection_active, detection_stats
    
    classFile = 'coco.names'
    if not os.path.exists(classFile):
        print(f"Error: {classFile} not found!")
        return
        
    with open(classFile, 'rt') as f:
        classNames = f.read().rstrip('\n').split('\n')
    
    configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
    weightPath = 'frozen_inference_graph.pb'
    
    if not os.path.exists(configPath) or not os.path.exists(weightPath):
        print("Error: Model files not found!")
        return
    
    net = cv2.dnn_DetectionModel(weightPath, configPath)
    net.setInputSize(320, 320)
    net.setInputScale(1.0 / 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)
    
    cam = cv2.VideoCapture(video_source)
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cam.set(cv2.CAP_PROP_FPS, 30)
    
    last_alert_time = None
    alert_cooldown = 10
    fps_counter = 0
    fps_start_time = time.time()
    
    while detection_active:
        success, img = cam.read()
        if not success:
            break
        
        height, width = img.shape[:2]
        if width > 1280:
            scale = 1280 / width
            img = cv2.resize(img, (1280, int(height * scale)))
        
        fps_counter += 1
        if time.time() - fps_start_time >= 1.0:
            detection_stats['current_fps'] = fps_counter
            fps_counter = 0
            fps_start_time = time.time()
        
        classIds, confs, bbox = net.detect(img, confThreshold=0.5)
        
        personDetected = False
        animalsDetected = []
        
        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                label = classNames[classId - 1]
                
                if label == 'person':
                    personDetected = True
                
                animal_list = ['bird', 'cat', 'dog', 'cow', 'horse', 'sheep', 
                               'elephant', 'bear', 'zebra', 'giraffe']
                if label in animal_list:
                    animalsDetected.append(label)
                
                color = (0, 255, 0) if label != 'person' else (0, 0, 255)
                cv2.rectangle(img, box, color=color, thickness=2)
                cv2.putText(img, f"{label} {confidence:.2f}", (box[0] + 10, box[1] + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        if personDetected:
            current_time = datetime.now()
            
            if last_alert_time is None or (current_time - last_alert_time).seconds >= alert_cooldown:
                timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
                img_copy = img.copy()
                threading.Thread(target=handle_detection_async, 
                               args=(img_copy, timestamp_str, personDetected, animalsDetected), 
                               daemon=True).start()
                last_alert_time = current_time
        
        cv2.putText(img, f"FPS: {detection_stats['current_fps']}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if not frame_queue.full():
            frame_queue.put(img)
    
    cam.release()
    while not frame_queue.empty():
        frame_queue.get()

def generate_frames():
    """Generate frames for video streaming."""
    while detection_active:
        try:
            frame = frame_queue.get(timeout=1)
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except queue.Empty:
            continue

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload_video', methods=['POST'])
def upload_video():
    global detection_active
    
    if 'video' not in request.files:
        return jsonify({'success': False, 'message': 'No video file provided'})
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        detection_active = True
        thread = threading.Thread(target=process_detection, args=(filepath,))
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Video uploaded and detection started'})
    
    return jsonify({'success': False, 'message': 'Invalid file format'})

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global detection_active, camera_active
    
    detection_active = True
    camera_active = True
    
    thread = threading.Thread(target=process_detection, args=(0,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'message': 'Camera started'})

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global detection_active, camera_active
    
    detection_active = False
    camera_active = False
    time.sleep(0.5)
    
    return jsonify({'success': True, 'message': 'Detection stopped'})

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_stats')
def get_stats():
    return jsonify(detection_stats)

@app.route('/download_excel')
def download_excel():
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True)
    return jsonify({'success': False, 'message': 'No detection log available'})

@app.route('/get_detected_images')
def get_detected_images():
    try:
        if not os.path.exists(DETECTED_IMAGES_FOLDER):
            return jsonify({'success': True, 'images': []})
        
        images = []
        for filename in sorted(os.listdir(DETECTED_IMAGES_FOLDER), reverse=True):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                timestamp = filename.replace('detection_', '').replace('.jpg', '').replace('_', ' ').replace('-', ':')
                images.append({
                    'filename': filename,
                    'timestamp': timestamp,
                    'url': f'/detected_images/{filename}'
                })
        
        return jsonify({'success': True, 'images': images})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/detected_images/<filename>')
def serve_detected_image(filename):
    return send_from_directory(DETECTED_IMAGES_FOLDER, filename)

@app.route('/delete_image/<filename>', methods=['POST'])
def delete_image(filename):
    try:
        filepath = os.path.join(DETECTED_IMAGES_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True, 'message': 'Image deleted'})
        return jsonify({'success': False, 'message': 'Image not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)