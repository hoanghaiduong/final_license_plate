import asyncio
import json
from bson.objectid import ObjectId
from bson import json_util
from typing import List
from datetime import datetime
import sys
import os

from pymongo import ReturnDocument
from function import helper as helpers

# Thêm đường dẫn của thư mục chứa file database.py vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from databases.models.CarsModel import Cars, CheckinCheckoutLog
from database import connect_to_database


def serialize_doc(doc):
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


class CarController:
    def __init__(self):
        self.db, self.collection = connect_to_database()

    def get_all_cars_paginated(self, page: int, per_page: int):
        skips = per_page * (page - 1)
        cursor = self.collection.find().skip(skips).limit(per_page)
        # cars = json.loads(json_util.dumps(list(cursor)))
        cars = [serialize_doc(car) for car in cursor]
        total_cars = self.collection.count_documents({})
        return cars, total_cars

    def create_car(self, car_data: Cars) -> dict:
        car_data.created_at = datetime.now()
        existing_car = self.collection.find_one(
            {"license_plate": car_data.license_plate}
        )
        if existing_car:
            return {"error": "Biển số xe này đã tồn tại vui lòng thử lại !"}
        existing_owner = self.collection.find_one({"owner_name": car_data.owner_name})
        if existing_owner:
            return {"error": "Tên chủ sở hữu xe này đã tồn tại vui lòng thử lại !"}
        province = helpers.get_province(car_data.license_plate)
        car_data.province = province
        # lưu lịch sử vi phạm
        # violations = asyncio.run(helpers.fetch_violation_data(car_data.license_plate))
        # print("violations->>>", violations)
        # car_data.violations = violations
        result = self.collection.insert_one(car_data.dict())
        car_id = str(result.inserted_id)
        return {"success": True, "car_id": car_id}

    def get_car(self, car_id: str) -> Cars:
        car_data = self.collection.find_one({"_id": ObjectId(car_id)})
        if car_data:
            return Cars(**car_data).dict()
        return None

    def get_carByLicensePlate(self, license_plate: str) -> Cars:
        car_data = self.collection.find_one({"license_plate": license_plate})
        if car_data:
            car_data["id"] = str(car_data.pop("_id"))
            return Cars(**car_data).dict()
        return None

    def get_all_cars(self) -> List[Cars]:
        cars_data = list(self.collection.find())
        return [Cars(**car_data).dict() for car_data in cars_data]

    def update_car(self, car_id: str, car_data: dict) -> dict:
        updated_car = self.collection.find_one_and_update(
            {"_id": ObjectId(car_id)},
            {"$set": car_data},
            return_document=ReturnDocument.AFTER,
        )
        if updated_car:
            updated_car["id"] = str(updated_car.pop("_id"))
            return Cars(**updated_car).dict()
        return None

    def add_checkin_checkout_log(self, license_plate, checkin_checkout_data):
        checkin_checkout_log = CheckinCheckoutLog(**checkin_checkout_data)
        # Retrieve the car document
        car = self.collection.find_one({"license_plate": license_plate})

        if not car:
            return {"status": 404, "message": "Car not found"}
        # If checkin_checkout_logs field is null or empty, create a new list
        if "checkin_checkout_logs" not in car or not car["checkin_checkout_logs"]:
            car["checkin_checkout_logs"] = []
        # Check the last log entry in the checkin_checkout_logs
        if "checkin_checkout_logs" in car and car["checkin_checkout_logs"]:
            last_log = car["checkin_checkout_logs"][-1]
            last_event_type = last_log["event_type"]

            # Ensure alternating event types
            if last_event_type == checkin_checkout_log.event_type:
                next_event_type = (
                    "CHECK_OUT" if last_event_type == "CHECK_IN" else "CHECK_IN"
                )
                return {
                    "status": 400,
                    "message": f"The last event was '{last_event_type}', so the next event must be '{next_event_type}'",
                }

        # Add the new log entry
        result = self.collection.update_one(
            {"license_plate": license_plate},
            {"$push": {"checkin_checkout_logs": checkin_checkout_log.dict()}},
        )
        return (
            {"status": 200, "message": "Check-in/Check-out log added successfully"}
            if result.modified_count > 0
            else {"status": 500, "message": "Failed to add log"}
        )

    def delete_car(self, car_id: str) -> bool:
        result = self.collection.delete_one({"_id": ObjectId(car_id)})
        return result.deleted_count > 0
