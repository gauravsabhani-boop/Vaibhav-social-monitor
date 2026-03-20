#!/usr/bin/env python3
"""
Vaibhav Social Media Monitor - IMPROVED VERSION
Searches and emails social media updates with better extraction
"""

import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from groq import Groq
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import re

# Configuration
PERSON_NAME = "Vaibhav Sisinity"
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "gaurav.sabhani@lenskart.com")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

def extract_text_from_html(html_content):
    """Extract readable text from HTML"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text[:500]  # First 500 chars
    except:
        return ""

def search_duckduckgo(query):
    """
    Search using DuckDuckGo (better for finding LinkedIn/Twitter posts)
    """
    print(f"🔍 Searching DuckDuckGo: {query}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # DuckDuckGo search
        url = f"https://duckduckgo.com/html/?q={query}"
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Find search results
            for result in soup.find_all('div', class_='result'):
                try:
                    title_elem = result.find('a', class_='result__a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    url_text = title_elem.get('href', '')
                    
                    # Get snippet
                    snippet_elem = result.find('a', class_='result__snippet')
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                    
                    if len(title) > 10:
                        results.append({
                            'title': title[:100],
                            'url': url_text,
                            'snippet': snippet[:200],
                            'source': 'Web'
                        })
                except:
                    continue
            
            print(f"   ✅ Found {len(results)} results")
            return results[:5]
    
    except Exception as e:
        print(f"   ⚠️ DuckDuckGo Error: {str(e)[:50]}")
    
    return []

def search_google_advanced(query):
    """
    Advanced Google search with better parsing
    """
    print(f"🔍 Searching Google: {query}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        url = f"https://www.google.com/search?q={query}&num=10"
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Find all divs with class 'g' (Google result containers)
            for g in soup.find_all('div', class_='g'):
                try:
                    # Get title
                    title_elem = g.find('h3')
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()
                    
                    # Get URL
                    link_elem = g.find('a')
                    if not link_elem:
                        continue
                    url = link_elem.get('href', '')
                    
                    # Get snippet
                    snippet_elem = g.find('div', class_='VwiC3b')
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""
                    
                    if len(title) > 10 and 'http' in url:
                        results.append({
                            'title': title[:100],
                            'url': url,
                            'snippet': snippet[:200],
                            'source': 'Google'
                        })
                except:
                    continue
            
            print(f"   ✅ Found {len(results)} results")
            return results[:5]
    
    except Exception as e:
        print(f"   ⚠️ Google Error: {str(e)[:50]}")
    
    return []

def search_linkedin_posts():
    """
    Search for LinkedIn posts about Vaibhav
    """
    print(f"🔗 Searching LinkedIn Posts")
    
    results = []
    
    # Search 1: Direct LinkedIn profile search
    query1 = f"site:linkedin.com {PERSON_NAME} posts activity recent"
    results.extend(search_duckduckgo(query1))
    
    # Search 2: LinkedIn company updates
    query2 = f"site:linkedin.com/posts {PERSON_NAME}"
    results.extend(search_google_advanced(query2))
    
    # Search 3: LinkedIn activity feed
    query3 = f"site:linkedin.com {PERSON_NAME} posted shared updated"
    results.extend(search_duckduckgo(query3))
    
    # Filter to LinkedIn only
    linkedin_results = [r for r in results if 'linkedin.com' in r['url'].lower()]
    linkedin_results = linkedin_results[:5]  # Top 5
    
    print(f"   ✅ Found {len(linkedin_results)} LinkedIn results")
    return linkedin_results

def search_twitter_posts():
    """
    Search for Twitter posts about Vaibhav
    """
    print(f"🐦 Searching Twitter Posts")
    
    results = []
    
    # Search 1: Twitter posts
    query1 = f"site:twitter.com {PERSON_NAME} posted tweet"
    results.extend(search_duckduckgo(query1))
    
    # Search 2: X (new Twitter) posts
    query2 = f"site:x.com {PERSON_NAME}"
    results.extend(search_google_advanced(query2))
    
    # Search 3: Twitter mentions
    query3 = f"{PERSON_NAME} twitter"
    results.extend(search_duckduckgo(query3))
    
    # Filter to Twitter/X only
    twitter_results = [r for r in results if any(domain in r['url'].lower() for domain in ['twitter.com', 'x.com', 't.co'])]
    twitter_results = twitter_results[:5]  # Top 5
    
    print(f"   ✅ Found {len(twitter_results)} Twitter results")
    return twitter_results

def search_news():
    """
    Search for news about Vaibhav
    """
    print(f"📰 Searching News")
    
    results = []
    
    # Search 1: General news
    query1 = f"{PERSON_NAME} news update"
    results.extend(search_google_advanced(query1))
    
    # Search 2: Recent news
    query2 = f"{PERSON_NAME} 2024 2025"
    results.extend(search_duckduckgo(query2))
    
    # Search 3: Press releases
    query3 = f"{PERSON_NAME} announcement"
    results.extend(search_duckduckgo(query3))
    
    news_results = results[:5]
    
    print(f"   ✅ Found {len(news_results)} news results")
    return news_results

def search_general_web():
    """
    General web search
    """
    print(f"🌐 Searching Web")
    
    results = []
    
    # Search 1: Simple name search
    query1 = f"{PERSON_NAME}"
    results.extend(search_google_advanced(query1))
    
    # Search 2: Name with recent
    query2 = f"{PERSON_NAME} recent 2025"
    results.extend(search_duckduckgo(query2))
    
    web_results = results[:5]
    
    print(f"   ✅ Found {len(web_results)} web results")
    return web_results

def summarize_with_groq(all_results):
    """
    Summarize search results using Groq AI
    """
    print("🤖 Summarizing with AI...")
    
    if not all_results:
        return "No content found for Vaibhav Sisinity today."
    
    try:
        # Format results for AI
        content = f"Found {len(all_results)} relevant results about {PERSON_NAME}:\n\n"
        
        for i, result in enumerate(all_results[:15], 1):
            content += f"{i}. {result.get('title', 'No title')}\n"
            if result.get('snippet'):
                content += f"   Summary: {result['snippet']}\n"
            content += f"   Source: {result.get('source', 'Unknown')}\n"
            if result.get('url'):
                content += f"   URL: {result['url']}\n"
            content += "\n"
        
        if not GROQ_API_KEY:
            print("   ⚠️ No API key, using fallback summary")
            return create_fallback_summary(all_results)
        
        client = Groq(api_key=GROQ_API_KEY)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""Summarize these search results about {PERSON_NAME} in 8-12 bullet points. 
Be specific and factual. Include what was posted/mentioned and where.
Format as a bulleted list with key information.

{content}"""
                }
            ],
            model="mixtral-8x7b-32768",
            max_tokens=800,
        )
        
        summary = chat_completion.choices[0].message.content
        print("   ✅ Summary created")
        return summary
    
    except Exception as e:
        print(f"   ⚠️ AI Error: {str(e)[:50]}")
        return create_fallback_summary(all_results)

