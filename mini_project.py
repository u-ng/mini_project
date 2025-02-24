# 라이브러리 모음
from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
# 이미지 저장하기 위해 요청 라이브러리 필요
import requests
import os # 폴더 생성
import csv
import pandas as pd
import geopy.distance # 거리계산 라이브러리

from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")  # Headless 모드 활성화
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
    
def save_csv(name, shop_name, stars, addresses, categories, src):
    import csv
    with open(name, "w", newline="", encoding="CP949") as file:
        writer = csv.writer(file)
        header = ["상호명", "별점", "주소", "카테고리", "이미지"]
        writer.writerow(header)
        for i in range(len(shop_name)):
            writer.writerow([shop_name[i], stars[i], addresses[i], categories[i], src[i]])


def naver_shop(csv_name):
    start_point = "서울기술교육센터"
    url = f"https://map.naver.com/p/search/{start_point}?c=15.00,0,0,0,dh"
    driver = wb.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(url)
    time.sleep(1)

    driver.switch_to.default_content()
    driver.switch_to.frame("searchIframe")
    Advertisement = driver.find_elements(By.CLASS_NAME, "dPXjn")
    data = driver.find_elements(By.CLASS_NAME, "YwYLL")
    start_point_name = data[len(Advertisement)]
    
    time.sleep(1)
    start_point_name.click()
    time.sleep(1)
    driver.back()
    time.sleep(2)
    
    shop = driver.find_element(By.CLASS_NAME, "bubble_keyword_text")
    shop.click()
    time.sleep(2)
    
    driver.switch_to.default_content()
    driver.switch_to.frame("searchIframe")  # 프레임 전환(가게 목록)
    body = driver.find_element(By.CLASS_NAME, "Ryr1F")
    
    shop_name = []
    stars = []
    addresses = []
    categories = []
    src = []
    
    while True:
            last_height = driver.execute_script("return arguments[0].scrollHeight", body)
            # 요소 내에서 아래로 600px 스크롤
            driver.execute_script("arguments[0].scrollTop += 1200;", body)
            # 페이지 로드를 기다림
            time.sleep(1)  # 동적 콘텐츠 로드 시간에 따라 조절
            # 새 높이 계산
            new_height = driver.execute_script("return arguments[0].scrollHeight", body)
            # 스크롤이 더 이상 늘어나지 않으면 루프 종료
            if new_height == last_height:
                break
            last_height = new_height
    data = driver.find_elements(By.XPATH,'//*[@id="_pcmap_list_scroll_container"]/ul/li/div[1]/a[1]/div/div/span[1]') # 음식점 상호명(개수 세기 위해)
    button =  driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div[2]/div[2]/a[7]') # 페이지 넘기는 버튼 (>)
    
    while True:
        i = 0
        while True:
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame("searchIframe")  # 프레임 전환(가게 목록)
                data = driver.find_elements(By.CLASS_NAME, "TYaxT") # 음식점 상호명
                shop_name.append(data[i].text)
                data[i].click()
                time.sleep(2)
                driver.switch_to.default_content()
                driver.switch_to.frame("entryIframe")  # 프레임 전환(가게 목록)
                address = driver.find_element(By.CLASS_NAME, "LDgIH")
                addresses.append(address.text) # 가게 주소
                
                category = driver.find_element(By.CLASS_NAME, "lnJFt")
                categories.append(category.text.split(',')) # 가게 카테고리
                try:
                    src.append(driver.find_element(By.XPATH, '//*[@id="ibu_1"]').get_attribute("src"))
                except:
                    src.append('')
                try:
                    stars.append(driver.find_elements(By.CSS_SELECTOR, ".LXIwF")[0].text.split("\n")[1]) # 별점
                except:
                    stars.append('0')
                i += 1
            except:
                break
        if button.get_attribute("aria-disabled") == "false":
            driver.switch_to.default_content()
            driver.switch_to.frame("searchIframe")  # 프레임 전환(가게 목록)
            button.click() # 페이지 넘기는 버튼 클릭
            time.sleep(3)
        else:
            break
    driver.close()
    save_csv(csv_name, shop_name, stars, addresses, categories, src)

