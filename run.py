import sys
import time
import logging
import os
from dotenv import load_dotenv

from main.news_fetcher import fetch_techcrunch, fetch_hackernews
from main.summarizer import summarize_articles
from main.email_sender import send_email

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_pipeline():
    load_dotenv()
    recipient = os.environ.get("GMAIL_ADDRESS")

    logger.info("📰 뉴스 수집 시작...")
    tc_articles = fetch_techcrunch(5)
    hn_articles = fetch_hackernews(5)
    logger.info(f"✅ TechCrunch: {len(tc_articles)}건, Hacker News: {len(hn_articles)}건")

    logger.info("🤖 AI 요약 중...")
    tc_summary_text = summarize_articles(tc_articles, "TechCrunch")
    time.sleep(5)
    hn_summary_text = summarize_articles(hn_articles, "Hacker News")

    email_articles = [{
        'source': '📊 Today\'s Trends',
        'title': 'Key AI-Analyzed Trends',
        'url': '#',
        'summary': f"{tc_summary_text}\n\n{hn_summary_text}"
    }]

    logger.info("📧 이메일 발송 중...")
    send_email(email_articles, recipient)
    logger.info("🎉 완료!")


def main():
    for attempt in range(2):  # 최초 1회 + 재시도 1회
        try:
            run_pipeline()
            sys.exit(0)
        except Exception as e:
            logger.error(f"시도 {attempt + 1} 실패: {e}")
            if attempt == 0:
                logger.info("30초 후 재시도...")
                time.sleep(30)
            else:
                logger.error("최종 실패. 종료합니다.")
                sys.exit(1)


if __name__ == "__main__":
    main()