import cv2
import logging
import os
import qrcode
import threading
from flask import Flask, Response, render_template, jsonify, request
from imgurpython import ImgurClient

from my_codeformer import fix_face
from my_insightface import detect_face, swap_face

app = Flask(__name__)

camera = cv2.VideoCapture(1)
frame = None
lock = threading.Lock()
id = 0
freeze = False          # freeze the video streaming during face detection
swap_gender = False     # gender mismatching between the faces in the two images

def generate_frames():
    """Show the video stream from the camera."""
    global frame
    while True:
        success, frame = camera.read()
        if success and not freeze:
            ret, buffer = cv2.imencode(".png", frame)
            with lock:
                output_frame = buffer.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/png\r\n\r\n" + output_frame + b"\r\n")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/personal_information")
def personal_information():
    global choice
    choice = request.args.get("selection")
    return render_template("personal_information.html")

@app.route("/selecting_photo")
def selecting_photo():
    """Select the photo for face swap."""
    image_directory = 'static/images'
    if choice == "solo":
        images = [f for f in os.listdir(image_directory) if f.startswith('solo_') and f.endswith(('.png'))]
        return render_template("solo_selecting_image.html", images=images)
    else:
        images = [f for f in os.listdir(image_directory) if f.startswith('group_') and f.endswith(('.png'))]
        return render_template("group_selecting_image.html", images=images)

@app.route("/taking_photo")
def taking_photo():
    """Capture the photo for face swap."""
    global dest
    dest = request.args.get("selection")

    return render_template("taking_photo.html")

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/capture")
def capture():
    """Freeze the video streaming from the camera and detect face after capturing photo."""
    global freeze

    if frame is None:
        logger.warning("No frame available")
        return jsonify(-1)
    
    cv2.imwrite(f"static/input/photo_{id:02d}.png", frame)
    logger.info(f"Photo taken successfully (id={id:02d})")

    freeze = True

    try:
        detect_face(dest, id)
        freeze = False
    except Exception as e:
        logger.error(f"InsightFace: {e}")
        freeze = False
        return jsonify(-2)
    return jsonify(id)

@app.route("/prepare_swapping")
def prepare_swapping():
    global swap_gender
    swap_gender_str = request.args.get("swapGender")
    swap_gender = swap_gender_str.lower() == 'true' if swap_gender_str else False
    logger.info(f"swap gender: {swap_gender}")
    return render_template("processing.html")
    
@app.route("/swapping_result")
def swapping_result():
    global id, swap_gender
    try:
        swap_face(dest, id, swap_gender)
    except Exception as e:
        logger.error(f"InsightFace: {e}")
        return render_template("swapping_failed.html")
    
    try:
        fix_face(id)
    except Exception as e:
        logger.error(f"CodeFormer: {e}")
        return render_template("swapping_failed.html")
     
    id += 1
    return render_template("swapping_result.html", id=id-1)

@app.route("/download_photo")
def download_photo():
    """Upload the result to an online album and generate a QR code for users to download."""
    client_id = "your-client-id"
    client_secret = "your-secret"
    access_token = "your-access-token"
    refresh_token = "your-refresh-token"
    album = "your-album",

    config = {
            "album": album,
            "name": f"result_{id-1:02d}",
            "title": f"result_{id-1:02d}",
        }

    try:
        client = ImgurClient(client_id, client_secret, access_token, refresh_token)
        logger.info(f"Uploading (id={id-1:02d})")
        image = client.upload_from_path(f"static/codeformer_output/result_{id-1:02d}.png", config=config, anon=False)
        logger.info(f"Uploaded successfully (id={id-1:02d})")
        qrcode.make(image["link"]).save(f"static/qrcode/qrcode_{id-1:02d}.png")
    except Exception as e:
        logger.error(f"Imgur: {e}")
        return render_template("qrcode_failed.html")

    return render_template("qrcode.html", id=id-1)

@app.route("/print_photo")
def print_photo():
    try:
        output_path = os.path.join(os.getcwd(), r"static\codeformer_output")
        img_name = f"result_{id-1:02d}.png"
        os.startfile(os.path.join(output_path, img_name), "print")
    except Exception as e:
        logger.error(f"Printer: {e}")
        return jsonify(-1)
    
    return jsonify(0)

if __name__ == "__main__":
    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("logging.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s"))
    logger.addHandler(file_handler)
    app.run(host="0.0.0.0", port=5000, debug=True)
