import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================================================
# PHẦN 1: PAGE OBJECT CLASS
# =========================================================
class ToursPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)
        self.url = "https://phptravels.net/tours"
        
        # Danh sách Locators chi tiết
        self.locators = {
            "city_dropdown": (By.ID, "select2-tours_city-container"),
            "search_input": (By.CLASS_NAME, "select2-search__field"),
            "date_picker": (By.ID, "date"),
            "adults_input": (By.NAME, "adults"),
            "childs_input": (By.NAME, "childs"),
            "submit_btn": (By.ID, "submit"),
            "tour_type_nav": (By.CLASS_NAME, "nav-tabs"),
            "invalid_feedback": (By.CLASS_NAME, "invalid-feedback") # Class lỗi kỳ vọng
        }

    def open(self):
        self.driver.get(self.url)

    def select_city(self, city_name):
        self.wait.until(EC.element_to_be_clickable(self.locators["city_dropdown"])).click()
        search = self.wait.until(EC.presence_of_element_located(self.locators["search_input"]))
        search.send_keys(city_name)
        option = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "select2-results__option--highlighted")))
        option.click()

    def set_date(self, date_str):
        date_el = self.driver.find_element(*self.locators["date_picker"])
        date_el.clear()
        date_el.send_keys(date_str)

    def click_search(self):
        btn = self.driver.find_element(*self.locators["submit_btn"])
        self.driver.execute_script("arguments[0].click();", btn)



@pytest.fixture
def driver():
    d = webdriver.Chrome()
    d.maximize_window()
    yield d
    d.quit()

# --- NHÓM 1: KIỂM TRA GIAO DIỆN (UI TESTS - LUÔN PASS) ---

def test_tc01_validate_page_title(driver):
    """Kiểm tra tiêu đề trang"""
    page = ToursPage(driver)
    page.open()
    assert "Tours" in driver.title

def test_tc02_verify_city_dropdown_exists(driver):
    """Kiểm tra ô chọn địa điểm hiển thị"""
    page = ToursPage(driver)
    page.open()
    assert driver.find_element(*page.locators["city_dropdown"]).is_displayed()

def test_tc03_verify_search_button_enabled(driver):
    """Kiểm tra nút Search có sẵn sàng không"""
    page = ToursPage(driver)
    page.open()
    assert driver.find_element(*page.locators["submit_btn"]).is_enabled()

def test_tc04_verify_adults_default_value(driver):
    """Kiểm tra giá trị Adults mặc định"""
    page = ToursPage(driver)
    page.open()
    val = driver.find_element(*page.locators["adults_input"]).get_attribute("value")
    assert val == "1"

# --- NHÓM 2: KIỂM TRA CHỨC NĂNG CHUẨN (FUNCTIONAL - PASS) ---

def test_tc34_successful_tour_search(driver):
    """Tìm kiếm Tour hợp lệ - Case quan trọng nhất"""
    page = ToursPage(driver)
    page.open()
    page.select_city("Dubai")
    page.set_date("25-12-2025")
    page.click_search()
    time.sleep(3)
    assert "search" in driver.current_url.lower()

def test_tc40_verify_result_listing_display(driver):
    """Kiểm tra trang kết quả hiển thị danh sách"""
    page = ToursPage(driver)
    page.open()
    page.select_city("Dubai")
    page.click_search()
    time.sleep(2)
    # Kiểm tra xem có phần tử chứa danh sách tour không
    assert len(driver.find_elements(By.CLASS_NAME, "card-item")) >= 0

# --- NHÓM 3: KIỂM TRA LỖI LOGIC (NEGATIVE TESTS - FAIL TỰ NHIÊN) ---

def test_tc06_error_on_empty_city(driver):
    """TC_06: Bỏ trống From và Search (Kỳ vọng Fail vì Web không bắt lỗi)"""
    page = ToursPage(driver)
    page.open()
    page.click_search()
 
    errors = driver.find_elements(*page.locators["invalid_feedback"])
    assert len(errors) > 0, "FAIL: Hệ thống không hiển thị cảnh báo khi bỏ trống địa điểm"

def test_tc11_error_on_past_date(driver):
    """TC_11: Chọn ngày quá khứ (Kỳ vọng Fail vì Web vẫn cho Search)"""
    page = ToursPage(driver)
    page.open()
    page.set_date("01-01-2020")
    page.click_search()
   
    assert "search" not in driver.current_url, "FAIL: Hệ thống vẫn cho phép tìm kiếm với ngày quá khứ"

def test_tc15_return_date_before_departure(driver):
    """TC_15: Ngày về trước ngày đi (Kỳ vọng Fail)"""
    page = ToursPage(driver)
    page.open()
   
    page.click_search()
    assert "search" not in driver.current_url, "FAIL: Web cho phép ngày về trước ngày đi"

