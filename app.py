
import os
import numpy as np
import base64
from flask import (
    Flask,

    jsonify,
    render_template,
    request,
    send_from_directory,
)
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from pydantic import Json, ValidationError
from pymongo.errors import PyMongoError
import torch
import cv2
from controllers.cars import CarController
from databases.models.CarsModel import Cars
import function.utils_rotate as utils_rotate
import function.helper as helper
from routes import navs
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

app = Flask(__name__)
CORS(app, origins="*")  # Enable CORS for all routes
socketio = SocketIO(app)

# Load models
yolo_LP_detect = torch.hub.load(
    "yolov5",
    "custom",
    path="model/LP_detector_nano_61.pt",
    force_reload=True,
    source="local",
)
yolo_license_plate = torch.hub.load(
    "yolov5",
    "custom",
    path="model/LP_ocr_nano_62.pt",
    force_reload=True,
    source="local",
)
yolo_license_plate.conf = 0.60

# vid = cv2.VideoCapture(0)  # Capture video from the webcam
# def generate_frames():
#     prev_frame_time = 0

#     recording = True  # Flag to control recording
#     while True:
#         ret, frame = vid.read()
#         if not ret:
#             break

#         plates = yolo_LP_detect(frame, size=640)
#         list_plates = plates.pandas().xyxy[0].values.tolist()
#         list_read_plates = set()

#         for plate in list_plates:
#             flag = 0
#             x = int(plate[0])  # xmin
#             y = int(plate[1])  # ymin
#             w = int(plate[2] - plate[0])  # xmax - xmin
#             h = int(plate[3] - plate[1])  # ymax - ymin
#             cv2.rectangle(
#                 frame,
#                 (int(plate[0]), int(plate[1])),
#                 (int(plate[2]), int(plate[3])),
#                 color=(0, 255, 0),
#                 thickness=2,
#             )
#             crop_img = frame[y : y + h, x : x + w]
#             lp = ""
#             for cc in range(2):
#                 for ct in range(2):
#                     lp = helper.read_plate(
#                         yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct)
#                     )
#                     if lp != "unknown":
#                         list_read_plates.add(lp)
#                         cv2.putText(
#                             frame,
#                             lp,
#                             (int(plate[0]), int(plate[1] - 10)),
#                             cv2.FONT_HERSHEY_SIMPLEX,
#                             0.9,
#                             (36, 255, 12),
#                             2,
#                         )
#                         flag = 1
#                         break
#                 if flag == 1:
#                     break
#             if flag == 1:
#                 # Stop recording if a license plate is detected
#                 cv2.imwrite("captured_frame.jpg", frame)

#                 # Encode the captured frame to base64
#                 with open("captured_frame.jpg", "rb") as f:
#                     captured_frame_base64 = base64.b64encode(f.read()).decode("utf-8")

#                 # Get paths for cropped and original images
#                 cropped_image_path = f"static/cars/cropped_image_{lp}.jpg"
#                 original_image_path = f"static/cars/original_image_{lp}.jpg"

#                 print(cropped_image_path,original_image_path)
#                 break

#         # Calculate and display FPS
#         new_frame_time = time.time()
#         fps = 1 / (new_frame_time - prev_frame_time)
#         prev_frame_time = new_frame_time
#         fps = int(fps)
#         cv2.putText(
#             frame,
#             str(fps),
#             (7, 70),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             3,
#             (100, 255, 0),
#             3,
#             cv2.LINE_AA,
#         )

#         ret, buffer = cv2.imencode(".jpg", frame)
#         frame = buffer.tobytes()
#         yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/node_modules/<path:filename>")
def node_modules(filename):
    return send_from_directory("node_modules", filename)


@app.route("/")
def index():
    return render_template("home.html", navs=navs)


