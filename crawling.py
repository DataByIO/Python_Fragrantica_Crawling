#common method
import requests
import pandas as pd
import os
from selenium.webdriver.common.by import By
from selenium import webdriver
#from selenium.webdriver.chrome.service import Service #운영환경
from selenium.webdriver.chrome.service import Service as service #개발환경
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.support import expected_conditions as EC

def init():
    #전역변수(Global) 영역
    counter0 = 0
    counter2 = 2
    counter3 = 3
    hrefValue = []
    perfumeName = []
    PerfumeBrandName = []
    imgUrl = []

    #크롬 드라이브 로드
    options = Options()
    options.binary_location= 'C:/Program Files/Google/Chrome/Application/chrome.exe'


    # Headless 모드 설정
    #options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
    #options.add_argument('--disable-gpu')  # GPU 비활성화 (Headless 모드에서 필요함)
    #options.add_argument('--no-sandbox')  # 안전모드 비활성화 (리눅스 환경에서 주로 필요)
    #options.add_argument('--remote-debugging-port=9222')  # 디버깅 포트 열기 (선택적)

    prefs = {
        "profile.managed_default_content_settings.images": 2,  # 이미지 로딩 비활성화
        "profile.managed_default_content_settings.stylesheets": 2,  # 스타일시트 비활성화
        "profile.managed_default_content_settings.cookies": 2,  # 쿠키 비활성화
        "profile.managed_default_content_settings.javascript": 2  # JavaScript 비활성화
    }
    options.add_experimental_option("prefs", prefs)
    #사이트 오픈 후 브랜드 리스트 크롤링
    designersOpen = f"https://www.fragrantica.com/designers"
    # WebDriver 객체 생성
    driver = webdriver.Chrome(service=service(ChromeDriverManager().install()), options=options)
    driver.get(designersOpen)

    # 브랜드 리스트를 가지고옴 -> 메인에 보이는 브랜드 리스트는 120가지의 브랜드 -> 반복문은 0부터 시작이라 1를 기준으로 120바퀴 돌도록 설정
    def perfumeBrand(counter0, counter2, counter3, PerfumeBrandName, perfumeName):
        for a in range(2, 122):
            try:
                brandNameData = driver.find_element(By.XPATH, f'//*[@id="main-content"]/div[1]/div[1]/div[4]/div[{a}]/a')                
                brandNameDataAppend = brandNameData.get_attribute('href')
                PerfumeBrandName.append(brandNameDataAppend.split('/')[-1].replace('.html', ''))#문자열을 잘라서 가지고옴
                
                #크롤링을 진행한 브랜드의 폴더 생성
                os.makedirs(PerfumeBrandName[counter0], exist_ok=True)  
                print(f"생성한 폴더명::: {PerfumeBrandName[counter0]}")
                counter0 += 1
            except Exception as e:
                print("요소를 찾을 수 없음:", e)
        driver.close()
    #크롤링 진행을 완료 후 현재 열려있는 창을 닫음

    def perfumeList(counter0, counter2, counter3, PerfumeBrandName, perfumeName, hrefValue, imgUrl):
        counter0 = 0
        for a2 in range(len(PerfumeBrandName)): #120번 반복이 필요함 각 브랜드 마다 접근ㅇ ㅣ필요하기 때문...
            url = f"https://www.fragrantica.com/designers/{PerfumeBrandName[a2]}.html"
            # 페이지 열기
            
            driver = webdriver.Chrome(service=service(ChromeDriverManager().install()), options=options)
            driver.get(url)
            try:
                elementsCount = driver.find_elements(By.CSS_SELECTOR, '.prefumeHbox.px1-box-shadow')
            except Exception as e:
                print("요소를 찾을 수 없음:", e)
            if len(elementsCount) > 10: #향수가 100개 이상인 경우
                elementsCount[:10]  # 100개만 남기고 나머지는 버리기
            for b in range(len(elementsCount)):#product 수 만큼 실행 향수가 93개 있으면 93번 돌아돌아~
            # 첫번째 배열 브랜드의 제품 상세 링크를 반복문으로 가지고옴
                try:#특정 영역에서 Exception 발생시 count는 증가(다음배열의 데이터로 넘어가기 위해) 처리
                    a_tag_find = driver.find_element(By.XPATH, f'//*[@id="brands"]/div[{counter3}]/div[1]/div[3]/h3/a')
                    a_tag_attribute = a_tag_find.get_attribute('href')
                    hrefValue.append(a_tag_attribute)  # href 속성 값 가져오기
                    img_tag = driver.find_element(By.XPATH, f'//*[@id="brands"]/div[{counter3}]/div[1]/div[2]/img')    
                    imgurlTr = img_tag.get_attribute('src')
                    # 이미지변환 's.'를 '375x500.'으로 변환
                    imgUrlval = imgurlTr.replace('/s.', '/375x500.')
                    imgUrl.append(imgUrlval)
                    text = elementsCount[counter0].text
                    perfumeName.append([text.split("\n")[0]])  # \n1을 기준으로 분리하고 첫 번째 부분 취함
                    counter0 += 1
                    counter3 += 1
                except Exception as e:
                    print(f"오류 발생:::: {counter3}번째 배열은 향수 데이터가 아닙니다.")
                    counter0 += 1
                    counter3 += 1
            imgSeve(imgUrl, PerfumeBrandName, perfumeName)
            driver.close()
            jsonSeve(hrefValue, perfumeName)
        imgUrl = []
        hrefValue = []
        perfumeName = []
        PerfumeBrandName.pop(0)
        perfumeName.pop(0)
        print(perfumeName)  # 출력: perfumeName
                

    def imgSeve(imgUrl, PerfumeBrandName, perfumeName):
        for i in range(len(imgUrl)):#imgUrl의 수 만큼 반복
            if imgUrl:  # src가 존재하는 경우
                try:
                    # 이미지를 다운로드
                    response = requests.get(imgUrl[i])
                    # 이미지가 정상적으로 응답을 받았다면 저장
                    if response.status_code == 200:
                        # 파일명 설정 (이미지 번호로 설정)
                        imgName = f"{perfumeName[i][0]}.jpg"  # .jpg 확장자 사용
                        img_path = os.path.join(PerfumeBrandName[0], imgName)
                        # 이미지를 로컬에 저장
                        with open(img_path, 'wb') as file:
                            file.write(response.content)
                        print(f"이미지::: {imgName} 저장 완료!")
                    else:
                        print(f"이미지 다운로드 실패::: {imgUrl[i]}")
                except Exception as e:
                    print(f"이미지 다운로드 중 오류 발생::: {e}")
        
                
    def jsonSeve(hrefValue, perfumeName):
        for i in range(len(hrefValue)):#hrefValue의 수 만큼 반복
            driver = webdriver.Chrome(service=service(ChromeDriverManager().install()), options=options)
            driver.get(hrefValue[i])
            driver.minimize_window()
            print(f"Json Data Mapping perfumeName::: {perfumeName[i][0]} - PAGE OPEN")
            accordList = driver.find_elements(By.CSS_SELECTOR, '.cell.accord-box')
            accord = []
            for e in range(len(accordList)):
                accord.append(accordList[e].text)
            accordResult = ', '.join(accord)
            gender = driver.find_element(By.XPATH, f'//*[@id="toptop"]/h1/small').text
            # 현재 작업 디렉토리 가져오기
            current_dir = os.getcwd()
            # 엑셀 파일 경로 (현재 경로에서 엑셀 파일을 찾기)
            excel_file = os.path.join(current_dir, 'perfume_data.xlsx')  # 'data.xlsx'가 현재 경로에 있다고 가정
            json_data = [{"perfumeBrandName": f"{PerfumeBrandName[0]}",
                            "perfumeName": f"{perfumeName[i][0]}",
                            "hrefValue": f"{hrefValue[i]}",
                            "accord": f"{accordResult}",
                            "gender" : f"{gender}"}]
            
            # JSON 데이터를 DataFrame으로 변환
            new_data = pd.json_normalize(json_data)
            # 기존 엑셀 파일 읽기 (존재하지 않으면 빈 DataFrame 생성)
            if os.path.exists(excel_file):
                existing_data = pd.read_excel(excel_file, engine='openpyxl')
            else:
                existing_data = pd.DataFrame()  # 기존 파일이 없으면 빈 DataFrame 사용
            # 새로운 데이터를 기존 데이터에 추가
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)
            # 결합된 데이터를 엑셀 파일에 저장
            combined_data.to_excel(excel_file, index=False, engine='openpyxl')
            driver.close()
            print(f"Json Data Mapping perfumeName::: {perfumeName[i][0]} - PAGE CLOSE Count: [{[i]}]")
            print(f"JSON 데이터를 기존 엑셀 파일에 추가했습니다. 파일 경로::: {excel_file} - {perfumeName[i][0]}")      

    
    perfumeBrand(counter0, counter2, counter3, PerfumeBrandName, perfumeName)
    perfumeList(counter0, counter2, counter3, PerfumeBrandName, perfumeName, hrefValue, imgUrl)

init()
