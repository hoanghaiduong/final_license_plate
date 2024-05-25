import json
import math
import re


# import undetected_chromedriver as uc
import asyncio

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from function.provinces import PROVINCE_CODES


# license plate type classification helper function
def linear_equation(x1, y1, x2, y2):
    b = y1 - (y2 - y1) * x1 / (x2 - x1)
    a = (y1 - b) / x1
    return a, b


def check_point_linear(x, y, x1, y1, x2, y2):
    a, b = linear_equation(x1, y1, x2, y2)
    y_pred = a * x + b
    return math.isclose(y_pred, y, abs_tol=3)


# detect character and number in license plate
def read_plate(yolo_license_plate, im):
    LP_type = "1"
    results = yolo_license_plate(im)
    bb_list = results.pandas().xyxy[0].values.tolist()
    if len(bb_list) == 0 or len(bb_list) < 7 or len(bb_list) > 10:
        return "unknown"
    center_list = []
    y_mean = 0
    y_sum = 0
    for bb in bb_list:
        x_c = (bb[0] + bb[2]) / 2
        y_c = (bb[1] + bb[3]) / 2
        y_sum += y_c
        center_list.append([x_c, y_c, bb[-1]])

    # find 2 point to draw line
    l_point = center_list[0]
    r_point = center_list[0]
    for cp in center_list:
        if cp[0] < l_point[0]:
            l_point = cp
        if cp[0] > r_point[0]:
            r_point = cp
    for ct in center_list:
        if l_point[0] != r_point[0]:
            if (
                check_point_linear(
                    ct[0], ct[1], l_point[0], l_point[1], r_point[0], r_point[1]
                )
                == False
            ):
                LP_type = "2"

    y_mean = int(int(y_sum) / len(bb_list))
    size = results.pandas().s

    # 1 line plates and 2 line plates
    line_1 = []
    line_2 = []
    license_plate = ""
    if LP_type == "2":
        for c in center_list:
            if int(c[1]) > y_mean:
                line_2.append(c)
            else:
                line_1.append(c)
        for l1 in sorted(line_1, key=lambda x: x[0]):
            license_plate += str(l1[2])
        license_plate += "-"
        for l2 in sorted(line_2, key=lambda x: x[0]):
            license_plate += str(l2[2])
    else:
        for l in sorted(center_list, key=lambda x: x[0]):
            license_plate += str(l[2])
    return license_plate


# def format_license_plate(lp):
#     if lp.isdigit() or re.search(r'[^\w.-]', lp):
#         return None

#     # Biểu thức chính quy để tìm các nhóm chữ cái và số
#     pattern = r'([A-Z]+)(\d+)'

#     # Tìm các nhóm chữ cái và số trong chuỗi biển số và thực hiện thay thế
#     formatted_lp = re.sub(pattern, r'\1-\2', lp)

#     if formatted_lp:

#         parts = formatted_lp.split("-")
#         if len(parts) == 2:
#             before = parts[0]  # Nhóm biển trước
#             after = parts[1]   # Nhóm biển sau
#             # Kiểm tra độ dài của nhóm số để xử lý
#             if len(after) == 5:
#                 # Chia nhóm số thành phần trước và sau dấu chấm
#                 after = f"{after[:3]}.{after[3:]}"
#                 print('vào đây 2',formatted_lp)
#             # Kiểm tra xem nhóm biển trước có đúng định dạng không
#             if len(before) == 3 and before[:-1].isdigit() and before[-1].isalpha():
#                 print('vào đây 3',formatted_lp)
#                 # Kết hợp chữ cái và số, cách nhau bởi dấu gạch ngang
#                 formatted_lp = f"{before}-{after}"
#                 return formatted_lp


#     # Trả về None nếu không tìm thấy kết quả phù hợp
#     return None
def format_license_plate(lp):
    # Loại bỏ tất cả các ký tự đặc biệt ngoại trừ dấu "-" từ chuỗi biển số xe
    lp_cleaned = re.sub(r"[^\w]", "", lp)

    return lp_cleaned


def get_province(license_plate):
    code = license_plate[:2]
    return PROVINCE_CODES.get(code, "Unknown Province")


# driver = uc.Chrome(headless=True, use_subprocess=True)
# def fetch_violation_data(license_number_value):

#     try:
#         # Mở trang web và thực hiện các thao tác
#         print("Opening website...")
#         driver.get('https://phatnguoi.com')
#         time.sleep(1)

#         print("Finding input field...")
#         license_input = driver.find_element(By.ID, 'licenseNumber')
#         license_input.send_keys(license_number_value)
#         time.sleep(1)

#         print("Clicking submit button...")
#         submit_button = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div/form/div[2]/button')
#         submit_button.click()
#         time.sleep(5)

#         print("Extracting result text...")
#         result_element = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div/div')
#         result_text = result_element.text

#         return result_text

#     except Exception as err:
#         print("An error occurred:", err)
#         return None
#     finally:
#         print("Collecting data successfully")
#         driver.quit()
#         #os.system('taskkill /F /IM chrome.exe /T')


# async def fetch_violation_data(license_number_value):
#     try:
#         async with async_playwright() as p:
#             browser = await p.firefox.launch(headless=True)
#             page = await browser.new_page()
#             print("Opening website...")
#             await page.goto("https://phatnguoixe.com")

#             async def submit_license_plate():
#                 print("Finding input field...")
#                 license_input = await page.wait_for_selector('//*[@id="bienso"]')
#                 await license_input.fill(license_number_value)
#                 print("Clicking submit button...")
#                 submit_button = await page.wait_for_selector('//*[@id="submit"]')
#                 await submit_button.click()

