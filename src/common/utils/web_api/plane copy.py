from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# 启动浏览器
driver = webdriver.Chrome()

# 打开目标网页
driver.get("https://flights.ctrip.com/booking/DLC-SHA-day-1.html")

# 等待页面加载
time.sleep(5)

# 提取所需数据
flights = driver.find_elements(By.CLASS_NAME, 'flight-item')
for flight in flights:
    print(flight.text)

# 关闭浏览器
driver.quit()