# Enhanced Website Scraping & Preprocessing Module
# Specifically designed for Hardware Store Lead Generation

import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import json
from concurrent.futures import ThreadPoolExecutor
import urllib3

# Disable SSL warnings for problematic sites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HardwareStoreLeadScraper:
    """
    Enhanced website scraper specifically designed for hardware store lead generation
    Focuses on extracting IT infrastructure needs, technical pain points, and hardware opportunities
    """

    def __init__(self, timeout: int = 15, max_content_length: int = 4000):
        """
        Initialize the hardware-focused website scraper

        Args:
            timeout (int): Request timeout in seconds
            max_content_length (int): Maximum characters to extract per page
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.session = requests.Session()

        # Enhanced browser headers to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })

        # Disable SSL verification for problematic sites
        self.session.verify = False

        # Initialize hardware-specific extraction patterns
        self._init_hardware_patterns()

    def _init_hardware_patterns(self):
        """Initialize patterns for hardware-specific intelligence extraction"""

        # Infrastructure & Server Needs
        self.infrastructure_patterns = [
            r'(?:server|hosting|infrastructure|cloud|on-premise|data center|hardware) (?:needs?|requirements?|challenges?|issues?|problems?|upgrades?|migration)',
            r'(?:looking for|need|require|seeking) (?:new )?(?:servers?|workstations?|networking|storage|backup)',
            r'(?:performance|speed|capacity|storage|memory|processing) (?:issues?|problems?|bottlenecks?|limitations?)',
            r'(?:scaling|expanding|growing) (?:infrastructure|systems?|operations?|team)',
            r'(?:outdated|legacy|old|aging) (?:systems?|hardware|equipment|infrastructure)'
        ]

        # Growth & Expansion Indicators
        self.growth_patterns = [
            r'(?:hiring|recruiting|adding|expanding) (?:\w+ )?(?:team|developers?|engineers?|staff)',
            r'(?:new office|additional location|expanding to|opening in)',
            r'(?:raised|funding|investment|series [abc]|venture capital)',
            r'(?:growing|scaling|expanding) (?:rapidly|quickly|fast|business|operations)',
            r'(?:remote work|hybrid|distributed team|work from home) (?:setup|infrastructure|needs)',
            r'(?:\d+)% (?:growth|increase) in (?:team|revenue|business)'
        ]

        # Technical Pain Points
        self.pain_point_patterns = [
            r'(?:slow|sluggish|performance|speed) (?:systems?|applications?|processes?|workflows?)',
            r'(?:security|compliance|data protection|backup|disaster recovery) (?:concerns?|issues?|requirements?|needs?)',
            r'(?:downtime|outages?|system failures?|crashes?|reliability issues?)',
            r'(?:integration|compatibility|connectivity) (?:problems?|challenges?|issues?)',
            r'(?:budget|cost|expensive|affordable) (?:constraints?|concerns?|solutions?|hardware)',
            r'(?:manual processes?|inefficient|time-consuming|repetitive tasks?)'
        ]

        # Decision Maker Indicators
        self.decision_maker_patterns = [
            r'(?:cto|chief technology officer|it director|it manager|head of it|technical lead)',
            r'(?:operations? manager|head of operations?|ops lead)',
            r'(?:procurement|purchasing|buying|vendor management)',
            r'(?:budget approval|purchasing decisions?|it spending|technology investments?)'
        ]

        # Technology Stack & Infrastructure
        self.tech_infrastructure_patterns = [
            # Cloud & Hosting
            r'(?:aws|amazon web services|azure|google cloud|gcp|digital ocean|linode)',
            r'(?:cloud|hosting|saas|paas|iaas|hybrid cloud|multi-cloud)',

            # Development & DevOps
            r'(?:docker|kubernetes|containers?|microservices)',
            r'(?:ci/cd|continuous integration|devops|automation)',

            # Databases & Storage
            r'(?:mysql|postgresql|mongodb|redis|elasticsearch|database)',
            r'(?:storage|backup|disaster recovery|data management)',

            # Programming & Frameworks
            r'(?:python|javascript|react|node\.?js|angular|vue|java|\.net)',
            r'(?:web development|mobile development|software development)',

            # Infrastructure Tools
            r'(?:nginx|apache|load balancer|cdn|ssl|security)',
            r'(?:monitoring|logging|analytics|performance tracking)'
        ]

        # Workstation & Hardware Needs
        self.hardware_needs_patterns = [
            r'(?:workstations?|desktops?|laptops?|computers?) (?:for|needed|required)',
            r'(?:high-performance|gaming|graphics?) (?:computers?|workstations?|rigs?)',
            r'(?:development|programming|coding|design) (?:machines?|workstations?|setups?)',
            r'(?:video editing|3d rendering|cad|design) (?:computers?|workstations?)',
            r'(?:networking|switches?|routers?|access points?) (?:equipment|hardware|setup)',
            r'(?:storage|nas|san|backup) (?:solutions?|systems?|hardware)'
        ]

        # Business Context & Urgency
        self.urgency_patterns = [
            r'(?:urgent|asap|immediately|quickly|soon) (?:need|require|looking)',
            r'(?:deadline|timeline|by (?:end of|q[1-4]|january|february|march|april|may|june|july|august|september|october|november|december))',
            r'(?:budget allocated|approved budget|ready to purchase|ready to buy)',
            r'(?:rfp|request for proposal|quotes?|proposals?|vendors?)',
            r'(?:project starting|implementation|rollout|deployment) (?:soon|scheduled|planned)'
        ]

        # Company Size & Growth Indicators
        self.company_scale_patterns = [
            r'(?:\d+(?:\+|plus)) (?:employees?|team members?|staff)',
            r'(?:startup|scale-up|growing company|established company)',
            r'(?:series [abc]|funding|investment|revenue of \$?\d+)',
            r'(?:multiple offices?|locations?|branches?|sites?)',
            r'(?:international|global|worldwide|multiple countries?)'
        ]

    def scrape_company_website(self, company: Dict) -> Dict:
        """
        Enhanced scraping with hardware-specific intelligence extraction

        Args:
            company (Dict): Company data with website URL

        Returns:
            Dict: Enhanced company data with hardware-focused insights
        """
        print(f" Hardware-focused scraping: {company['name']} ({company['website']})")

        # Initialize enhanced company data with hardware-specific structure
        enhanced_company = company.copy()
        enhanced_company['hardware_intelligence'] = {
            'infrastructure_needs': [],
            'growth_indicators': [],
            'technical_pain_points': [],
            'decision_makers': [],
            'tech_stack': [],
            'hardware_opportunities': [],
            'urgency_signals': [],
            'company_scale': [],
            'budget_indicators': [],
            'scraping_success': False,
            'scraping_error': None,
            'content_preview': '',
            'hardware_readiness_score': 0
        }

        try:
            # Multi-page scraping strategy
            pages_to_scrape = self._get_strategic_pages(company['website'])
            all_content = ""

            for page_url in pages_to_scrape:
                page_data = self._scrape_single_page(page_url)
                if page_data['success']:
                    all_content += f"\n--- {page_url} ---\n" + page_data['content']

                    # Break early if we have enough content
                    if len(all_content) > self.max_content_length:
                        break

            if all_content:
                enhanced_company['hardware_intelligence']['scraping_success'] = True
                enhanced_company['hardware_intelligence']['content_preview'] = all_content[:500]

                # Extract hardware-specific intelligence
                self._extract_hardware_intelligence(enhanced_company, all_content)

                # Calculate hardware readiness score
                enhanced_company['hardware_intelligence']['hardware_readiness_score'] = self._calculate_hardware_readiness_score(enhanced_company)

                print(f" Successfully extracted hardware intelligence from {company['name']}")

            else:
                enhanced_company['hardware_intelligence']['scraping_error'] = "No content extracted from any pages"
                print(f"No content extracted from {company['name']}")

        except Exception as e:
            enhanced_company['hardware_intelligence']['scraping_error'] = str(e)
            print(f" Error processing {company['name']}: {str(e)}")

        return enhanced_company

    def _get_strategic_pages(self, base_url: str) -> List[str]:
        """
        Get strategic pages to scrape based on hardware sales priorities

        Args:
            base_url (str): Base website URL

        Returns:
            List[str]: Prioritized list of URLs to scrape
        """
        # Always start with homepage
        pages = [base_url]

        try:
            # Get homepage first to find additional pages
            homepage_data = self._scrape_single_page(base_url)
            if not homepage_data['success']:
                return pages

            soup = homepage_data['soup']

            # High-priority pages for hardware intelligence
            priority_pages = {
                'about': ['about', 'company', 'team', 'story'],
                'services': ['services', 'solutions', 'products', 'offerings'],
                'technology': ['technology', 'tech-stack', 'infrastructure', 'platform'],
                'careers': ['careers', 'jobs', 'hiring', 'join-us', 'work-with-us'],
                'case-studies': ['case-studies', 'portfolio', 'work', 'projects'],
                'contact': ['contact', 'get-in-touch', 'reach-us']
            }

            # Find links matching priority pages
            links = soup.find_all('a', href=True)
            found_pages = set()

            for link in links:
                href = link['href'].lower()
                link_text = link.get_text().lower().strip()

                for category, keywords in priority_pages.items():
                    for keyword in keywords:
                        if (keyword in href or keyword in link_text) and len(found_pages) < 4:
                            full_url = urljoin(base_url, link['href'])
                            if full_url not in found_pages and full_url != base_url:
                                found_pages.add(full_url)
                                pages.append(full_url)
                                break
                    if len(found_pages) >= 4:
                        break
                if len(found_pages) >= 4:
                    break

        except Exception as e:
            print(f" Error finding strategic pages for {base_url}: {str(e)}")

        return pages[:5]  # Limit to 5 pages maximum

    def _scrape_single_page(self, url: str) -> Dict:
        """
        Enhanced single page scraping with better error handling, HTTPS forcing, and retry

        Args:
            url (str): URL to scrape

        Returns:
            Dict: Scraping result with content and status
        """
        try:
            # Force HTTPS scheme and clean the URL
            parsed = urlparse(url)
            if not parsed.scheme:
                url = 'https://' + url
            elif parsed.scheme == 'http':
                url = url.replace("http://", "https://")

            # Add a short delay to reduce chance of rate limiting
            time.sleep(0.5)

            try:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f" First request failed for {url}: {str(e)}. Retrying once...")
                time.sleep(1)  # Backoff
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                response.raise_for_status()

            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return {'success': False, 'content': '', 'soup': None, 'error': 'Not HTML content'}

            # Parse HTML safely
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
            except Exception:
                soup = BeautifulSoup(response.content, 'lxml')

            # Remove unwanted HTML elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
                element.decompose()

            # Extract and clean main content
            content = self._extract_main_content_enhanced(soup)
            clean_content = self._clean_text_enhanced(content)

            return {
                'success': True,
                'content': clean_content,
                'soup': soup,
                'error': None
            }

        except requests.exceptions.SSLError as e:
            print(f" SSL Error for {url}: {str(e)}")
            return {'success': False, 'content': '', 'soup': None, 'error': f'SSL Error: {str(e)}'}
        except requests.exceptions.Timeout:
            print(f"⏱ Timeout while accessing {url}")
            return {'success': False, 'content': '', 'soup': None, 'error': 'Request timeout'}
        except requests.exceptions.RequestException as e:
            print(f" Request failed for {url}: {str(e)}")
            return {'success': False, 'content': '', 'soup': None, 'error': f'Request failed: {str(e)}'}
        except Exception as e:
            print(f" Unexpected error for {url}: {str(e)}")
            return {'success': False, 'content': '', 'soup': None, 'error': f'Parsing failed: {str(e)}'}

    def _extract_main_content_enhanced(self, soup: BeautifulSoup) -> str:
        """
        Enhanced content extraction with multiple strategies

        Args:
            soup (BeautifulSoup): Parsed HTML

        Returns:
            str: Extracted main content
        """
        content_parts = []

        # Strategy 1: Look for main content containers
        main_selectors = [
            'main', '[role="main"]', '.main-content', '#main-content', '.content', '#content',
            'article', '.post', '.entry-content', '.page-content'
        ]

        for selector in main_selectors:
            elements = soup.select(selector)
            if elements:
                content_parts.append(' '.join([elem.get_text() for elem in elements]))
                break

        # Strategy 2: Look for business-specific sections
        business_selectors = [
            '.hero', '.banner', '.intro', '.about', '.services', '.solutions',
            '.company', '.team', '.technology', '.platform', '.products'
        ]

        for selector in business_selectors:
            elements = soup.select(selector)
            for elem in elements[:2]:  # Limit to avoid duplication
                content_parts.append(elem.get_text())

        # Strategy 3: Get headings and important text
        headings = soup.find_all(['h1', 'h2', 'h3'])
        for heading in headings[:10]:  # Top 10 headings
            content_parts.append(heading.get_text())

        # Strategy 4: Fallback to body content
        if not content_parts:
            body = soup.find('body')
            if body:
                content_parts.append(body.get_text())
            else:
                content_parts.append(soup.get_text())

        return ' '.join(content_parts)

    def _clean_text_enhanced(self, text: str) -> str:
        """
        Enhanced text cleaning for better extraction

        Args:
            text (str): Raw text to clean

        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove common web artifacts
        text = re.sub(r'(?:cookie|privacy policy|terms of service|subscribe|newsletter)', '', text, flags=re.IGNORECASE)

        # Keep important punctuation but remove special characters
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\$\%\+\#]', ' ', text)

        # Remove very short words except important ones
        words = text.split()
        important_short_words = {'we', 'us', 'or', 'to', 'is', 'it', 'ai', 'ml', 'io', 'ui', 'ux', 'qa', 'qa', 'bi'}
        words = [word for word in words if len(word) > 2 or word.lower() in important_short_words]

        # Remove duplicate words in sequence
        cleaned_words = []
        prev_word = ""
        for word in words:
            if word.lower() != prev_word.lower():
                cleaned_words.append(word)
                prev_word = word

        return ' '.join(cleaned_words).strip()

    def _extract_hardware_intelligence(self, company: Dict, content: str) -> None:
        """
        Extract comprehensive hardware-specific intelligence

        Args:
            company (Dict): Company data to enhance
            content (str): Scraped content to analyze
        """
        content_lower = content.lower()
        intelligence = company['hardware_intelligence']

        # Extract infrastructure needs
        intelligence['infrastructure_needs'] = self._extract_pattern_matches(
            content_lower, self.infrastructure_patterns, "Infrastructure Needs"
        )

        # Extract growth indicators
        intelligence['growth_indicators'] = self._extract_pattern_matches(
            content_lower, self.growth_patterns, "Growth Indicators"
        )

        # Extract technical pain points
        intelligence['technical_pain_points'] = self._extract_pattern_matches(
            content_lower, self.pain_point_patterns, "Technical Pain Points"
        )

        # Extract decision maker indicators
        intelligence['decision_makers'] = self._extract_pattern_matches(
            content_lower, self.decision_maker_patterns, "Decision Makers"
        )

        # Extract technology stack
        intelligence['tech_stack'] = self._extract_pattern_matches(
            content_lower, self.tech_infrastructure_patterns, "Technology Stack"
        )

        # Extract hardware opportunities
        intelligence['hardware_opportunities'] = self._extract_pattern_matches(
            content_lower, self.hardware_needs_patterns, "Hardware Opportunities"
        )

        # Extract urgency signals
        intelligence['urgency_signals'] = self._extract_pattern_matches(
            content_lower, self.urgency_patterns, "Urgency Signals"
        )

        # Extract company scale indicators
        intelligence['company_scale'] = self._extract_pattern_matches(
            content_lower, self.company_scale_patterns, "Company Scale"
        )

        # Extract budget indicators
        intelligence['budget_indicators'] = self._extract_budget_indicators(content_lower)

        # Additional context extraction
        self._extract_additional_context(company, content_lower)

    def _extract_pattern_matches(self, content: str, patterns: List[str], category: str) -> List[str]:
        """
        Extract matches for given patterns

        Args:
            content (str): Content to search
            patterns (List[str]): Regex patterns to match
            category (str): Category name for logging

        Returns:
            List[str]: List of matched phrases
        """
        matches = []

        for pattern in patterns:
            try:
                found_matches = re.findall(pattern, content, re.IGNORECASE)
                for match in found_matches:
                    if isinstance(match, tuple):
                        match = ' '.join(match)

                    clean_match = match.strip().rstrip('.,!?:;')
                    if len(clean_match) > 5 and clean_match not in matches:
                        matches.append(clean_match)

                        # Limit matches per category
                        if len(matches) >= 5:
                            break
            except re.error:
                continue  # Skip invalid regex patterns

        return matches[:5]  # Return top 5 matches

    def _extract_budget_indicators(self, content: str) -> List[str]:
        """
        Extract budget and financial indicators

        Args:
            content (str): Content to search

        Returns:
            List[str]: Budget indicators
        """
        budget_patterns = [
            r'budget of \$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:million|thousand|k|m)?',
            r'revenue of \$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:million|thousand|k|m)?',
            r'funding of \$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:million|thousand|k|m)?',
            r'raised \$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:million|thousand|k|m)?',
            r'(?:investment|capital|funding|raised|budget|revenue)\s+(?:of\s+)?\$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:million|thousand|k|m)?'
        ]

        indicators = []
        for pattern in budget_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                indicators.append(f"Financial indicator: ${match}")
                if len(indicators) >= 3:
                    break

        return indicators

    def _extract_additional_context(self, company: Dict, content: str) -> None:
        """
        Extract additional context for personalized outreach

        Args:
            company (Dict): Company data to enhance
            content (str): Content to analyze
        """
        intelligence = company['hardware_intelligence']

        # Extract key business phrases for personalization
        business_phrases = []
        phrase_patterns = [
            r'we (?:help|enable|empower|support) (?:companies|businesses|organizations|clients) (?:to )?([^.]{10,80})',
            r'our mission is (?:to )?([^.]{10,80})',
            r'we specialize in ([^.]{10,80})',
            r'(?:focused on|committed to|dedicated to) ([^.]{10,80})'
        ]

        for pattern in phrase_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                clean_phrase = match.strip().rstrip('.,!?:;')
                if len(clean_phrase) > 10:
                    business_phrases.append(clean_phrase)
                if len(business_phrases) >= 2:
                    break

        intelligence['business_context'] = business_phrases

        # Extract industry-specific mentions
        industry_keywords = {
            'fintech': ['financial', 'banking', 'payments', 'fintech', 'trading'],
            'healthcare': ['healthcare', 'medical', 'hospital', 'patient', 'clinical'],
            'ecommerce': ['ecommerce', 'retail', 'shopping', 'marketplace', 'online store'],
            'saas': ['saas', 'software as a service', 'subscription', 'cloud platform'],
            'startup': ['startup', 'early-stage', 'seed', 'series a', 'founders']
        }

        detected_industries = []
        for industry, keywords in industry_keywords.items():
            for keyword in keywords:
                if keyword in content:
                    detected_industries.append(industry)
                    break

        intelligence['industry_context'] = detected_industries

    def _calculate_hardware_readiness_score(self, company: Dict) -> int:
        """
        Calculate hardware readiness score based on extracted intelligence

        Args:
            company (Dict): Company with extracted intelligence

        Returns:
            int: Score from 0-100 indicating hardware purchase readiness
        """
        intelligence = company['hardware_intelligence']
        score = 0

        # Infrastructure needs (30 points)
        if intelligence['infrastructure_needs']:
            score += min(30, len(intelligence['infrastructure_needs']) * 10)

        # Growth indicators (25 points)
        if intelligence['growth_indicators']:
            score += min(25, len(intelligence['growth_indicators']) * 8)

        # Technical pain points (20 points)
        if intelligence['technical_pain_points']:
            score += min(20, len(intelligence['technical_pain_points']) * 7)

        # Urgency signals (15 points)
        if intelligence['urgency_signals']:
            score += min(15, len(intelligence['urgency_signals']) * 15)

        # Budget indicators (10 points)
        if intelligence['budget_indicators']:
            score += min(10, len(intelligence['budget_indicators']) * 10)

        return min(100, score)

    def scrape_multiple_companies(self, companies: List[Dict], max_workers: int = 2) -> List[Dict]:
        """
        Scrape multiple companies with parallel processing (reduced workers for stability)

        Args:
            companies (List[Dict]): List of companies to scrape
            max_workers (int): Maximum number of parallel workers

        Returns:
            List[Dict]: List of enhanced companies with hardware intelligence
        """
        print(f" Starting hardware-focused scraping of {len(companies)} companies...")

        enhanced_companies = []

        # Use ThreadPoolExecutor with reduced workers for stability
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scraping tasks
            future_to_company = {
                executor.submit(self.scrape_company_website, company): company
                for company in companies
            }

            # Collect results as they complete
            for future in future_to_company:
                try:
                    enhanced_company = future.result(timeout=45)  # Increased timeout
                    enhanced_companies.append(enhanced_company)
                except Exception as e:
                    company = future_to_company[future]
                    print(f" Failed to scrape {company['name']}: {str(e)}")
                    # Add company with error info
                    company['hardware_intelligence'] = {
                        'scraping_success': False,
                        'scraping_error': str(e),
                        'infrastructure_needs': [],
                        'growth_indicators': [],
                        'technical_pain_points': [],
                        'decision_makers': [],
                        'tech_stack': [],
                        'hardware_opportunities': [],
                        'urgency_signals': [],
                        'company_scale': [],
                        'budget_indicators': [],
                        'hardware_readiness_score': 0,
                        'content_preview': ''
                    }
                    enhanced_companies.append(company)

        print(f" Completed hardware intelligence extraction for {len(enhanced_companies)} companies")
        return enhanced_companies

    def display_hardware_insights(self, companies: List[Dict]) -> None:
        """
        Display hardware-focused insights in a formatted way

        Args:
            companies (List[Dict]): List of companies with hardware intelligence
        """
        print(f"\n HARDWARE INTELLIGENCE REPORT FOR {len(companies)} COMPANIES")
        print("=" * 80)

        for i, company in enumerate(companies, 1):
            intel = company.get('hardware_intelligence', {})

            print(f"\n COMPANY #{i}: {company['name']}")
            print(f" Website: {company['website']}")
            print(f" Industry: {company.get('industry', 'Unknown')}")
            print(f" Employees: {company.get('employee_count', 'Unknown')}")
            print(f" Scraping Success: {intel.get('scraping_success', False)}")
            print(f" Hardware Readiness Score: {intel.get('hardware_readiness_score', 0)}/100")

            if intel.get('scraping_success'):
                # Infrastructure needs
                if intel.get('infrastructure_needs'):
                    print(f" Infrastructure Needs: {', '.join(intel['infrastructure_needs'][:2])}")

                # Growth indicators
                if intel.get('growth_indicators'):
                    print(f" Growth Signals: {', '.join(intel['growth_indicators'][:2])}")

                # Technical pain points
                if intel.get('technical_pain_points'):
                    print(f" Pain Points: {', '.join(intel['technical_pain_points'][:2])}")

                # Technology stack
                if intel.get('tech_stack'):
                    print(f" Tech Stack: {', '.join(intel['tech_stack'][:4])}")

                # Hardware opportunities
                if intel.get('hardware_opportunities'):
                    print(f" Hardware Opportunities: {', '.join(intel['hardware_opportunities'][:2])}")

                # Urgency signals
                if intel.get('urgency_signals'):
                    print(f"⏰ Urgency: {', '.join(intel['urgency_signals'][:1])}")

                # Budget indicators
                if intel.get('budget_indicators'):
                    print(f" Budget Signals: {', '.join(intel['budget_indicators'][:1])}")

                # Content preview
                preview = intel.get('content_preview', '')[:150]
                if preview:
                    print(f" Content Preview: {preview}...")

            else:
                error = intel.get('scraping_error', 'Unknown error')
                print(f" Scraping Error: {error[:100]}...")

            print("-" * 60)

    def save_hardware_intelligence(self, companies: List[Dict], base_filename: str = "hardware_leads") -> None:
        """
        Save hardware intelligence data in multiple formats

        Args:
            companies (List[Dict]): Companies with hardware intelligence
            base_filename (str): Base filename for output files
        """
        try:
            # Save detailed JSON data
            json_filename = f"{base_filename}_detailed.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(companies, f, indent=2, ensure_ascii=False)
            print(f" Detailed data saved to {json_filename}")

            # Save CSV summary
            csv_filename = f"{base_filename}_summary.csv"
            self._save_csv_summary(companies, csv_filename)

            # Save hardware prospects (high-scoring leads)
            prospects_filename = f"{base_filename}_prospects.json"
            high_scoring_leads = [
                company for company in companies
                if company.get('hardware_intelligence', {}).get('hardware_readiness_score', 0) >= 30
            ]

            if high_scoring_leads:
                with open(prospects_filename, 'w', encoding='utf-8') as f:
                    json.dump(high_scoring_leads, f, indent=2, ensure_ascii=False)
                print(f" High-potential prospects saved to {prospects_filename}")
                print(f"   Found {len(high_scoring_leads)} companies with readiness score >= 30")

        except Exception as e:
            print(f" Failed to save data: {str(e)}")

    def _save_csv_summary(self, companies: List[Dict], filename: str) -> None:
        """
        Save CSV summary of hardware intelligence

        Args:
            companies (List[Dict]): Companies with data
            filename (str): CSV filename
        """
        try:
            import pandas as pd

            csv_data = []
            for company in companies:
                intel = company.get('hardware_intelligence', {})

                csv_data.append({
                    'Company Name': company.get('name', ''),
                    'Website': company.get('website', ''),
                    'Industry': company.get('industry', ''),
                    'Employee Count': company.get('employee_count', 0),
                    'Location': company.get('location', ''),
                    'Scraping Success': intel.get('scraping_success', False),
                    'Hardware Readiness Score': intel.get('hardware_readiness_score', 0),
                    'Infrastructure Needs': ' | '.join(intel.get('infrastructure_needs', [])[:3]),
                    'Growth Indicators': ' | '.join(intel.get('growth_indicators', [])[:3]),
                    'Technical Pain Points': ' | '.join(intel.get('technical_pain_points', [])[:3]),
                    'Tech Stack': ' | '.join(intel.get('tech_stack', [])[:5]),
                    'Hardware Opportunities': ' | '.join(intel.get('hardware_opportunities', [])[:3]),
                    'Urgency Signals': ' | '.join(intel.get('urgency_signals', [])[:2]),
                    'Budget Indicators': ' | '.join(intel.get('budget_indicators', [])[:2]),
                    'Decision Makers': ' | '.join(intel.get('decision_makers', [])[:2]),
                    'Company Scale': ' | '.join(intel.get('company_scale', [])[:2]),
                    'Content Preview': intel.get('content_preview', '')[:200] + '...' if intel.get('content_preview') else '',
                    'Scraping Error': intel.get('scraping_error', '') if not intel.get('scraping_success') else ''
                })

            df = pd.DataFrame(csv_data)
            df.to_csv(filename, index=False)
            print(f" CSV summary saved to {filename}")

        except ImportError:
            print(" pandas not available, skipping CSV export")
        except Exception as e:
            print(f" CSV export failed: {str(e)}")

    def get_top_prospects(self, companies: List[Dict], min_score: int = 40) -> List[Dict]:
        """
        Get top hardware prospects based on readiness score

        Args:
            companies (List[Dict]): Companies with hardware intelligence
            min_score (int): Minimum readiness score threshold

        Returns:
            List[Dict]: Top prospects sorted by readiness score
        """
        prospects = [
            company for company in companies
            if company.get('hardware_intelligence', {}).get('hardware_readiness_score', 0) >= min_score
        ]

        # Sort by readiness score (descending)
        prospects.sort(
            key=lambda x: x.get('hardware_intelligence', {}).get('hardware_readiness_score', 0),
            reverse=True
        )

        return prospects

    def generate_prospect_summary(self, companies: List[Dict]) -> Dict:
        """
        Generate summary statistics for hardware prospects

        Args:
            companies (List[Dict]): Companies with hardware intelligence

        Returns:
            Dict: Summary statistics
        """
        total_companies = len(companies)
        successful_scrapes = sum(1 for c in companies if c.get('hardware_intelligence', {}).get('scraping_success', False))

        # Score distribution
        scores = [c.get('hardware_intelligence', {}).get('hardware_readiness_score', 0) for c in companies]
        high_potential = sum(1 for s in scores if s >= 50)
        medium_potential = sum(1 for s in scores if 20 <= s < 50)
        low_potential = sum(1 for s in scores if s < 20)

        # Top categories of opportunities
        all_infrastructure = []
        all_pain_points = []
        all_opportunities = []

        for company in companies:
            intel = company.get('hardware_intelligence', {})
            all_infrastructure.extend(intel.get('infrastructure_needs', []))
            all_pain_points.extend(intel.get('technical_pain_points', []))
            all_opportunities.extend(intel.get('hardware_opportunities', []))

        summary = {
            'total_companies': total_companies,
            'successful_scrapes': successful_scrapes,
            'scraping_success_rate': f"{(successful_scrapes/total_companies*100):.1f}%" if total_companies > 0 else "0%",
            'high_potential_leads': high_potential,
            'medium_potential_leads': medium_potential,
            'low_potential_leads': low_potential,
            'average_readiness_score': sum(scores) / len(scores) if scores else 0,
            'top_infrastructure_needs': self._get_top_mentions(all_infrastructure),
            'top_pain_points': self._get_top_mentions(all_pain_points),
            'top_hardware_opportunities': self._get_top_mentions(all_opportunities)
        }

        return summary

    def _get_top_mentions(self, items: List[str], top_n: int = 5) -> List[str]:
        """
        Get top mentioned items from a list

        Args:
            items (List[str]): List of items to count
            top_n (int): Number of top items to return

        Returns:
            List[str]: Top mentioned items
        """
        if not items:
            return []

        # Count mentions
        from collections import Counter
        counts = Counter([item.lower() for item in items])
        return [item for item, count in counts.most_common(top_n)]


