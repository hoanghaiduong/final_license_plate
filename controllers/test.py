from cars import CarController
from databases.models.CarsModel import Cars

# Sử dụng controller
if __name__ == "__main__":
    # Khởi tạo controller
    controller = CarController()

    # # Tạo một đối tượng Cars
    car = Cars(
        province="Hanoi",
        checkin_time="2024-05-17 10:00:00",
        license_plate="29F-12345",
        owner_name="John Doe",
        vehicle_type="Car",
        brand="Toyota",
        model="Camry",
        engine_capacity="2000cc",
    )
    
    # Sử dụng đối tượng Cars để tạo một xe
    car_id = controller.create_car(car)
    print("Created car with ID:", car_id)

    # # Lấy thông tin của một xe
    # car = controller.get_car(car_id)
    # print("Car info:", car)

    # Lấy thông tin của tất cả các xe
    all_cars = controller.get_all_cars()
    print("All cars:", all_cars)

    # Cập nhật thông tin của một xe
    # updated = controller.update_car(car_id, {"province": "Ho Chi Minh City"})
    # print("Car updated:", updated)

    # Xóa một xe
    # deleted = controller.delete_car(car_id)
    # print("Car deleted:", deleted)
