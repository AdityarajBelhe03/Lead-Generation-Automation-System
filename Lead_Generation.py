# Lead Discovery Module - Apollo API Integration for Google Colab
# Part 1: Setup and Lead Discovery

import requests
import json
import pandas as pd
from typing import List, Dict, Optional
import time

# Install required packages (run this cell first in Colab)
# !pip install requests pandas beautifulsoup4 python-readability openai

class LeadDiscovery:
    """
    Lead Discovery class for finding business leads using Apollo API
    """
    
    def __init__(self, apollo_api_key: str):
        """
        Initialize with Apollo API key
        
        Args:
            apollo_api_key (str): Your Apollo API key
        """
        self.apollo_api_key = apollo_api_key
        self.base_url = "https://api.apollo.io/v1"
        self.headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'X-Api-Key': apollo_api_key
        }
    
    def search_companies(self, 
                        industry_keywords: List[str] = None,
                        company_size_min: int = 50,
                        company_size_max: int = 200,
                        location: str = None,
                        limit: int = 10) -> List[Dict]:
        """
        Search for companies using Apollo API
        
        Args:
            industry_keywords (List[str]): Industry keywords to search for
            company_size_min (int): Minimum company size
            company_size_max (int): Maximum company size  
            location (str): Geographic location filter
            limit (int): Number of results to return
            
        Returns:
            List[Dict]: List of company data
        """
        
        # Default industry keywords if none provided
        if industry_keywords is None:
            industry_keywords = ["software", "technology", "SaaS", "IT services"]
        
        # Build search payload for /organizations/search endpoint
        payload = {
            "page": 1,
            "per_page": limit,
            "organization_num_employees_ranges": [f"{company_size_min},{company_size_max}"],
            "q_organization_keyword_tags": industry_keywords[:3]  # Limit to 3 keywords for free plan
        }
        
        # Add location filter if provided
        if location:
            payload["organization_locations"] = [location]
        
        try:
            print(f" Searching for companies with keywords: {', '.join(industry_keywords)}")
            print(f" Company size: {company_size_min}-{company_size_max} employees")
            
            response = requests.post(
                f"{self.base_url}/organizations/search",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                companies = data.get('organizations', [])
                
                print(f" Found {len(companies)} companies")
                return self._process_company_data(companies)
            
            elif response.status_code == 403:
                print(" Free plan limitation detected. Trying alternative approach...")
                return self._search_companies_fallback(industry_keywords, company_size_min, company_size_max, limit)
            
            else:
                print(f" API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            print(" Request timed out")
            return []
        except requests.exceptions.RequestException as e:
            print(f" Request failed: {str(e)}")
            return []
    
    def _search_companies_fallback(self, industry_keywords: List[str], 
                                 company_size_min: int, 
                                 company_size_max: int, 
                                 limit: int) -> List[Dict]:
        """
        Fallback method using simpler API calls for free plan
        """
        print("🔄 Using free plan compatible search...")
        
        # Use a simpler payload structure
        payload = {
            "page": 1,
            "per_page": min(limit, 25),  # Free plan typically limits results
            "organization_num_employees_ranges": [f"{company_size_min},{company_size_max}"]
        }
        
        # Add single industry keyword if provided
        if industry_keywords:
            payload["q_organization_keyword_tags"] = [industry_keywords[0]]
        
        try:
            response = requests.post(
                f"{self.base_url}/organizations/search",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                companies = data.get('organizations', [])
                print(f" Found {len(companies)} companies using fallback method")
                return self._process_company_data(companies)
            else:
                print(f" Fallback also failed: {response.status_code}")
                print(" Consider trying manual company list or upgrading Apollo plan")
                return self._create_sample_companies()
                
        except Exception as e:
            print(f" Fallback failed: {str(e)}")
            return self._create_sample_companies()
    
    def _create_sample_companies(self) -> List[Dict]:
        """
        Create sample companies for demonstration when API fails
        """
        print("📝 Creating sample companies for demonstration...")
        
        sample_companies = [
            {
                'name': 'TechFlow Solutions',
                'website': 'https://techflow.example.com',
                'domain': 'techflow.example.com',
                'industry': 'Software Development',
                'employee_count': 75,
                'description': 'Custom software development and digital transformation services',
                'location': 'San Francisco, CA',
                'founded_year': 2018,
                'linkedin_url': 'https://linkedin.com/company/techflow-solutions',
                'annual_revenue': 5000000,
                'technologies': ['Python', 'React', 'AWS'],
                'raw_data': {}
            },
            {
                'name': 'DataCore Analytics',
                'website': 'https://datacore-analytics.example.com',
                'domain': 'datacore-analytics.example.com',
                'industry': 'Data Analytics',
                'employee_count': 120,
                'description': 'Big data analytics and business intelligence solutions',
                'location': 'Austin, TX',
                'founded_year': 2016,
                'linkedin_url': 'https://linkedin.com/company/datacore-analytics',
                'annual_revenue': 8000000,
                'technologies': ['Python', 'Tableau', 'Snowflake'],
                'raw_data': {}
            },
            {
                'name': 'CloudSync Systems',
                'website': 'https://cloudsync.example.com',
                'domain': 'cloudsync.example.com',
                'industry': 'Cloud Services',
                'employee_count': 95,
                'description': 'Cloud migration and DevOps automation services',
                'location': 'Seattle, WA',
                'founded_year': 2019,
                'linkedin_url': 'https://linkedin.com/company/cloudsync-systems',
                'annual_revenue': 6500000,
                'technologies': ['Docker', 'Kubernetes', 'Terraform'],
                'raw_data': {}
            }
        ]
        
        print("⚠️ Note: These are sample companies for demonstration")
        print("💡 Get real data by upgrading your Apollo plan or using a different lead source")
        
        return sample_companies
    
    def _process_company_data(self, raw_companies: List[Dict]) -> List[Dict]:
        """
        Process and clean company data from Apollo API response
        
        Args:
            raw_companies (List[Dict]): Raw company data from API
            
        Returns:
            List[Dict]: Processed company data
        """
        processed_companies = []
        
        for company in raw_companies:
            try:
                processed_company = {
                    'name': company.get('name', 'Unknown'),
                    'website': company.get('website_url', ''),
                    'domain': company.get('primary_domain', ''),
                    'industry': company.get('industry', 'Unknown'),
                    'employee_count': company.get('estimated_num_employees', 0),
                    'description': company.get('short_description', ''),
                    'location': self._extract_location(company),
                    'founded_year': company.get('founded_year'),
                    'linkedin_url': company.get('linkedin_url', ''),
                    'annual_revenue': company.get('estimated_annual_revenue'),
                    'technologies': company.get('technologies', []),
                    'raw_data': company  # Keep original data for reference
                }
                
                # Only add companies with websites
                if processed_company['website'] or processed_company['domain']:
                    if not processed_company['website'] and processed_company['domain']:
                        processed_company['website'] = f"https://{processed_company['domain']}"
                    
                    processed_companies.append(processed_company)
                    
            except Exception as e:
                print(f"⚠️ Error processing company data: {str(e)}")
                continue
        
        return processed_companies
    
    def _extract_location(self, company: Dict) -> str:
        """
        Extract location information from company data
        
        Args:
            company (Dict): Company data
            
        Returns:
            str: Formatted location string
        """
        try:
            # Try to get headquarters location
            hq = company.get('primary_phone', {})
            if isinstance(hq, dict):
                city = hq.get('city', '')
                country = hq.get('country', '')
                if city and country:
                    return f"{city}, {country}"
            
            # Fallback to other location fields
            locations = company.get('organization_locations', [])
            if locations:
                location = locations[0]
                city = location.get('city', '')
                country = location.get('country', '')
                if city and country:
                    return f"{city}, {country}"
            
            return "Unknown"
            
        except:
            return "Unknown"
    
    def display_leads(self, companies: List[Dict]) -> None:
        """
        Display found leads in a formatted way
        
        Args:
            companies (List[Dict]): List of company data
        """
        if not companies:
            print(" No leads found")
            return
        
        print(f"\n FOUND {len(companies)} POTENTIAL LEADS")
        print("=" * 60)
        
        for i, company in enumerate(companies, 1):
            print(f"\n LEAD #{i}")
            print(f" Company: {company['name']}")
            print(f" Website: {company['website']}")
            print(f" Industry: {company['industry']}")
            print(f" Employees: {company['employee_count']}")
            print(f" Location: {company['location']}")
            if company['description']:
                print(f" Description: {company['description'][:100]}...")
            print("-" * 40)
    
    def save_leads_to_csv(self, companies: List[Dict], filename: str = "leads.csv") -> None:
        """
        Save leads to CSV file
        
        Args:
            companies (List[Dict]): List of company data
            filename (str): Output filename
        """
        if not companies:
            print(" No leads to save")
            return
        
        # Convert to DataFrame for easy CSV export
        df_data = []
        for company in companies:
            df_data.append({
                'Company Name': company['name'],
                'Website': company['website'],
                'Industry': company['industry'],
                'Employee Count': company['employee_count'],
                'Location': company['location'],
                'Description': company['description'],
                'Founded Year': company['founded_year'],
                'LinkedIn': company['linkedin_url']
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv(filename, index=False)
        print(f" Leads saved to {filename}")

# Example usage and testing
def test_lead_discovery(api_key: str = None):
    """
    Test function to demonstrate the Lead Discovery module
    """
    print(" LEAD DISCOVERY MODULE TEST")
    print("=" * 50)
    
    # Debug: Print the received API key (masked for security)
    if api_key:
        print(f" API Key received: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '****'}")
        API_KEY = api_key
    else:
        API_KEY = "5LTMoGEKMvJsj4qM0Ye0EQ"  
    
    if API_KEY == "5LTMoGEKMvJsj4qM0Ye0EQ" or not API_KEY or API_KEY.strip() == "":
        print(" Please provide your Apollo API key")
        print(" Run: test_lead_discovery('your_actual_api_key_here')")
        print(" Or sign up at https://apollo.io to get your free API key")
        return None
    
    # Initialize lead discovery
    ld = LeadDiscovery(API_KEY)
    
    # Search for leads
    leads = ld.search_companies(
        industry_keywords=["software development", "web development", "mobile app"],
        company_size_min=20,
        company_size_max=150,
        limit=5
    )
    
    # Display results
    ld.display_leads(leads)
    
    # Save to CSV
    if leads:
        ld.save_leads_to_csv(leads, "potential_leads.csv")
    
    return leads

# Run the test (uncomment the line below to run)
# test_leads = test_lead_discovery()

print("Lead Discovery Module loaded successfully!")
print("\n TO START LEAD DISCOVERY:")
print("Since you've already replaced your API key, run this command in the next cell:")
print("test_leads = test_lead_discovery()")
print("\nOr create a custom search:")
print(" ld = LeadDiscovery('your_api_key_here')")
print(" leads = ld.search_companies(['software', 'technology'], 50, 200, limit=10)")