import os
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. Fetch securely from a WordPress-based Odia news feed (highly reliable)
rss_url = "https://odishareporter.in/feed/" 
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

print(f"Fetching news from {rss_url}...")
try:
    response = requests.get(rss_url, headers=headers, timeout=10)
    print(f"Server Status Code: {response.status_code} (200 means Success!)")
    feed = feedparser.parse(response.content)
except Exception as e:
    print(f"Failed to connect to the server: {e}")
    exit()

# 2. Safety check
if len(feed.entries) == 0:
    print("Error: No articles found! The feed might be empty or blocked.")
    exit()

latest_article = feed.entries[0]

# 3. Extract the Title
article_title = latest_article.title.replace('"', "'") 

# 4. Extract Original Text 
raw_summary = latest_article.summary
soup = BeautifulSoup(raw_summary, "html.parser")
original_text = soup.get_text(strip=True)

# 5. REWRITE WITH OLLAMA (LOCAL AI)
print("Sending text to local Ollama (llama3) for rewriting...")
ollama_url = "http://localhost:11434/api/generate"

ai_prompt = f"Rewrite the following Odia news summary in a professional journalistic tone in Odia. Do not add any English words. Output ONLY the rewritten Odia text, no introductions or explanations:\n\n{original_text}"

try:
    ollama_response = requests.post(ollama_url, json={
        "model": "llama3", 
        "prompt": ai_prompt,
        "stream": False
    })
    article_text = ollama_response.json()['response'].strip()
    print("Successfully rewritten by AI!")
except Exception as e:
    print(f"Ollama connection failed, falling back to original text. Error: {e}")
    article_text = original_text

# 6. Extract the Image
image_url = "https://via.placeholder.com/800x400.png?text=Odia+News"
if 'media_content' in latest_article:
    image_url = latest_article.media_content[0]['url']
elif 'links' in latest_article:
    for link in latest_article.links:
        if link.get('type', '').startswith('image/'):
            image_url = link.href

# 7. Format and Save
today_date = datetime.now().strftime('%Y-%m-%d')
time_str = datetime.now().strftime('%H-%M')
filename = f"_posts/{today_date}-{time_str}-news.md"

markdown_content = f"""---
layout: post
title: "{article_title}"
date: {today_date}
image: {image_url}
---

![Header Image]({image_url})

{article_text}
"""

with open(filename, 'w', encoding='utf-8') as file:
    file.write(markdown_content)

print(f"Successfully created {filename}")

# 8. Push to GitHub
os.system('git add .')
os.system('git commit -m "Auto-published AI rewritten article"')
os.system('git push origin main')