def create_fallback_summary(results):
    """
    Create summary without AI
    """
    if not results:
        return "No content found for Vaibhav Sisinity today."
    
    summary = f"📊 FOUND {len(results)} RESULTS:\n\n"
    
    for i, result in enumerate(results[:10], 1):
        summary += f"• {result.get('title', 'No title')}\n"
        if result.get('snippet'):
            summary += f"  - {result['snippet'][:150]}\n"
        summary += f"  📍 Source: {result.get('source', 'Unknown')}\n\n"
    
    return summary

def send_email_summary(summary):
    """
    Send email with summary
    """
    print("📧 Sending email...")
    
    try:
        if not all([GMAIL_USER, GMAIL_PASSWORD, RECIPIENT_EMAIL]):
            print("   ❌ Missing email credentials")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"📱 {PERSON_NAME} - Daily Social Media Summary"
        
        body = f"""
Good morning!

Here's today's summary of {PERSON_NAME}'s social media presence and web mentions:

{summary}

---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}
Vaibhav Social Monitor - 100% Automated
Checked: LinkedIn, Twitter, News, and General Web
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print("   ✅ Email sent successfully!")
        return True
    
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False

def main():
    """
    Main function
    """
    print(f"\n{'='*70}")
    print(f"🚀 Vaibhav Social Media Monitor - IMPROVED")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"{'='*70}\n")
    
    all_results = []
    
    # Search all platforms with improved methods
    print("📡 SEARCHING ALL PLATFORMS...\n")
    
    all_results.extend(search_linkedin_posts())
    all_results.extend(search_twitter_posts())
    all_results.extend(search_news())
    all_results.extend(search_general_web())
    
    # Remove duplicates
    unique_results = []
    seen_urls = set()
    for result in all_results:
        url = result.get('url', '')
        if url not in seen_urls:
            unique_results.append(result)
            seen_urls.add(url)
    
    print(f"\n📊 Total unique results found: {len(unique_results)}\n")
    
    # Summarize
    summary = summarize_with_groq(unique_results)
    
    print("\n" + "="*70)
    print("📋 SUMMARY:")
    print("="*70)
    print(summary)
    print("="*70 + "\n")
    
    # Send email
    send_email_summary(summary)
    
    print("\n✅ Monitor cycle completed!\n")
    return summary

if __name__ == "__main__":
    main()
