Xscrape.ipynb은 데이터 수집을 위한 X 크롤링 
- 코드 내에 X 계정 ID/PASSWORD 입력 

언급분석.ipynb은 크롤링 된 데이터에 대한 긍/부정 정서 분석(날짜별, 주제별) 
- 언급분석.ipynb 내에서, 펜타포트와 관련 없는 언급을 GPT API를 통해 태깅하는 GPT_1.py, 언급된 주제를 GPT API를 통해 태깅하는 GPT_2.py 파일을 사용
- 이때 .txt 파일에 자신의 OPEN_AI_API_KEY를 입력 후 .env로 바꿔야 GPT_1.py, GPT_2.py에서 GPT api를 사용 가능