def cal_distance(in_name, out_name):
    df = pd.read_csv(in_name, encoding="CP949")
    for i in range(len(df)):
        if df["주소"][i] == "서울 강서구 내발산동 강서로 289":
            df["주소"][i] = "내발산동 701-9"
    
    start_point = "서울기술교육센터"
    url = f"https://map.naver.com/p/search/{start_point}?c=15.00,0,0,0,dh"
    driver = wb.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(url)
    time.sleep(5)
    
    driver.switch_to.default_content()
    driver.switch_to.frame("searchIframe")  # 프레임 전환(가게 목록)
    
    Advertisement = driver.find_elements(By.CLASS_NAME, "dPXjn")
    data = driver.find_elements(By.CLASS_NAME, "YwYLL")
    start_point_name = data[len(Advertisement)]
    time.sleep(0.5)
    start_point_name.click()
    time.sleep(2)
    
    driver.switch_to.default_content()
    driver.switch_to.frame("entryIframe")
    address_start = driver.find_element(By.CLASS_NAME, "LDgIH").text
    
    url = f'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address_start}' #주소입력
    headers = {
        "X-NCP-APIGW-API-KEY-ID": "mu1lcgmiuq",
        "X-NCP-APIGW-API-KEY": "uczovRUFAgnhNkUJTkq7kdf8KYixBZy7fA42KFtp"
    } # header에 api-key
    data = requests.get(url,headers=headers).json()
    x_start =data["addresses"][0]['x']
    y_start =data["addresses"][0]['y']
    
    distance = []
    driver.clsoe()
    for i in range(len(df)):
        address = df["주소"][i]
        url = f'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}' #주소입력
        headers = {
            "X-NCP-APIGW-API-KEY-ID": "mu1lcgmiuq",
            "X-NCP-APIGW-API-KEY": "uczovRUFAgnhNkUJTkq7kdf8KYixBZy7fA42KFtp"
        } # header에 api-key
        data = requests.get(url,headers=headers).json()
        x =data["addresses"][0]['x']
        y =data["addresses"][0]['y']
        dis = geopy.distance.distance((y_start, x_start), (y,x)).km
        dis = round(dis * 1000, 0)
        distance.append(int(dis)) #(37.5423051, 126.8412894) =>대한상공회의소 좌표

    df["거리"] = distance
    df.to_csv(out_name, encoding="CP949")

def kakao_shop():
    with open ("shop_distance.csv", "r") as file:
        df = pd.read_csv(file)
    url = "https://m.map.kakao.com/"
    driver = wb.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(url)
    search_kakao = driver.find_element(By.XPATH,'//*[@id="innerQuery"]')
    driver.find_element(By.XPATH,'//*[@id="innerQuery"]').click()
    search_kakao.click()
    search_kakao.send_keys("a")
    shop_name = []
    stars = []
    addresses = []
    categories = []
    # def check_kor(text):
    #     p = re.compile('[ㄱ-힣]')
    #     r = p.search(text)
    #     if r is None:
    #         return False
    #     else:
    #         return True
    def apn(i):
        name=df["상호명"][i]
        star=driver.find_element(By.XPATH,'//*[@id="mArticle"]/div[1]/div/div[1]/div[1]/a[1]/span[1]/span[1]').text
        adress= driver.find_element(By.CSS_SELECTOR,'#mArticle > div.cont_locationinfo > div > div:nth-child(2) > div > span.txt_address').text
        category= driver.find_element(By.CSS_SELECTOR,'#mArticle > div.cont_essential > div > div.place_details > span > span.txt_location').text.split()
        shop_name.append(name)
        stars.append(star)
        addresses.append(adress)
        categories.append(category)
    def null_apn(i):
        name=df["상호명"][i]
        star=0
        adress=df["주소"][i]
        category=df["카테고리"][i]
        shop_name.append(name)
        stars.append(star)
        addresses.append(adress)
        categories.append(category)
    for i in range(len(df)):
        search_kakao = driver.find_element(By.XPATH,'//*[@id="innerQuery"]')
        search_kakao.click()
        driver.find_element(By.XPATH,'//*[@id="insideTotalSearchForm"]/fieldset/div/button/span').click()
        try:
            search_kakao.send_keys(df["상호명"][i])
            search_kakao.send_keys(Keys.ENTER)
            time.sleep(1)
            driver.find_element(By.CSS_SELECTOR,"#sortSelect").click()
            time.sleep(0.5)
            driver.find_element(By.CSS_SELECTOR,"#sortSelect > option:nth-child(2)").click()
            driver.find_element(By.CSS_SELECTOR,'#placeList > li.search_item.base > a.link_result > span > span.txt_tit > strong').click()
            apn(i)
            driver.back()
            continue
        except:
            a = df["상호명"][i].split()
            search_kakao = driver.find_element(By.XPATH,'//*[@id="innerQuery"]')
            search_kakao.click()
            time.sleep(1)
            driver.find_element(By.XPATH,'//*[@id="insideTotalSearchForm"]/fieldset/div/button/span').click()
        try:
            search_kakao.send_keys(a[0])
            search_kakao.send_keys(Keys.ENTER)
            time.sleep(0.5)
            driver.find_element(By.CSS_SELECTOR,"#sortSelect").click()
            time.sleep(0.5)
            driver.find_element(By.CSS_SELECTOR,"#sortSelect > option:nth-child(2)").click()
            driver.find_element(By.XPATH,'//*[@id="placeList"]/li[1]/a[1]/span[2]/span[1]/strong').click()
            time.sleep(1)
            apn(i)
            driver.back()
            pass
        except:
            null_apn(i)
            pass
    
    save_csv("shop_kakao.csv")

naver_shop("shop.csv")
cal_distance("shop.csv", "shop_distance.csv")

kakao_shop()
