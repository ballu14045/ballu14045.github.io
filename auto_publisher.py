import os
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. Fetch securely
rss_url = "https://odishareporter.in/feed/" 
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

print(f"Fetching news from {rss_url}...")
try:
    response = requests.get(rss_url, headers=headers, timeout=10)
    feed = feedparser.parse(response.content)
except Exception as e:
    print(f"Failed to connect to the server: {e}")
    exit()

if len(feed.entries) == 0:
    print("Error: No articles found!")
    exit()

latest_article = feed.entries[0]
article_url = latest_article.link

# 2. Extract Text 
article_title = latest_article.title.replace('"', "'") 
raw_summary = latest_article.summary
soup = BeautifulSoup(raw_summary, "html.parser")
original_text = soup.get_text(strip=True)

# 3. REWRITE WITH ANYTHINGLLM
print("Sending text to AnythingLLM for rewriting...")

# --- UPDATE THESE TWO VARIABLES ---
anythingllm_api_key = "6F7CF4M-3T5MSF6-N7SKQYY-SQV5A0G"
workspace_slug = "sata-katha-odia-news" 
# ----------------------------------

anythingllm_url = f"http://localhost:3001/api/v1/workspace/{workspace_slug}/chat"
api_headers = {
    "Authorization": f"Bearer {anythingllm_api_key}",
    "Content-Type": "application/json"
}

ai_prompt = f"Rewrite this news summary:\n\n{original_text}"

try:
    llm_response = requests.post(anythingllm_url, headers=api_headers, json={
        "message": ai_prompt,
        "mode": "chat" 
    })
    
    response_data = llm_response.json()
    
    # DEBUGGER: Check if AnythingLLM actually returned text
    if 'textResponse' in response_data and response_data['textResponse'] is not None:
        article_text = response_data['textResponse'].strip()
        print("Successfully rewritten by AnythingLLM!")
    else:
        print(f"AnythingLLM Error. Raw response: {response_data}")
        article_text = original_text
        
except Exception as e:
    print(f"AnythingLLM connection crashed: {e}")
    article_text = original_text

# 4. Extract the Image
image_url = "https://via.placeholder.com/800x400.png?text=Odia+News"
if 'media_content' in latest_article:
    image_url = latest_article.media_content[0]['url']
elif 'links' in latest_article:
    for link in latest_article.links:
        if link.get('type', '').startswith('image/'):
            image_url = link.href

# 5. Format and Save
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

# 6. Push to GitHub
os.system('git add .')
os.system('git commit -m "Auto-published AI rewritten article via AnythingLLM"')
os.system('git push origin main')

