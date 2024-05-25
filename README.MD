# Car Check-In/Check-Out Logging System

This project is a Car Check-In/Check-Out Logging System, which allows users to log the check-in and check-out times of cars, ensuring alternating event types (CHECK_IN and CHECK_OUT).

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)

## Features

- Log check-in and check-out times for cars.
- Ensure alternating event types to maintain correct order of events.
- Retrieve and display check-in/check-out logs for each car.

## Technologies Used

- **Python**: Programming language used for the backend logic.
- **Pydantic**: Data validation and settings management using Python type annotations.
- **MongoDB**: NoSQL database used for storing car data and logs.

## Installation

1. Tạo và kích hoạt môi trường ảo:

   ```bash
   python -m venv venv

   ```

2. Kích hoạt môi trường ảo:
   Trên macOS/Linux:

   ```bash
   source venv/bin/activate
   ```

   Trên Windows:

   ```bash
   venv\Scripts\activate
   ```

3. Cài đặt các gói phụ thuộc:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Cài đặt các gói npm (nếu dự án có phần frontend hoặc cần npm):

   ```bash
   npm install --force
   ```

5. Chạy ứng dụng:

   ```bash

   python app.py
   ```
