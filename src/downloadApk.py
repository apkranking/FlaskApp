import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

def downloadApk(packageName, CHROME_DRIVER_DIR, DOWNLOAD_PATH):    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_DIR, options=options)

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': DOWNLOAD_PATH}}
    driver.execute("send_command", params)
    
    driver.get('https://m.apkpure.com/search')

    searchBox = driver.find_element_by_xpath('//*[@id="so"]/div/div[2]/input')
    searchBox.send_keys(packageName)

    submitButton = driver.find_element_by_xpath('//*[@id="so"]/div/div[4]')
    submitButton.click()
    time.sleep(5)
    appLocation = driver.find_element_by_xpath('//*[@id="search-res"]/li[1]/dl/a')
    appLocation.click()
    time.sleep(5)
    try:
        downloadButton = driver.find_element_by_xpath('//*[@id="down_btns"]/div/a[1]')
    except Exception:
        downloadButton = driver.find_element_by_xpath('//*[@id="down_btns"]/a')
    downloadButton.click()
    time.sleep(10)
    driver.quit()