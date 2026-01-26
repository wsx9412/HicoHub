import os
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import json

# 1. 설정 (깃허브 Secret 환경변수에서 가져옴)
# 구글 서비스 계정 키(JSON)를 환경변수에 등록해야 합니다.
creds_json = os.environ.get('GOOGLE_SHEETS_CREDS')
creds_dict = json.loads(creds_json)
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# 2. 구글 시트 열기 (본인의 시트 ID 입력)
# 시트 URL의 /d/ 와 /edit 사이의 문자열입니다.
SHEET_ID = '1k8zmxLBPXz2uAUbjE8YwIfcUdlcL-S2VLZlkqU1cjsc' 
sheet = client.open_by_key(SHEET_ID).sheet1

# 3. 뉴스 검색 키워드 설정 (환경변수에서 가져오거나 기본값 사용)
keyword = os.environ.get('NEWS_KEYWORD', '') 
search_url = f"https://www.google.com/search?q={keyword if keyword else '최신뉴스'}&tbm=nws"

# 4. 크롤링 실행
headers = {"User-Agent": "Mozilla/5.0"}
res = requests.get(search_url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

news_list = []
# 제목 행 추가 (헤더) - 퀴즈 앱에서 0번 줄을 제목으로 쓰기로 했으므로 유지합니다.
news_list.append(["문제(뉴스 제목)", "정답(키워드)"])

for g in soup.select('div.SoS9be'):
title_element = g.select_one('div.n0uTEe')
if title_element:
title = title_element.text
news_list.append([title, keyword if keyword else '최신뉴스'])

# 5. 시트 초기화 후 새로운 데이터 쓰기
if len(news_list) > 1: # 제목 외에 실제 뉴스 데이터가 있을 때만 실행
sheet.clear() # 기존에 있던 모든 내용을 깨끗하게 지웁니다.
sheet.update('A1', news_list) # A1 셀부터 리스트 전체를 덮어씌웁니다.
print(f"성공: 기존 데이터를 지우고 {len(news_list)-1}개의 최신 뉴스로 업데이트했습니다.")
