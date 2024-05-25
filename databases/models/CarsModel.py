import uuid
from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field, root_validator
from datetime import datetime


class CheckinCheckoutLog(BaseModel):
    time: str
    event_type: str  # 'CHECKIN' or 'CHECKOUT'


class Cars(BaseModel):
    id: Optional[str] = None
    # id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")  # Sử dụng str(uuid.uuid4()) để tạo UUID mới
    province: str = None
    checkin_time: str
    license_plate: str
    violations: Optional[Union[List[Dict[str, str]], str]] = (
        None  # Kiểu dữ liệu Union cho phép sử dụng nhiều kiểu dữ liệu khác nhau
    )
    checkin_checkout_logs: Optional[List[CheckinCheckoutLog]] = None
    owner_name: str
    vehicle_type: str
    brand: str
    model: str
    engine_capacity: str
    original_image: str
    cropped_image: str
    checkout_time: str = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        allow_population_by_field_name = True


# province: Tỉnh thành của xe (string có chấp nhận dấu).
# checkin_time: Thời gian checkin của xe (string).
# license_plate: Biển số xe (string).
# violations: Danh sách vi phạm của xe (JSON).
# owner_name: Tên chủ xe (string).
# vehicle_type: Loại xe (string) như ô tô, xe máy, xe điện.
# brand: Hãng xe (string).
# model: Dòng xe (string).
# engine_capacity: Phân khối xe (string).
