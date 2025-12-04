# Ultimate Universal Web Scraper

A complete, self-contained tool that can scrape any website URL with advanced automatic detection capabilities.

## 🌟 Features

- **Automatic Structure Detection**: Identifies cards, tables, lists, grids, and repeating elements
- **Comprehensive Field Extraction**: Extracts text, numbers, links, images, emails, phones, prices, and more
- **Universal Pagination Support**: Handles numbered pages, next buttons, load-more, infinite scroll, and hidden APIs
- **Dynamic Content Handling**: Works with JavaScript-heavy sites and AJAX-loaded content
- **API Interception**: Automatically detects and captures data from background API calls
- **Export Options**: Download data as JSON, CSV, or Excel files
- **Professional UI**: Clean, modern interface with live preview and statistics

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Run the Application**:
   ```bash
   streamlit run ultimate_scraper.py
   ```

3. **Open in Browser**: The app will automatically open in your default browser at `http://localhost:8501`

## 🛠️ How to Use

1. Enter any website URL in the input field
2. Adjust configuration settings as needed:
   - Maximum pages to scrape
   - Scroll iterations for lazy-loaded content
   - Wait times between page loads
3. Click "Start Scraping"
4. Monitor the live preview as data is extracted
5. Once complete, view detailed statistics and field analysis
6. Download your data in JSON, CSV, or Excel format

## 🔧 Technical Capabilities

### Structure Detection
- Automatically identifies repeating content patterns
- Works with cards, product listings, job boards, directories, and more
- Handles complex nested structures and varying layouts

### Field Extraction
- Intelligently extracts contact information (emails, phones)
- Captures pricing, dates, locations, and categories
- Preserves image URLs and link destinations
- Extracts structured data from tables and lists

### Dynamic Content
- Waits for JavaScript-rendered content to load
- Handles lazy-loading images and data
- Works with modern single-page applications (SPAs)

## 📊 Output Formats

### JSON
Complete structured data export with all extracted fields preserved.

### CSV
Tabular format suitable for spreadsheets and databases.

## 🎯 Use Cases

- **Business Intelligence**: Extract competitor pricing, product catalogs
- **Lead Generation**: Collect contact information from directories
- **Market Research**: Gather product listings, reviews, and ratings
- **Job Aggregation**: Pull job postings from career sites
- **Real Estate**: Extract property listings and details
- **Academic Research**: Collect structured data for analysis

## ⚙️ Configuration Options

- **Max Pages**: Control how many pages to scrape (1-100)
- **Wait Time**: Adjust delays between page loads
- **Headless Mode**: Run browser in background or visible mode

## 📝 Requirements

- Python 3.8+
- Streamlit
- Playwright
- BeautifulSoup4
- Pandas
- Requests
- NumPy
- XlsxWriter

## ⚠️ Disclaimer

- This tool is developed for **educational and testing purposes only**. 
- The developer (Achraf MOULJEBOUJ) is not responsible for any misuse of this tool. 
- Users must ensure they comply with the Terms of Service of the target websites 
- and relevant data protection laws (GDPR) before scraping.
- Respecting robots.txt and website terms of service
- Implementing appropriate rate limiting
- Ensuring compliance with applicable laws and regulations
- Obtaining proper permissions when required

## 🤝 Support

For issues, feature requests, or questions, please open an issue on the repository.

---
**Made with ♥ By Achraf MOULJEBOUJ**