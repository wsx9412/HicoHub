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
SHEET_ID = '여러분의_시트_ID' 
sheet = client.open_by_key(SHEET_ID).sheet1

# 3. 뉴스 검색 키워드 설정 (환경변수에서 가져오거나 기본값 사용)
keyword = os.environ.get('NEWS_KEYWORD', '') 
search_url = f"https://www.google.com/search?q={keyword if keyword else '최신뉴스'}&tbm=nws"

# 4. 크롤링 실행
headers = {"User-Agent": "Mozilla/5.0"}
res = requests.get(search_url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

news_list = []
# 구글 뉴스 제목 추출 (구조는 바뀔 수 있으므로 주기적 체크 필요)
for g in soup.select('div.SoS9be'): 
    title = g.select_one('div.n0uTEe').text
    # 퀴즈 형식에 맞게 [제목]을 문제로, [검색어]를 정답으로 넣거나 자유롭게 구성 가능
    news_list.append([title, f"뉴스 키워드: {keyword if keyword else '전체'}"])

# 5. 시트에 데이터 추가 (최신 뉴스 5개만 예시로 추가)
if news_list:
    sheet.append_rows(news_list[:5])
    print(f"성공: {len(news_list[:5])}개의 뉴스를 시트에 추가했습니다.")