#             print("Finding input field...")
#             await submit_license_plate()
#             await asyncio.sleep(5)  # Use asyncio.sleep instead of time.sleep
#             print("Extracting result text...")
#             result_element = await page.wait_for_selector('//*[@id="resultValue"]')
#             result_html = await result_element.inner_html()

#             # Check for incorrect format message
#             if "Biển số xe không đúng định dạng" in result_html:
#                 print("Incorrect format detected. Retrying...")
#                 type_car_option = await page.wait_for_selector(
#                     '//*[@id="frmSubmit"]/label[2]/input'
#                 )
#                 await type_car_option.click()
#                 await submit_license_plate()
#                 await asyncio.sleep(5)
#             elif (
#                 "Không tìm thấy vi phạm" in result_html
#                 or "Không tìm thấy lỗi vi phạm" in result_html
#             ):
#                 return json.dumps(
#                     {"status": 200, "num_violations": 0, "violations": []},
#                     ensure_ascii=False,
#                 )
#             elif "Đang có rất đông lượt tìm kiếm" in result_html:
#                 return json.dumps(
#                     {
#                         "status": 400,
#                         "message": "Server is overload ! Please try again",
#                     },
#                     ensure_ascii=False,
#                 )
#             # Parse the HTML content
#             soup = BeautifulSoup(result_html, "html.parser")

#             # Extract general violation info
#             header = soup.find("h3", class_="css-1oevxvn")
#             num_violations = int(header.find("span", style="color: red;").text)

#             # Extract details of each violation
#             violations = []
#             tables = soup.find_all("table", class_="css_table")
#             for table in tables:
#                 violation = {}
#                 rows = table.find_all("tr")
#                 for row in rows:
#                     cells = row.find_all("td")
#                     if len(cells) == 2:
#                         key = cells[0].get_text(strip=True).replace(":", "")
#                         value = cells[1].get_text(strip=True)
#                         violation[key] = value
#                     elif len(cells) == 1 and "colspan" in cells[0].attrs:
#                         key = cells[0].get_text(strip=True)
#                         value = cells[0].next_sibling.get_text(strip=True)
#                         # Special handling for "Nơi giải quyết vụ việc"
#                         if key.strip() == "Nơi giải quyết vụ việc:":
#                             # Concatenate values from subsequent rows until a row without colspan is encountered
#                             next_row = row.find_next_sibling("tr")
#                             while next_row and "colspan" in next_row.find("td").attrs:
#                                 value += " " + next_row.find("td").get_text(strip=True)
#                                 next_row = next_row.find_next_sibling("tr")
#                             violation[key] = value
#                         elif value.strip() != "":
#                             violation[key] = value
#                     else:
#                         violation[key] = value

#                 violations.append(violation)

#             # Create result dictionary
#             result_data = {
#                 "status": 200,
#                 "num_violations": num_violations,
#                 "violations": violations,
#             }

#             return json.dumps(result_data, ensure_ascii=False)
#     except Exception as err:
#         print("An error occurred:", err)
#         return json.dumps({"error": str(err)}, ensure_ascii=False)
#     finally:
#         print("Collecting data successfully")
#         await browser.close()


async def fetch_violation_data(license_number_value):
    try:
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            page = await browser.new_page()
            print("Opening website...")
            await page.goto("https://phatnguoixe.com")

            async def submit_license_plate():
                print("Finding input field...")
                license_input = await page.wait_for_selector('//*[@id="bienso"]')
                await license_input.fill(license_number_value)
                print("Clicking submit button...")
                submit_button = await page.wait_for_selector('//*[@id="submit"]')
                await submit_button.click()

            await submit_license_plate()
            await asyncio.sleep(3)  # Use asyncio.sleep instead of time.sleep
            print("Extracting result text...")
            result_element = await page.wait_for_selector('//*[@id="resultValue"]')
            result_html = await result_element.inner_html()
            result_text = await result_element.inner_text()
            # Check for incorrect format message
            if "Biển số xe không đúng định dạng" in result_html:
                print("Incorrect format detected. Retrying...")
                type_car_option = await page.wait_for_selector(
                    '//*[@id="frmSubmit"]/label[2]/input'
                )
                await type_car_option.click()
                await submit_license_plate()
                await asyncio.sleep(3)
                # After retrying, update result_html again
                result_element = await page.wait_for_selector('//*[@id="resultValue"]')
                result_html = await result_element.inner_html()
                result_text = await result_element.inner_text()

            if (
                "Không tìm thấy vi phạm" in result_html
                or "Không tìm thấy lỗi vi phạm" in result_html
            ):

                return json.dumps(
                    {"status": 200, "message": "Không tìm thấy lỗi vi phạm"},
                    ensure_ascii=False,
                )
            elif "Đang có rất đông lượt tìm kiếm" in result_html:
                return json.dumps(
                    {
                        "status": 400,
                        "message": "Server is overload ! Please try again",
                    },
                    ensure_ascii=False,
                )

            # Parse the HTML content
            soup = BeautifulSoup(result_html, "html.parser")

            # Find all center tags
            center_tags = soup.find_all("center")
            # Remove the last center tag
            if len(center_tags) >= 2:
                center_tags[-1].decompose()
                center_tags[-2].decompose()

            # Get the inner text of the result element
            result_text_clean = soup.get_text()

            # Create result dictionary
            result_data = {
                "status": 200,
                "message": result_text_clean,
            }

            return json.dumps(result_data, ensure_ascii=False)
    except Exception as err:
        print("An error occurred:", err)
        return json.dumps({"error": str(err)}, ensure_ascii=False)
    finally:
        print("Collecting data successfully")
        await browser.close()
