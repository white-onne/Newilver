import time
from google import genai
from .news_fetcher import fetch_techcrunch, fetch_hackernews


def summarize_articles(articles, source_name):
    articles_text = "\n\n".join([
        f"제목: {article['title']}\n링크: {article['link']}\n요약: {article.get('summary', 'N/A')}"
        for article in articles
    ])

    prompt = f"""다음은 {source_name}의 최신 기술 뉴스입니다.

{articles_text}

위 기사들을 다음 형식으로 요약해주세요:

1. 오늘의 주요 트렌드 (2-3줄)
2. 각 기사별 핵심 요약 (기사당 1-2줄, 제목과 함께)
[기사 제목]
핵심 요약 내용
기사 링크
3. 주목할 만한 기술/회사 키워드

추가적으로
- 형식은 HTML 형식
- 간결하고 읽기 쉽게 작성
- 모든 글씨 색은 검정색
- 오늘의 주요 트렌드 내용의 폰트 크기는 10, 일반 글씨체
- 기사 제목 폰트 크기는 13, 굵은 글씨체, 글머리 기호 없음
- 핵심 요약 내용의 폰트 크기는 10, 글머리 기호 없음, 일반 글씨체
- 기사 링크 폰트 크기는 10, 그리고 주소를 그대로 작성해줘, 글머리 기호 없음, 일반 글씨체
- 다 영어로 작성
"""

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )

    return response.text


if __name__ == "__main__":

    tc_articles = fetch_techcrunch(5)
    hn_articles = fetch_hackernews(5)

    print("=== AI Summary of Tech crunch ===")
    tc_summary = summarize_articles(tc_articles, "TechCrunch")
    print(tc_summary)

    time.sleep(5)

    print("\n\n=== AI Summary of Hacker News===")
    hn_summary = summarize_articles(hn_articles, "Hacker News")
    print(hn_summary)