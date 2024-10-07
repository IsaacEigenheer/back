from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import os
import time
import random
import sys
from pathlib import Path

os.chdir('python_backend')
def move_mouse_smoothly(driver, element):
    action = ActionChains(driver)
    action.move_to_element(element)
    action.perform()

def execute_action_with_retry(driver, action_func, max_attempts=2, *args):
    for attempt in range(max_attempts):
        try:
            action_func(driver, *args)
            return  
        except Exception as e:
            time.sleep(random.uniform(2, 5))
    raise

def start(path, current_client):
    pdf_path = path
    filename_id = (Path(pdf_path)).stem
    caminhos_arquivos = []

    if current_client != 'Jacto':
        path_cropped = 'cropped_images'
    else:
        path_cropped = 'crops2'

    for arquivo in os.listdir(path_cropped):
        if filename_id in arquivo:
            caminho_relativo = os.path.join(path_cropped, arquivo)
            caminho_absoluto = os.path.abspath(caminho_relativo)
            caminhos_arquivos.append(caminho_absoluto)

    def convert_to_excel():
        attemps = 0
        while attemps < 3:
            try:

                download_directory = os.path.abspath("Excel")
                
                firefox_options = FirefoxOptions()
                firefox_options.add_argument('--ignore-ssl-errors=yes')
                firefox_options.add_argument('--ignore-certificate-errors')
                #firefox_options.add_argument('--headless')
                profile = webdriver.FirefoxProfile()
                profile.set_preference('browser.download.folderList', 2)
                profile.set_preference('browser.download.manager.showWhenStarting', False)
                profile.set_preference('browser.download.dir', download_directory)
                profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')
                firefox_options.profile = profile
                firefox_service = FirefoxService(executable_path=GeckoDriverManager().install())
                driver = webdriver.Firefox(service=firefox_service, options=firefox_options)

                driver.get('https://www.google.com/')
                driver.execute_script(f'window.location.href = "https://www.fileeagle.com/pdfeagle/image-to-excel";')
                time.sleep(15)
                file_input = driver.find_element('xpath', '//*[@id="file"]')
                move_mouse_smoothly(driver, file_input)
                qnt_arquivos = len(caminhos_arquivos)
                if qnt_arquivos <= 11:
                    for arquivo in caminhos_arquivos:
                        file_input.send_keys(arquivo)
                fileLoop = 0
                if qnt_arquivos > 11:
                    for arquivo in caminhos_arquivos:
                        if fileLoop < 11:
                                file_input.send_keys(arquivo)
                                print(arquivo)
                                fileLoop += 1 
                time.sleep(8)
                driver.execute_script("window.scrollBy(0, 600);")
                language_element = driver.find_element(By.XPATH, '//*[@id="select_language"]/div/div/span/span[1]/span')
                language_element.click()
                english_option = driver.find_element(By.XPATH, '//li[text()="English"]')
                english_option.click()
                time.sleep(4)
                driver.execute_script("window.scrollBy(0, 300);")
                element = driver.find_element(By.ID, 'convert')
                driver.execute_script("arguments[0].click();", element)
                time.sleep(12)
                driver.execute_script("window.scrollBy(0, 100);")
                links = driver.find_elements(By.XPATH, "//a[contains(@title, 'output')]")
                if qnt_arquivos <= 11:
                    u = 0
                    while len(links) < (qnt_arquivos) and u < 308000:
                        links = driver.find_elements(By.XPATH, "//a[contains(@title, 'output')]")
                        u +=1
                if qnt_arquivos > 11:
                    u = 0
                    while len(links) < 11 and u < 308000:
                        links = driver.find_elements(By.XPATH, "//a[contains(@title, 'output')]")
                        u +=1     
                links = driver.find_elements(By.XPATH, "//a[contains(@title, 'output')]")
                for index, link in enumerate(links):
                    link.click()
                    time.sleep(3)
                time.sleep(6)
                driver.quit()
                time.sleep(3)
                if qnt_arquivos > 11:
                    del caminhos_arquivos[0:11]
                    convert_to_excel()
                break
            except:
                attemps += 1

    convert_to_excel()

if __name__ == '__main__':
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    start(arg1, arg2)