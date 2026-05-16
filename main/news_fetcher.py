import feedparser
import requests
import time


def fetch_techcrunch(news_num: int = 1):
    feed = feedparser.parse('https://techcrunch.com/feed/')
    return [
        {
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': entry.summary,
        }
        for entry in feed.entries[:news_num]
    ]


def fetch_hackernews(news_num: int = 1):
    top_ids = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json').json()[:news_num]

    articles = []
    for story_id in top_ids:
        story = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json').json()
        if story.get('type') == 'story':
            articles.append({
                'title': story.get('title'),
                'link': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                'score': story.get('score'),
                'by': story.get('by'),
            })

    return articles


if __name__ == "__main__":
    print("=== TechCrunch Newest articles ===")
    start_time = time.time()
    tc_articles = fetch_techcrunch(5)
    for article in tc_articles:
        print(f"- {article['title']}")
        print(f"  {article['link']}\n")
    end_time = time.time()

    print(f"Execution time: {end_time - start_time:.4f}s")

    print("\n=== Hacker News Top Stories ===")
    start_time = time.time()
    hn_articles = fetch_hackernews(5)
    for article in hn_articles:
        print(f"- {article['title']}")
        print(f"  {article['link']}\n")

    end_time = time.time()

    print(f"Execution time: {end_time - start_time:.4f}s")