@app.route("/add-car", methods=["POST"])
def insert_car():
    cars_controller = CarController()
    car_data = request.json

    car = Cars(**car_data)
    response = cars_controller.create_car(car)
    if "error" in response:
        return jsonify({"status": 400, "error": response["error"]}), 400
    else:
        return (
            jsonify(
                {
                    "status": 200,
                    "message": "Car added successfully",
                    "car_id": response["car_id"],
                }
            ),
            201,
        )


@app.route("/update-car", methods=["PUT"])
def update_car():
    cars_controller = CarController()
    car_id = request.args.get("_id")
    car_data = request.json
    try:
        # Validate and create a Cars object
        car = Cars(**car_data)
    except ValidationError as e:
        return jsonify({"status": 400, "error": e.errors()}), 400

    # Update the car in the database
    updated_car = cars_controller.update_car(car_id, car.dict(exclude_unset=True))

    if updated_car:
        return (
            jsonify(
                {
                    "status": 200,
                    "message": "Car updated successfully",
                    "car": updated_car,
                }
            ),
            200,
        )
    else:
        return jsonify({"status": 400, "error": "Car not found or update failed"}), 400


@app.route("/get-car", methods=["GET"])
def get_car():
    # Lấy giá trị của tham số "license_plate" từ request query
    car_id = request.args.get("license_plate")

    # Kiểm tra xem car_id có tồn tại không
    if not car_id:
        return jsonify({"status": 400, "message": "Car ID is required"}), 400

    cars_controller = CarController()

    car = cars_controller.get_carByLicensePlate(car_id)
    if car is None:
        return jsonify({"status": 404, "message": "Car not found"}), 404
    else:
        return jsonify({"status": 200, "car": car}), 200


@app.route("/check-violations", methods=["GET"])
async def check_violations_route():
    license_plate = request.args.get("license_plate")
    if not license_plate:
        return jsonify({"error": "license_plate is required"}), 400
    result = await helper.fetch_violation_data(license_plate)
    print(result)
    return result


@app.route("/test")
def testfunction():
    return render_template("test.html")


# @app.route("/image_feed")
# def image_feed():
#     return Response(
#         generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
#     )


@app.route("/list-car")
def list_cars_page():
    return render_template("list_cars.html", navs=navs)


