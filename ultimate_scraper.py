"""
Ultimate Web Scraper - Universal Edition
Universal Job Market & Healthcare Directory Scraper
"""

import streamlit as st
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Tag
import pandas as pd
import sys
import re
import json
import time
from urllib.parse import urljoin, unquote
from typing import Dict, Any, List, Optional
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Universal Job Scraper", 
    page_icon="🕸️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# --- CUSTOM CSS (PROFESSIONAL THEME) ---
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        min-height: 100vh;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5em;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        padding-bottom: 0;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1em;
        margin-top: 10px;
    }

    /* Button styling - FULL WIDTH */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        height: 60px;
        width: 100%; /* Full Width */
        font-size: 18px;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        margin-top: 10px;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }

    /* Input styling - FULL WIDTH */
    .stTextInput > div > div > input {
        border-radius: 12px;
        padding: 15px;
        font-size: 16px;
    }

    /* Metric styling */
    .stMetric {
        background: linear-gradient(13deg, #000000 0%, #6f51a4 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }

    /* Status box styling */
    .status-box {
        background: rgba(255, 255, 255, 0.1);
        border-left: 5px solid #667eea;
        padding: 15px;
        border-radius: 5px;
        color: white;
        margin-bottom: 10px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h1, h2, h3 {
        color: white !important;
    }
    section[data-testid="stSidebar"] label {
        color: #e0e0e0 !important;
        font-weight: 600;
    }

    /* Capabilities Badge Styling */
    .cap-badge {
        display: inline-block;
        padding: 5px 10px;
        margin: 3px;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgb(255 255 255);
        color: white;
        font-size: 0.85em;
        width: 95%;
    }
    
    /* Footer styling */
    .footer {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: 50px;
        box-shadow: 0 -5px 30px rgba(102, 126, 234, 0.3);
    }
    .footer p {
        color: white;
        margin: 0;
        font-weight: 500;
        font-size: 1em;
    }
    .footer .heart {
        color: #ff6b6b;
        font-size: 1.2em;
    }
    .footer a {
        color: white !important;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)


# ==================== HELPERS ====================

class StringUtils:
    @staticmethod
    def clean(text: str) -> str:
        if not text: return ""
        text = re.sub(r'\s+', ' ', text).strip()
        return text

class PaginationManager:
    @staticmethod
    def get_url_for_page(base_url: str, page_num: int) -> str:
        # Handle MIIG (tx_solr[page])
        pattern_solr = r'(tx_solr(?:%5B|\[)page(?:%5D|\])=)(\d+)'
        if re.search(pattern_solr, base_url):
            return re.sub(pattern_solr, f'\\g<1>{page_num}', base_url)
        
        # Handle Altenpflege (page=X)
        pattern_std = r'(page=)(\d+)'
        if re.search(pattern_std, base_url):
            return re.sub(pattern_std, f'page={page_num}', base_url)
        
        # Fallback: Append parameter
        separator = '&' if '?' in base_url else '?'
        if "make-it-in-germany" in base_url:
            return f"{base_url}{separator}tx_solr%5Bpage%5D={page_num}"
        else:
            return f"{base_url}{separator}page={page_num}"

# ==================== SITE EXTRACTORS ====================

class MakeItGermanyExtractor:
    """Logic for MIIG (Deep Scraping)"""
    
    @staticmethod
    async def extract_list(page, base_url):
        # Finds URLs to detail pages
        try:
            await page.wait_for_selector("text=Details ansehen", timeout=10000)
        except:
            return []
            
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        
        detail_buttons = soup.find_all(string=re.compile(r'Details ansehen'))
        for btn in detail_buttons:
            link = btn.find_parent('a')
            if link and link.get('href'):
                links.append(urljoin(base_url, link.get('href')))
        return links

    @staticmethod
    async def extract_details(page, url):
        # Deep scrapes the specific details
        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            data = {'source_url': url}

            overview = soup.find('article', class_='detail-page__overview')
            if overview:
                h1 = overview.find('h1', class_='h3')
                if h1: data['company_name'] = StringUtils.clean(h1.get_text()) # Using standardized key

                # Sometimes company is in subheader
                company_tag = overview.find('a', class_='head__children')
                if company_tag: 
                    # If h1 was job title, this is company
                    data['job_title'] = data.get('company_name') 
                    data['company_name'] = StringUtils.clean(company_tag.get_text())

                ul = overview.find('ul', class_='il')
                if ul:
                    for li in ul.find_all('li'):
                        text = li.get_text(" ", strip=True)
                        if "Arbeitsort" in text: data['address'] = text.replace("Arbeitsort:", "").strip()

            additional = soup.find('div', class_='additional__text')
            if additional:
                # Email
                for a in additional.find_all('a', href=re.compile(r'mailto:', re.I)):
                    email = unquote(a['href']).replace('mailto:', '').split('?')[0]
                    if '@' in email: data['email'] = email; break
                
                # Phone
                for a in additional.find_all('a', href=re.compile(r'tel:')):
                    data['phone'] = unquote(a['href']).replace('tel:', '').strip(); break
                
                # Web
                web = additional.find('a', href=re.compile(r'http'), target='_blank')
                if web: data['website'] = web['href']

            return data
        except Exception as e:
            return {}

class AltenpflegeExtractor:
    """Logic for AP Website (JS Obfuscated List)"""
    
    @staticmethod
    async def extract_list(page, base_url):
        # For this site, we scrape data directly from the list page because
        # the contact info is present (though obfuscated by JS)
        try:
            # Wait for the H2 headers to appear (indicating content loaded)
            await page.wait_for_selector("h2.has-text-weight-bold", timeout=15000)
            # Wait a bit for the JS 'eval' scripts to run and populate mailto/tel links
            await page.wait_for_timeout(2000)
        except:
            return []

        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        results = []
        
        # Strategy: Iterate through the H2s (Company Names) and look at siblings
        # Structure: H2 -> div.columns (Address) -> div (Contacts) -> div (Description)
        
        headers = soup.find_all("h2", class_="has-text-weight-bold")
        
        for h2 in headers:
            try:
                item = {}
                item['company_name'] = StringUtils.clean(h2.get_text())
                item['source_url'] = base_url
                
                # 1. Address (Next Sibling: div.columns)
                address_div = h2.find_next_sibling("div", class_="columns")
                if address_div:
                    addr_parts = [StringUtils.clean(s.get_text()) for s in address_div.find_all("span", class_="show-unscaled")]
                    item['address'] = ", ".join(filter(None, addr_parts))
                
                # 2. Contacts (Next Sibling of Address: div with icons)
                # Since JS ran, the 'eval' code should have been replaced by real <a> tags
                contact_div = address_div.find_next_sibling("div") if address_div else None
                
                if contact_div:
                    # Phone
                    phone_link = contact_div.find("a", href=re.compile(r'^tel:'))
                    if phone_link:
                        item['phone'] = StringUtils.clean(phone_link.get_text())
                    
                    # Email
                    email_link = contact_div.find("a", href=re.compile(r'^mailto:'))
                    if email_link:
                        item['email'] = unquote(email_link['href'].replace('mailto:', '')).strip()
                        
                    # Website
                    web_link = contact_div.find("a", href=re.compile(r'^http'), class_="icon")
                    if web_link:
                        item['website'] = web_link['href']

                # 3. Description (Usually text following the contacts)
                # Look for the container text or the next paragraph
                if contact_div:
                    desc_text = contact_div.get_text(" ", strip=True)
                    # Often the description is appended or in the next block. 
                    # In the screenshot, "Rechtsberatung..." is below the icons.
                    # We try to grab the parent's full text and subtract what we found, or look for next sibling.
                    next_div = contact_div.find_next_sibling("div")
                    if next_div:
                        item['description'] = StringUtils.clean(next_div.get_text())[:300] + "..."

                results.append(item)
            except Exception as e:
                continue
                
        return results # Returns LIST of data dicts, not URLs

# ==================== MAIN ENGINE ====================

async def run_scraper(start_url, num_pages, headless, wait_time, status_box, progress_bar):
    all_results = []
    
    # DETERMINE MODE
    is_make_it = "make-it-in-germany" in start_url
    is_altenpflege = "altenpflege.de" in start_url
    
    if not (is_make_it or is_altenpflege):
        status_box.error("⚠️ Unknown website.")
        return []

    async with async_playwright() as p:
        status_box.info("🚀 Launching browser engine...")
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        for current_page in range(1, num_pages + 1):
            target_url = PaginationManager.get_url_for_page(start_url, current_page)
            status_box.markdown(f'<div class="status-box">📄 Scanning Page {current_page}/{num_pages}...</div>', unsafe_allow_html=True)
            
            try:
                await page.goto(target_url, timeout=45000)
                
                # Polite wait
                if current_page > 1: await asyncio.sleep(wait_time)

                if is_altenpflege:
                    # Altenpflege: Extract data directly from list (JS decoded)
                    page_data = await AltenpflegeExtractor.extract_list(page, target_url)
                    all_results.extend(page_data)
                    progress_bar.progress(current_page / num_pages)
                    
                    if not page_data:
                        status_box.warning(f"No results on page {current_page}.")
                        break
                        
                elif is_make_it:
                    # Make-it: Extract Links then Deep Scrape
                    links = await MakeItGermanyExtractor.extract_list(page, target_url)
                    
                    if not links:
                        status_box.warning(f"No links found on page {current_page}.")
                        break
                        
                    # Deep Scrape Loop
                    deep_page = await context.new_page()
                    # Block images for speed
                    await deep_page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font"] else route.continue_())
                    
                    for i, link in enumerate(links):
                        status_box.markdown(f'<div class="status-box">🔍 Deep Scraping: {i+1}/{len(links)} on Page {current_page}</div>', unsafe_allow_html=True)
                        data = await MakeItGermanyExtractor.extract_details(deep_page, link)
                        if data: all_results.append(data)
                        if wait_time > 0: await asyncio.sleep(wait_time * 0.5)
                    
                    await deep_page.close()
                    progress_bar.progress(current_page / num_pages)

            except Exception as e:
                status_box.error(f"❌ Error on page {current_page}: {e}")
                continue

        await browser.close()
    
    return all_results

# ==================== UI ====================

def main():
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌐 Ultimate Universal Web Scraper</h1>
        <p>Universal Job Market & Healthcare Directory Scraper</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("### ⚙️ Control Center")
        st.markdown("---")
        
        st.markdown("#### 📄 Pagination")
        num_pages = st.number_input("Pages to Scan", 1, 50, 2)
        
        st.markdown("#### ⏱️ Performance")
        wait_time = st.slider("Wait Time (sec)", 0.5, 10.0, 2.0, 0.5)
        
        st.markdown("#### 🔧 System")
        headless = st.checkbox("Headless Mode", value=True)
        
        st.markdown("---")
        st.markdown("### 📊 Capabilities")
        # Custom Badge Design for Capabilities
        st.markdown("""
        <div>
            <span class="cap-badge">💡 Smart Pagination </span>
            <span class="cap-badge">✨ Multi-Site Support</span>
            <span class="cap-badge">🔗 Deep Scraping</span>
            <span class="cap-badge">📧 Email Decoding</span>
            <span class="cap-badge">📱 Phone Extraction</span>
            <span class="cap-badge">🗺️ German Address Parsing </span>
        </div>
        """, unsafe_allow_html=True)
    
    # --- MAIN INPUT (FULL WIDTH) ---
    url_input = st.text_input(
        "🔗 Enter Website URL",
        value="",
        placeholder="https://www.example.com?page=1"
    )
    
    start_button = st.button("🚀 Start Scraping", use_container_width=True)
    
    # Status
    status_box = st.empty()
    progress_bar = st.empty()
    
    # State
    if 'scraped_data' not in st.session_state:
        st.session_state.scraped_data = None
    
    if start_button:
        if not url_input:
            st.error("⚠️ Please enter a URL")
        else:
            try:
                result = asyncio.run(run_scraper(
                    url_input, num_pages, headless, wait_time, status_box, progress_bar
                ))
                
                if result:
                    st.session_state.scraped_data = result
                    st.balloons()
                else:
                    st.warning("No data extracted.")
            except Exception as e:
                st.error(f"Failed: {e}")
    
    # Results
    if st.session_state.scraped_data:
        st.markdown("---")
        st.markdown("## 📊 Extraction Results")
        
        data = st.session_state.scraped_data
        df = pd.DataFrame(data)
        
        # Stats
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Items", len(data))
        c2.metric("Fields", len(df.columns))
        c3.metric("Emails", sum(1 for x in data if x.get('email')))
        c4.metric("Phones", sum(1 for x in data if x.get('phone')))
        
        # Reorder columns
        priority = ['company_name', 'email', 'phone', 'address', 'website', 'description']
        cols = [c for c in priority if c in df.columns] + [c for c in df.columns if c not in priority]
        
        st.dataframe(df[cols], use_container_width=True, height=500)
        
        # Downloads
        c1, c2 = st.columns(2)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        c1.download_button("📥 Download CSV", df[cols].to_csv(index=False).encode('utf-8'), f"data_{timestamp}.csv", "text/csv", use_container_width=True)
        c2.download_button("📄 Download JSON", df[cols].to_json(orient="records", force_ascii=False).encode('utf-8'), f"data_{timestamp}.json", "application/json", use_container_width=True)
        
        # Clear button
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.scraped_data = None
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.warning(
            """
            **⚠️ Disclaimer:**
            This tool is developed for **educational and testing purposes only**. 
            The developer (Achraf MOULJEBOUJ) is not responsible for any misuse of this tool. 
            Users must ensure they comply with the Terms of Service of the target websites 
            and relevant data protection laws (GDPR) before scraping.
            """
        )
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>Made with <span class="heart">♥</span> By <a href="https://achraf.mouljebouj.com">Achraf MOULJEBOUJ</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()