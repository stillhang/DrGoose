import requests
import feedparser
import re
from datetime import datetime
import os

AI_KEYWORDS_EN = ['ai', 'llm', 'gpt', 'claude', 'anthropic', 'openai', 'gemini',
                  'machine learning', 'neural', 'deep learning', 'diffusion',
                  'transformer', 'inference', 'agent', 'rag']

AI_KEYWORDS_ZH = ['ai', '人工智能', '大模型', '语言模型', '机器学习', '深度学习',
                  'llm', 'gpt', 'claude', '智能体', '生成式', 'aigc', '算法',
                  '神经网络', '自动驾驶', 'agent', '多模态']

def fetch_hackernews_ai(limit=6):
    try:
        top_ids = requests.get(
            'https://hacker-news.firebaseio.com/v0/topstories.json', timeout=10
        ).json()[:100]
        stories = []
        for sid in top_ids:
            if len(stories) >= limit:
                break
            s = requests.get(
                f'https://hacker-news.firebaseio.com/v0/item/{sid}.json', timeout=5
            ).json()
            title = s.get('title', '').lower()
            if any(kw in title for kw in AI_KEYWORDS_EN):
                stories.append({
                    'title': s.get('title'),
                    'url': s.get('url') or f'https://news.ycombinator.com/item?id={sid}',
                    'score': s.get('score', 0),
                    'comments': s.get('descendants', 0),
                })
        return stories
    except Exception as e:
        print(f'HN fetch error: {e}')
        return []

def fetch_feed(url, limit=5):
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:limit]:
            results.append({
                'title': entry.get('title', '').strip(),
                'url': entry.get('link', ''),
            })
        return results
    except Exception as e:
        print(f'Feed fetch error ({url}): {e}')
        return []

def fetch_cn_ai(limit=6):
    """从少数派和爱范儿抓取 AI 相关中文文章"""
    sources = [
        ('少数派', 'https://sspai.com/feed'),
        ('爱范儿', 'https://www.ifanr.com/feed'),
    ]
    results = []
    for source_name, url in sources:
        if len(results) >= limit:
            break
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if len(results) >= limit:
                    break
                title = entry.get('title', '').lower()
                if any(kw in title for kw in AI_KEYWORDS_ZH):
                    results.append({
                        'title': entry.get('title', '').strip(),
                        'url': entry.get('link', ''),
                        'source': source_name,
                    })
        except Exception as e:
            print(f'CN feed error ({source_name}): {e}')
    return results

def fetch_arxiv_ai(limit=4):
    try:
        feed = feedparser.parse('https://export.arxiv.org/rss/cs.AI')
        papers = []
        for entry in feed.entries[:limit]:
            summary = entry.get('summary', '')
            summary = re.sub(r'<[^>]+>', '', summary)
            summary = summary[:150].strip() + '...'
            papers.append({
                'title': entry.get('title', '').strip(),
                'url': entry.get('link', ''),
                'summary': summary,
            })
        return papers
    except Exception as e:
        print(f'arXiv fetch error: {e}')
        return []

def build_post(date_str, date_full, hn, verge, cn, arxiv):
    def section(title, items, with_summary=False, show_source=False):
        if not items:
            return f'\n## {title}\n\n> 今日暂无内容\n'
        lines = [f'\n## {title}\n']
        for item in items:
            line = f'- [{item["title"]}]({item["url"]})'
            if 'score' in item:
                line += f' · ⭐{item["score"]} 💬{item["comments"]}'
            if show_source and item.get('source'):
                line += f' `{item["source"]}`'
            lines.append(line)
            if with_summary and item.get('summary'):
                lines.append(f'  > {item["summary"]}')
        return '\n'.join(lines) + '\n'

    cover = "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=1200&auto=format&fit=crop"

    return f"""---
title: "AI 动态日报 · {date_str}"
date: {date_full}
lastmod: {date_full}
author: liaoshihang
cover: {cover}
categories:
  - AI 动态
tags:
  - AI
  - 日报
draft: false
---

每日 AI 资讯自动汇总。

<!--more-->

## 🇨🇳 中文社区
{section('中文 AI 资讯', cn, show_source=True).strip()}

---
{section('Hacker News · AI 热议', hn)}
{section('The Verge · AI 新闻', verge)}
{section('arXiv · 最新论文', arxiv, with_summary=True)}
---

*由 GitHub Actions 自动生成 · {date_str}*
"""

def send_discord(webhook_url, date_str, total, cn_count, site_url):
    try:
        requests.post(webhook_url, json={
            'embeds': [{
                'title': f'📰 AI 日报 {date_str} 已发布',
                'description': f'共收录 **{total}** 条资讯，其中中文 **{cn_count}** 条',
                'url': f'{site_url}/posts/ai-news-{date_str}/',
                'color': 0x5865F2,
                'footer': {'text': 'DrGoose · 自动采集'}
            }]
        }, timeout=10)
    except Exception as e:
        print(f'Discord notify error: {e}')

if __name__ == '__main__':
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    date_full = now.strftime('%Y-%m-%dT09:00:00+08:00')

    print('Fetching HN...')
    hn = fetch_hackernews_ai()
    print(f'  {len(hn)} stories')

    print('Fetching The Verge...')
    verge = fetch_feed('https://www.theverge.com/rss/ai-artificial-intelligence/index.xml')
    print(f'  {len(verge)} articles')

    print('Fetching Chinese AI news...')
    cn = fetch_cn_ai()
    print(f'  {len(cn)} articles')

    print('Fetching arXiv...')
    arxiv = fetch_arxiv_ai()
    print(f'  {len(arxiv)} papers')

    content = build_post(date_str, date_full, hn, verge, cn, arxiv)

    os.makedirs('content/posts', exist_ok=True)
    filepath = f'content/posts/ai-news-{date_str}.md'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Written: {filepath}')

    total = len(hn) + len(verge) + len(cn) + len(arxiv)
    webhook = os.environ.get('DISCORD_WEBHOOK')
    site = os.environ.get('SITE_URL', 'https://liaoshihang.com')
    if webhook:
        send_discord(webhook, date_str, total, len(cn), site)
        print('Discord notified.')
    else:
        print('No DISCORD_WEBHOOK set, skipping notification.')
