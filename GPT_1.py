import os
import re
import asyncio
import pandas as pd
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv('.env')
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
instructions = """
Given a tweet in Korean, determine if it is related to the PentaPort Rock Festival held in Incheon, South Korea.

If related: 
    Summarize the content clearly and concisely, preserving the original tone, emotion, and key keywords.
    It must be 1~2 sentence.
    Do not explain or paraphrase the tweet; maintain its original style.
    The response must be in clear and natural Korean.

If not related:
    Do not summarize the content, just put "not related" at the end.
    Unrelated tweets often contain gaming terms "펜타킬" or discuss esports players(ex. Gumayusi, Ruler etc.) and events (especially T1, e-sorts team).
        etc. "구마유시 왜 펜타 뺏음ㅡㅡ". "나는 펜타 언제 해보지", "현준이 맨날 펜타 뺏네", "민형아 다음엔 할 수 있을 거야" 
    Or it is related with "card" game like "펜타클 카드".
    If you can find it is related to esports or card game, put the category with "not related" tag. Like not related: esports

Related Tweets Criteria
A tweet is considered related if it:
    Explicitly mentions "펜타포트" or "펜타".
    Implicitly refers to the festival by mentioning one of the artists from this year's lineup:
    It is usally about: plan to enjoy, 준비물, 교통, 대기줄, 운영, 출연진, 식음료, 음향, 아티스트 etc.
    If the tweet seems not related to gaming/esports or card game, apply loose criteria. I.E) If you cannot find the tag for not-related, do not put the not-related.

Plus, the artist's name who features on the festival is masked as {출연진}. So if {출연진} is in the tweet, it is related.    

Input & Output Format
Example Input:
1. 와 오늘 펜타 가는데 날씨 진짜 미쳤다
2. 롤에서 펜타킬 했다ㅋㅋ
3. {출연진} 무대 진짜 개찢었다 펜타는 대체 이 사람들을 어케 부른거임?
4. 펜타 줄 ㅈㄴ기네 하
5. {출연진} 무대 보고 싶어서 펜타 갈까 말까 고민 중
6. 이번 펜타 S급: {출연진}     A급: {출연진}    B급: {출연진}
7. 펜타클 카드 성능 왜이러냐 진짜 

Expected Output:
1. 오늘 가는데 날씨가 너무 덥다
2. 롤에서 펜타킬 했다ㅋㅋ - not related: e-sports
3. {출연진} 무대가 진짜 대박이었다. 대체 어떻게 이런 사람들을 불렀을까
4. 대기줄이 너무 길다
5. {출연진} 무대를 보러 갈지 말지 고민 중
6. 이번에 S급은 {출연진}, A급은 {출연진}, B급은 {출연진}였다.
7. 펜타클 카드 성능 왜이러냐 진짜 - not related: card game
"""

def remove_leading_numbers(text: str) -> str:
    txt = re.sub(r'^\d+\s*\d*\.\s*', '', text)
    txt = re.sub(r'^\d+\s*', '', txt)
    return txt

async def process_row(i, row, sem):
    txt = f"{i}. {row['masked']}"
    async with sem:  # 동시 실행 개수 제한
        response = await client.responses.create(
            model="gpt-4o-mini",
            instructions=instructions,
            input=txt
        )
    return i, remove_leading_numbers(response.output_text)

async def main(df, max_concurrency=5):
    sem = asyncio.Semaphore(max_concurrency)
    tasks = [process_row(i, row, sem) for i, row in df.iterrows()]
    results = await asyncio.gather(*tasks)
    results = sorted(results, key=lambda x: x[0])  # 인덱스 순서 보장
    df['processed'] = [r[1] for r in results]
    df.to_csv('processed.csv', index=False)
    
df = pd.read_csv('masked.csv', index_col=0)
asyncio.run(main(df, max_concurrency=5))