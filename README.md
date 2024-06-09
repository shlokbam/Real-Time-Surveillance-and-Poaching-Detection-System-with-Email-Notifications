
# Real-Time Surveillance and Poaching Detection System with Email Notifications

## Introduction

This project aims to create an intelligent real-time surveillance system that detects poaching activities. The system identifies the presence of both humans and specific animals in video footage, triggers automated email notifications when potential poaching is detected, and records these incidents in an Excel file. The primary goal is to aid in wildlife protection by providing timely alerts and evidence of poaching activities.

## Features

- **Real-Time Detection**: Utilizes AI to detect humans and specific animals in video footage.
- **Automated Email Alerts**: Sends email notifications with attached images when potential poaching is detected.
- **Excel Records**: Logs detection events with timestamps and animal types in an Excel file.
- **Video Processing**: Supports both live camera feeds and video file inputs for flexible deployment.
- **Image Saving**: Saves images of detected events for further review and evidence.

## Proof of Concept

The system has been tested with various video inputs to ensure accurate detection and timely notifications. A sample Images is included for demonstration purposes. The system successfully detects humans and specified animals, sends email alerts, and logs the events in an Excel file.
![Sample Image 1](images/photo1.png)
![Sample Image 2](images/photo2.png)
![Sample Image 3](images/photo5.png)

## Setup and Installation

### Prerequisites

- Python 3.6 or higher
- OpenCV
- OpenPyXL
- smtplib
- Email credentials (for sending notifications)

### Installation Steps

1. **Clone the Repository**
   ```sh
   git clone https://github.com/yourusername/poaching-detection-system.git
   cd poaching-detection-system
   ```

2. **Install Dependencies**
   ```sh
   pip install opencv-python openpyxl
   ```

3. **Download Pre-trained Model and Configuration Files**
   - `ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt`
   - `frozen_inference_graph.pb`
   - `coco.names`

4. **Setup Email Credentials**
   Update the `send_email` function in the `Camera` function with your email credentials:
   ```python
   your_email = "your-email@gmail.com"
   your_password = "your-email-password"
   recipient_email = "recipient-email@gmail.com"
   ```

### Running the System

1. **Run the Script**
   ```sh
   python detect_poaching.py
   ```

2. **Interactive Session**
   - The system will start processing the video input (either from a file or live feed).
   - Detected events will be displayed with bounding boxes and labels.
   - Email notifications will be sent automatically for detected poaching events.

## Project Structure

poaching-detection-system/

│

├── coco.names       # COCO class names

├── frozen\_inference\_graph.pb       # Pre-trained model

├── ssd\_mobilenet\_v3\_large\_coco\_2020\_01\_14.pbtxt       # Model config file

├── detect\_poaching.py       # Main script

├── detected\_images/        # Folder to save detected images
 
├── poaching\_records.xlsx       # Excel file to log detection events

├── README.md      # Project documentation

## Usage

- **Real-Time Monitoring**: Set `cam = cv2.VideoCapture(0)` in the script to use a webcam for live monitoring.
- **Video File Processing**: Set `video_file_path` to the path of your video file to process pre-recorded videos.
- **Excel Logging**: Check `poaching_records.xlsx` for a log of detection events.
- **Email Notifications**: Ensure email credentials are correctly set for receiving notifications.

## Contributing

Contributions are welcome! If you have any suggestions or improvements, feel free to create a pull request or open an issue.

## License

This project is licensed under the MIT License.
