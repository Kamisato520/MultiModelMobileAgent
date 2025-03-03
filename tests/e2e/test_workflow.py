import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def driver():
    """设置Selenium WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def test_login_workflow(driver, test_user):
    """测试登录流程"""
    # 访问登录页面
    driver.get('http://localhost:5000/login')
    
    # 输入登录信息
    username_input = driver.find_element(By.NAME, 'username')
    password_input = driver.find_element(By.NAME, 'password')
    submit_button = driver.find_element(By.ID, 'login-button')
    
    username_input.send_keys(test_user.username)
    password_input.send_keys('password123')
    submit_button.click()
    
    # 等待重定向到仪表板
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'dashboard'))
    )
    
    # 验证登录成功
    assert 'dashboard' in driver.current_url

def test_create_task_workflow(driver, test_user, test_device):
    """测试创建任务流程"""
    # 先登录
    # ... 登录代码 ...
    
    # 导航到任务创建页面
    driver.get('http://localhost:5000/tasks/create')
    
    # 选择设备
    device_select = driver.find_element(By.ID, 'device-select')
    device_select.click()
    device_option = driver.find_element(By.XPATH, 
        f"//option[@value='{test_device.device_id}']")
    device_option.click()
    
    # 输入任务内容
    input_textarea = driver.find_element(By.ID, 'task-input')
    input_textarea.send_keys('test automation task')
    
    # 提交任务
    submit_button = driver.find_element(By.ID, 'submit-task')
    submit_button.click()
    
    # 等待任务创建成功提示
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))
    )
    
    # 验证任务创建成功
    success_message = driver.find_element(By.CLASS_NAME, 'success-message')
    assert 'Task created successfully' in success_message.text 