# Enhanced test function for hardware store lead generation
def test_hardware_scraper(companies: List[Dict] = None, save_results: bool = True):
    """
    Test the enhanced hardware-focused website scraper

    Args:
        companies (List[Dict]): Companies to scrape (from Apollo API)
        save_results (bool): Whether to save results to files

    Returns:
        List[Dict]: Enhanced companies with hardware intelligence
    """
    print("🔧 HARDWARE STORE LEAD SCRAPER TEST")
    print("=" * 60)

    # Use provided companies or create hardware-relevant samples
    if not companies:
        print(" Using hardware-relevant sample companies for testing...")
        companies = [
            {
                'name': 'TechFlow Solutions',
                'website': 'https://techflow.example.com',
                'industry': 'Software Development',
                'employee_count': 75,
                'location': 'San Francisco, CA'
            },
            {
                'name': 'DataCore Analytics',
                'website': 'https://example.com',  # Use a real site for testing
                'industry': 'Data Analytics',
                'employee_count': 120,
                'location': 'Austin, TX'
            }
        ]

    print(f" Target: {len(companies)} companies for hardware intelligence extraction")

    # Initialize enhanced scraper
    scraper = HardwareStoreLeadScraper(timeout=20, max_content_length=5000)

    # Scrape companies with hardware focus
    enhanced_companies = scraper.scrape_multiple_companies(companies, max_workers=2)

    # Display hardware intelligence
    scraper.display_hardware_insights(enhanced_companies)

    # Generate prospect summary
    summary = scraper.generate_prospect_summary(enhanced_companies)

    print(f"\n HARDWARE PROSPECTS SUMMARY")
    print("=" * 50)
    print(f" Total Companies Processed: {summary['total_companies']}")
    print(f" Successful Scrapes: {summary['successful_scrapes']} ({summary['scraping_success_rate']})")
    print(f" High Potential Leads (50+ score): {summary['high_potential_leads']}")
    print(f" Medium Potential Leads (20-49 score): {summary['medium_potential_leads']}")
    print(f" Low Potential Leads (<20 score): {summary['low_potential_leads']}")
    print(f" Average Readiness Score: {summary['average_readiness_score']:.1f}/100")

    if summary['top_infrastructure_needs']:
        print(f"🏗️ Top Infrastructure Needs: {', '.join(summary['top_infrastructure_needs'][:3])}")

    if summary['top_pain_points']:
        print(f" Common Pain Points: {', '.join(summary['top_pain_points'][:3])}")

    if summary['top_hardware_opportunities']:
        print(f" Hardware Opportunities: {', '.join(summary['top_hardware_opportunities'][:3])}")

    # Get top prospects
    top_prospects = scraper.get_top_prospects(enhanced_companies, min_score=30)
    if top_prospects:
        print(f"\n TOP {len(top_prospects)} HARDWARE PROSPECTS:")
        for i, prospect in enumerate(top_prospects[:5], 1):
            score = prospect.get('hardware_intelligence', {}).get('hardware_readiness_score', 0)
            print(f"   {i}. {prospect['name']} (Score: {score}/100)")

    # Save results if requested
    if save_results:
        print(f"\n SAVING HARDWARE INTELLIGENCE DATA...")
        scraper.save_hardware_intelligence(enhanced_companies, "hardware_leads")

        print(f"\n Files Generated:")
        print(f"    hardware_leads_detailed.json (Full intelligence data)")
        print(f"    hardware_leads_summary.csv (Summary for review)")
        if top_prospects:
            print(f"   hardware_leads_prospects.json (High-potential leads)")

    print(f"\n Hardware intelligence extraction completed!")
    print(f" Ready for personalized hardware sales outreach generation!")

    return enhanced_companies


