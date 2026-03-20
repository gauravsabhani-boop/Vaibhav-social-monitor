#!/usr/bin/env python3
"""
Vaibhav Social Media Monitor
Searches and emails social media updates
"""

import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from groq import Groq
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
PERSON_NAME = "Vaibhav Sisinity"
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "gaurav.sabhani@lenskart.com")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

def search_google(query):
    """
    Search Google for a query
    """
    print(f"🔍 Searching Google: {query}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        url = f"https://www.google.com/search?q={query}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            for item in soup.find_all('a', href=True)[:5]:
                title = item.get_text()
                link = item['href']
                
                if len(title) > 10 and 'http' in link:
                    results.append({
                        'title': title[:100],
                        'url': link,
                        'source': 'Google'
                    })
            
            print(f"   ✅ Found {len(results)} results")
            return results
    
    except Exception as e:
        print(f"   ⚠️ Error: {str(e)[:50]}")
    
    return []

def search_linkedin():
    """Search LinkedIn for Vaibhav"""
    print(f"🔗 Searching LinkedIn")
    
    query = f"site:linkedin.com {PERSON_NAME}"
    results = search_google(query)
    linkedin_results = [r for r in results if 'linkedin.com' in r['url']]
    
    print(f"   ✅ Found {len(linkedin_results)} LinkedIn results")
    return linkedin_results

def search_twitter():
    """Search Twitter for Vaibhav"""
    print(f"🐦 Searching Twitter")
    
    query = f"site:twitter.com {PERSON_NAME}"
    results = search_google(query)
    twitter_results = [r for r in results if 'twitter.com' in r['url']]
    
    print(f"   ✅ Found {len(twitter_results)} Twitter results")
    return twitter_results

def search_news():
    """Search news for Vaibhav"""
    print(f"📰 Searching News")
    
    query = f"{PERSON_NAME} news"
    results = search_google(query)
    
    print(f"   ✅ Found {len(results)} news results")
    return results

def summarize_with_groq(results):
    """
    Summarize search results using Groq AI
    """
    print("🤖 Summarizing with AI...")
    
    if not results:
        return "No content found for Vaibhav Sisinity today."
    
    try:
        content = "Search Results:\n\n"
        for i, result in enumerate(results[:10], 1):
            content += f"{i}. {result['title']}\n"
            content += f"   Source: {result['source']}\n\n"
        
        if not GROQ_API_KEY:
            print("   ⚠️ No API key, using fallback summary")
            return create_fallback_summary(results)
        
        client = Groq(api_key=GROQ_API_KEY)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""Summarize these search results about {PERSON_NAME} in 5-7 bullet points. Format as a bulleted list.

{content}"""
                }
            ],
            model="mixtral-8x7b-32768",
            max_tokens=500,
        )
        
        summary = chat_completion.choices[0].message.content
        print("   ✅ Summary created")
        return summary
    
    except Exception as e:
        print(f"   ⚠️ AI Error: {str(e)[:50]}")
        return create_fallback_summary(results)

def create_fallback_summary(results):
    """Create summary without AI"""
    summary = "📊 FINDINGS:\n\n"
    
    if results:
        for i, result in enumerate(results[:5], 1):
            summary += f"• {result['title']}\n"
            summary += f"  Source: {result['source']}\n"
    else:
        summary += "• No content found today\n"
    
    return summary

def send_email_summary(summary):
    """Send email with summary"""
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
    """Main function"""
    print(f"\n{'='*60}")
    print(f"🚀 Vaibhav Social Monitor")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"{'='*60}\n")
    
    all_results = []
    
    # Search all platforms
    print("📡 SEARCHING ALL PLATFORMS...\n")
    all_results.extend(search_google(f"{PERSON_NAME}"))
    all_results.extend(search_linkedin())
    all_results.extend(search_twitter())
    all_results.extend(search_news())
    
    print(f"\n📊 Total results found: {len(all_results)}\n")
    
    # Summarize
    summary = summarize_with_groq(all_results)
    
    print("\n" + "="*60)
    print("📋 SUMMARY:")
    print("="*60)
    print(summary)
    print("="*60 + "\n")
    
    # Send email
    send_email_summary(summary)
    
    print("\n✅ Monitor cycle completed!\n")
    return summary

if __name__ == "__main__":
    main()
