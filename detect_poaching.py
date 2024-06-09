oimport cv2
import smtplib
import os
from datetime import datetime
import threading
import openpyxl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

def Camera():
    video_file_path = 'video.mp4'
    cam = cv2.VideoCapture(video_file_path)

    classNames = []
    classFile = 'coco.names'

    with open(classFile, 'rt') as f:
        classNames = f.read().rstrip('\n').split('\n')
    configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
    weightpath = 'frozen_inference_graph.pb'

    net = cv2.dnn_DetectionModel(weightpath, configPath)
    net.setInputSize(320, 230)
    net.setInputScale(1.0 / 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)

    fourcc = cv2.VideoWriter_fourcc(*'XVID') 
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    output_folder = 'detected_images'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create or load the Excel file
    excel_file = 'poaching_records.xlsx'
    if not os.path.exists(excel_file):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet['A1'] = 'Timestamp'
        sheet['B1'] = 'Animal Type'
    else:
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active

    def send_email(timestamp, animal_type, image_path):
        your_email = "your-email@gmail.com"
        your_password = "your-email-password"
        recipient_email = "recipient-email@gmail.com"
        subject = "Poaching Detected!"
        message = f"A person and a {animal_type} have been detected in the video at {timestamp}.\n\nRegards,\nThe Security System"

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(your_email, your_password)

            # Read the image data
            with open(image_path, 'rb') as f:
                img_data = f.read()

            # Create the email message with attachment
            email_message = MIMEMultipart()
            email_message['Subject'] = subject
            email_message.attach(MIMEText(message, 'plain'))
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(img_data)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename={os.path.basename(image_path)}')
            email_message.attach(attachment)

            # Send the email
            server.sendmail(your_email, recipient_email, email_message.as_string())

            print("Email notification sent successfully!")

            server.quit()

        except Exception as e:
            print("Failed to send email notification.")
            print(e)

    def handle_detection(img, animal_type):
        # Save the image of detected activity
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_name = f"detection_{timestamp.replace(':', '-')}.jpg"
        image_path = os.path.join(output_folder, image_name)
        cv2.imwrite(image_path, img)

        # Write to Excel file
        sheet.append([timestamp, animal_type])
        workbook.save(excel_file)

        # Send email notification with timestamp, animal type, and image
        send_email(timestamp, animal_type, image_path)

    while True:
        success, img = cam.read()
        classIds, confs, bbox = net.detect(img, confThreshold=0.5)

        if len(classIds) != 0:
            personDetected = False
            animalDetected = False
            animal_type = ""

            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                if classNames[classId - 1] == 'person':
                    personDetected = True
                if classNames[classId - 1] in ['bird', 'cat', 'dog', 'cow', 'horse', 'sheep', 'pig', 'gorilla', 'monkey', 'elephant', 'giraffe']:
                    animalDetected = True
                    animal_type = classNames[classId - 1]

                cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                cv2.putText(img, classNames[classId - 1], (box[0] + 10, box[1] + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), thickness=2)

            if personDetected:
                print("Person detected!")
                if animalDetected:
                    print("Poaching detected!!")

                # Start a new thread to handle detection
                threading.Thread(target=handle_detection, args=(img.copy(), animal_type if animalDetected else "None")).start()

        out.write(img)

        cv2.imshow('Output', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    out.release()
    cv2.destroyAllWindows()

Camera()