# Integration function for seamless workflow
def enhance_leads_with_hardware_intelligence(apollo_leads: List[Dict]) -> List[Dict]:
    """
    Main function to enhance Apollo leads with hardware-specific intelligence

    Args:
        apollo_leads (List[Dict]): Leads from Apollo API

    Returns:
        List[Dict]: Enhanced leads ready for hardware sales outreach
    """
    print(" ENHANCING LEADS WITH HARDWARE INTELLIGENCE")
    print("=" * 60)

    if not apollo_leads:
        print(" No leads provided for enhancement")
        return []

    # Initialize hardware scraper
    scraper = HardwareStoreLeadScraper(timeout=20, max_content_length=5000)

    # Process all leads
    enhanced_leads = scraper.scrape_multiple_companies(apollo_leads, max_workers=2)

    # Auto-save results
    scraper.save_hardware_intelligence(enhanced_leads, "enhanced_hardware_leads")

    # Display summary
    summary = scraper.generate_prospect_summary(enhanced_leads)
    print(f"\n ENHANCEMENT COMPLETE!")
    print(f"    Processed: {summary['total_companies']} companies")
    print(f"    High-potential leads: {summary['high_potential_leads']}")
    print(f"    Success rate: {summary['scraping_success_rate']}")

    return enhanced_leads


print("✅ Enhanced Hardware Store Lead Scraper loaded successfully!")
print("\n READY FOR HARDWARE-FOCUSED LEAD INTELLIGENCE EXTRACTION!")
print("\n USAGE OPTIONS:")
print(" enhance_leads_with_hardware_intelligence(your_apollo_leads)")
print(" test_hardware_scraper(your_apollo_leads)")
print(" scraper = HardwareStoreLeadScraper()")
print(" enhanced_leads = scraper.scrape_multiple_companies(leads)")
print("\n This scraper is optimized for:")
print("   • Infrastructure needs detection")
print("   • Technical pain points identification")
print("   • Growth signals recognition")
print("   • Hardware opportunity assessment")
print("   • Decision maker context")
print("   • Budget indicators")
print("   • Hardware readiness scoring")