@app.route("/get-cars", methods=["GET"])
def list_cars():
    try:
        controller = CarController()

        # Get query parameters for pagination
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=10, type=int)

        cars, total_cars = controller.get_all_cars_paginated(page, per_page)

        # Prepare pagination metadata
        pagination_metadata = {
            "page": page,
            "per_page": per_page,
            "total_cars": total_cars,
            "total_pages": (total_cars // per_page)
            + (1 if total_cars % per_page > 0 else 0),
        }

        return jsonify(
            {
                "status": 200,
                "message": "Fetch All Car successfully",
                "cars": cars,
                "pagination": pagination_metadata,
            }
        )
    except PyMongoError as pymongo_err:
        return (
            jsonify(
                {
                    "status": 500,
                    "message": f"Database error: {str(pymongo_err)}",
                }
            ),
            500,
        )


@app.route("/add-checkin-checkout-log", methods=["POST"])
def add_checkin_checkout_log():
    try:
        license_plate = request.args.get("license_plate")
        checkin_checkout_data = request.json
        controller = CarController()
        result = controller.add_checkin_checkout_log(
            license_plate, checkin_checkout_data
        )

        if result:
            return jsonify(result), result["status"]
        else:
            return jsonify({"status": 404, "message": "Car not found"}), 404
    except ValidationError as e:
        return jsonify({"status": 400, "message": e.errors()}), 400
    except Exception as ex:
        return jsonify({"status": 500, "message": str(ex)}), 500


# Process image data received through WebSocket
@socketio.on("image_data")
def handle_image(data):
    image_data = data["image_data"].split(",")[1]
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Perform object detection using YOLO for license plate detection
    plates = yolo_LP_detect(img, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()

    list_read_plates = list()
    flag = False

    for plate in list_plates:
        x, y, w, h = (
            int(plate[0]),
            int(plate[1]),
            int(plate[2] - plate[0]),
            int(plate[3] - plate[1]),
        )
        crop_img = img[y : y + h, x : x + w]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        for cc in range(2):
            for ct in range(2):
                lp = helper.read_plate(
                    yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct)
                )
                if lp != "unknown":
                    print("before formatting" + "|-> " + lp)
                    lp = helper.format_license_plate(lp)
                    list_read_plates.append(lp)
                    print(lp)
                    flag = True
                    break
            if flag:
                break

    if flag:
        license_plate = list(
            list_read_plates
        )  # Assuming you want to use the first detected plate
        _, encoded_frame = cv2.imencode(".jpg", img)
        # frame_base64 = base64.b64encode(encoded_frame).decode("utf-8")
        dir_path = os.path.join("static/cars/images/crops", str(license_plate[0]))
        os.makedirs(dir_path, exist_ok=True)

        cropped_image_path = os.path.join(dir_path, "cropped_image.jpg")
        cv2.imwrite(cropped_image_path, crop_img)

        original_image_path = os.path.join(dir_path, "original_image.jpg")
        cv2.imwrite(original_image_path, img)

        # with open(cropped_image_path, "rb") as f:
        #    cropped_img_base64 = base64.b64encode(f.read()).decode('utf-8')

        # with open(original_image_path, "rb") as f:
        #    original_img_base64 = base64.b64encode(f.read()).decode('utf-8')
        province_text = helper.get_province(str(license_plate[0]))
        emit(
            "license_plate",
            {
                "status": 200,
                "message": "Successfully",
                "license_plate": list_read_plates,
                "cropped_image": cropped_image_path.replace("\\", "/"),
                "original_image": original_image_path.replace("\\", "/"),
                "province_text": province_text,
            },
        )
    else:
        emit("license_plate", {"status": 400, "message": "No license plate"})


@socketio.on("checkout")
def handle_checkout(data):
    image_data = data["image_data"].split(",")[1]
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Perform object detection using YOLO for license plate detection
    plates = yolo_LP_detect(img, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()

    list_read_plates = list()
    flag = False

    for plate in list_plates:
        x, y, w, h = (
            int(plate[0]),
            int(plate[1]),
            int(plate[2] - plate[0]),
            int(plate[3] - plate[1]),
        )
        crop_img = img[y : y + h, x : x + w]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        for cc in range(2):
            for ct in range(2):
                lp = helper.read_plate(
                    yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct)
                )
                if lp != "unknown":
                    print("before formatting" + "|-> " + lp)
                    lp = helper.format_license_plate(lp)
                    list_read_plates.append(lp)
                    print(lp)
                    flag = True
                    break
            if flag:
                break

    if flag:
        license_plate = list(
            list_read_plates
        )  # Assuming you want to use the first detected plate
        _, encoded_frame = cv2.imencode(".jpg", img)

        # with open(cropped_image_path, "rb") as f:
        #    cropped_img_base64 = base64.b64encode(f.read()).decode('utf-8')

        # with open(original_image_path, "rb") as f:
        #    original_img_base64 = base64.b64encode(f.read()).decode('utf-8')
        province_text = helper.get_province(str(license_plate[0]))
        emit(
            "result_checkout",
            {
                "status": 200,
                "message": "Successfully",
                "license_plate": str(license_plate[0]),
            },
        )
    else:
        emit("result_checkout", {"status": 400, "message": "No license plate"})


# @socketio.on('stop_recording')
# def stop_recording():
#     # Implement logic to stop webcam capture
#     # For example, release the video capture resource
#     vid.release() # Uncomment and replace vid with your video capture object

# @socketio.on('start_recording')
# def start_recording():
#     # Implement logic to stop webcam capture
#     # For example, release the video capture resource
#     vid.read() # Uncomment and replace vid with your video capture object

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
