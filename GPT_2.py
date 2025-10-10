import os
import re
import asyncio
import pandas as pd
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv('.env')
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
instructions = """
You are an aspect-based multi-label extractor for tweets.  
All tweets are related to the **2025 PentaPort Rock Festival (펜타포트 락페스티벌; 펜타)**, held in Incheon from August 1–3, 2025.  

## Task  
- For each input tweet, identify and extract all relevant aspects.  
- A tweet may contain multiple aspects simultaneously.  
- Or it may not contain any aspect I define.
- Use the aspect categories and their representative keywords below as guidance. (Keywords are only examples, not exhaustive lists.)  
- For each aspect, output the following: "evidence_raw": 
   - Copy the exact substring from the input tweet that supports the aspect.

### Aspect Categories & Example Keywords
- '날씨': ['날씨', '더위']  
- '장소': ['부지', '인천', '송도']  
- '교통': ['1호선', '지하철', '셔틀', '꽃가마']  
- '운영': ['운영', '대기줄', '시큐리티', '경호', '요원', '검사']
- '티켓가격': ['티켓가격']
- '티켓팅': ['티켓팅', '예매', '블라인드', '인터파크', 'yes24']
- '인파': ['사람이 많다']  
- '화장실': ['러쉬', '화장실']  
- '관람문화': ['슬램', '락놀이', '구호', '깃발', '떼창']  
- '라인업': ['라인업', '시간표', '탐테', '{출연진}']  
- '음향': ['음향']  
- '아티스트': ['{출연진}', 아티스트의 이름]  
- 'F&B': ['음식', '음료', '맥주', '먹을 거', '김말국']  
- '굿즈': ['티셔츠', '슬로건']

## Output Format  
- Return results as a JSON object.  
- Keys = aspect category names.  
- Values = concise paraphrase or extracted span from the tweet that explains why the aspect applies.  

## Examples  

**Input Tweet**  
- "이번에 {출연진} 보러 펜타 갔는데 화장실이 너무 좋아서 놀람. 러쉬가 콜라보 했대..."  

**Output JSON**  
```json
{
  "아티스트": 이번에 {출연진} 보러 펜타 갔는데, 
  "화장실": 화장실이 너무 좋아서 놀람. 러쉬가 콜라보 했대...
}

**Input Tweet**  
- "{출연진} 보러 펜타간다! 넘 기대돼. 같이 가는 사람들 다들 조심히!"  

**Output JSON**  
```json
{
  "아티스트": {출연진} 보러 펜타간다! 넘 기대돼.
}

**Input Tweet**
- 다들 펜타 조심해서 다녀오세요

**Output JSON**  
```json
{"없음"}
"""

import asyncio
import pickle
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv('.env')

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# 동시 실행 제한
semaphore = asyncio.Semaphore(5)  # 동시에 5개만 실행

async def process_row(i, txt):
    async with semaphore:  # 동시에 실행 개수 제한
        try:
            response = await client.responses.create(
                model="gpt-4o-mini",
                instructions=instructions,
                input=txt
            )
            print(i)
            return (i, response.output_text)
        except Exception as e:
            # print(f"Error at {i}: {e}")
            return (i, None)

async def main(df_related):
    tasks = []
    for i, row in df_related.iterrows():
        txt = f"{row['masked']}"
        tasks.append(process_row(i, txt))

    results = await asyncio.gather(*tasks)

    with open('aspect_lst.pkl', 'wb') as f:
        pickle.dump(results, f)

if __name__ == "__main__":
    import pandas as pd
    
    df_related = pd.read_csv("related.csv")
    asyncio.run(main(df_related))
