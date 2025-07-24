# AI Message Generation System for Hardware Store Lead Generation
# Phase 3: Personalized Email Generation using DeepSeek R1 via OpenRouter

import json
import os
from openai import OpenAI
from typing import Dict, List, Optional, Tuple
import time
import random
from datetime import datetime
import re

class HardwareLeadMessageGenerator:
    """
    AI-powered message generator specifically designed for hardware store lead outreach
    Uses DeepSeek R1 via OpenRouter API for generating personalized B2B emails
    """
    
    def __init__(self, api_key: str, site_url: str = "hardware-leads-generator", site_name: str = "Hardware Sales Assistant"):
        """
        Initialize the AI message generator
        
        Args:
            api_key (str): OpenRouter API key
            site_url (str): Your site URL for OpenRouter rankings
            site_name (str): Your site name for OpenRouter rankings
        """
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
        self.site_url = site_url
        self.site_name = site_name
        self.model = "deepseek/deepseek-r1-0528:free"
        
        # Hardware store context
        self.hardware_store_context = {
            "store_name": "TechCore Hardware Solutions",
            "specialties": [
                "High-performance workstations",
                "Server infrastructure",
                "Networking equipment", 
                "Custom PC builds",
                "Enterprise storage solutions",
                "Video editing workstations",
                "Development machines",
                "Gaming rigs"
            ],
            "value_propositions": [
                "Custom configuration to exact specifications",
                "Competitive enterprise pricing",
                "Local technical support and warranty",
                "Fast deployment and setup",
                "Ongoing maintenance partnerships",
                "Bulk ordering discounts"
            ],
            "contact_info": {
                "email": "sales@techcorehardware.com",
                "phone": "+1 (555) 123-TECH",
                "website": "www.techcorehardware.com"
            }
        }
        
        # Initialize prompt templates
        self._init_prompt_templates()
    
    def _init_prompt_templates(self):
        """Initialize comprehensive prompt templates for different scenarios"""
        
        # Main system prompt for DeepSeek R1
        self.system_prompt = """You are a professional B2B sales representative for TechCore Hardware Solutions, a premium computer hardware store specializing in business workstations, servers, and IT infrastructure.

CRITICAL INSTRUCTIONS:
1. Generate ONLY professional, helpful, and non-pushy B2B sales emails
2. Use ONLY the provided company data - DO NOT hallucinate or invent information
3. Focus on hardware solutions that genuinely match the company's apparent needs
4. Maintain a consultative, educational tone rather than aggressive sales
5. Always include a soft call-to-action, never demand immediate purchase
6. Keep emails concise (150-200 words max) and scannable
7. Generate exactly 5 different email variations for each company

HARDWARE SOLUTIONS TO REFERENCE:
- High-performance workstations for development/design teams
- Server infrastructure for growing businesses
- Networking equipment for office expansion
- Custom PC builds for specific use cases
- Enterprise storage and backup solutions
- Video editing and rendering workstations

YOUR ROLE: Help businesses solve their hardware challenges with appropriate solutions, not just sell products."""

        # Email generation prompt template - Fixed formatting issue
        self.email_prompt_template = """Based on the following company intelligence data, generate 5 different personalized B2B sales emails for TechCore Hardware Solutions.

COMPANY DATA:
```json
{company_data}
```

REQUIREMENTS FOR EACH EMAIL:
1. Professional subject line (5-8 words)
2. Personalized greeting using company name
3. Reference specific company details from the data (industry, size, tech stack, etc.)
4. Suggest relevant hardware solutions based on their apparent needs
5. Include one specific value proposition
6. Soft call-to-action (consultation, quote, discussion)
7. Professional signature
8. Keep each email 150-200 words maximum

HARDWARE FOCUS AREAS TO CONSIDER:
- If they're a software company: Development workstations, servers
- If they're growing: Infrastructure scaling, networking
- If they mention tech stack: Compatible hardware configurations
- If they have pain points: Solutions to address specific issues
- If they show urgency signals: Fast deployment capabilities

OUTPUT FORMAT:
Generate exactly 5 email variations as a JSON array with this structure:
[
  {{
    "email_number": 1,
    "subject_line": "Subject here",
    "email_body": "Full email body here",
    "personalization_notes": "Why this approach was chosen",
    "hardware_focus": "Primary hardware solution highlighted"
  }},
  {{
    "email_number": 2,
    "subject_line": "Second subject here",
    "email_body": "Second email body here",
    "personalization_notes": "Personalization approach",
    "hardware_focus": "Hardware solution focus"
  }}
  ...continue for 5 emails total
]

AVOID:
- Generic templates that could apply to any company
- Overly aggressive sales language
- Making up company details not in the provided data
- Promising specific pricing without consultation
- Using buzzwords without substance

Begin generation:"""

    def load_company_data(self, json_file_path: str) -> List[Dict]:
        """
        Load company data from JSON file
        
        Args:
            json_file_path (str): Path to the JSON file with company data
            
        Returns:
            List[Dict]: List of company data dictionaries
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                companies = json.load(f)
            
            print(f" Loaded {len(companies)} companies from {json_file_path}")
            return companies
            
        except FileNotFoundError:
            print(f" File not found: {json_file_path}")
            return []
        except json.JSONDecodeError as e:
            print(f" JSON parsing error: {str(e)}")
            return []
        except Exception as e:
            print(f" Error loading file: {str(e)}")
            return []

    def prepare_company_for_ai(self, company: Dict) -> str:
        """
        Prepare company data for AI consumption by filtering and formatting
        
        Args:
            company (Dict): Raw company data
            
        Returns:
            str: Formatted company data for AI prompt
        """
        # Extract key information for AI
        ai_ready_data = {
            "company_name": company.get('name', 'Unknown'),
            "website": company.get('website', ''),
            "industry": company.get('industry', 'Unknown'),
            "employee_count": company.get('employee_count', 0),
            "location": company.get('location', 'Unknown'),
            "founded_year": company.get('founded_year'),
            "description": company.get('description', ''),
        }
        
        # Add hardware intelligence if available
        hardware_intel = company.get('hardware_intelligence', {})
        if hardware_intel:
            ai_ready_data.update({
                "hardware_readiness_score": hardware_intel.get('hardware_readiness_score', 0),
                "infrastructure_needs": hardware_intel.get('infrastructure_needs', [])[:3],
                "growth_indicators": hardware_intel.get('growth_indicators', [])[:3], 
                "technical_pain_points": hardware_intel.get('technical_pain_points', [])[:3],
                "tech_stack": hardware_intel.get('tech_stack', [])[:5],
                "hardware_opportunities": hardware_intel.get('hardware_opportunities', [])[:3],
                "urgency_signals": hardware_intel.get('urgency_signals', [])[:2],
                "company_scale": hardware_intel.get('company_scale', [])[:2],
                "budget_indicators": hardware_intel.get('budget_indicators', [])[:2],
                "business_context": hardware_intel.get('business_context', [])[:2],
                "industry_context": hardware_intel.get('industry_context', [])[:2],
                "content_preview": hardware_intel.get('content_preview', '')[:300],
                "scraping_success": hardware_intel.get('scraping_success', False)
            })
        
        # Add relevant keywords from raw data
        raw_data = company.get('raw_data', {})
        if raw_data:
            keywords = raw_data.get('keywords', [])
            # Filter for technology-related keywords
            tech_keywords = [k for k in keywords if any(tech in k.lower() for tech in 
                           ['software', 'development', 'technology', 'cloud', 'server', 
                            'programming', 'web', 'mobile', 'data', 'ai', 'machine learning'])]
            ai_ready_data['key_technologies'] = tech_keywords[:8]
        
        return json.dumps(ai_ready_data, indent=2)

    def generate_emails_for_company(self, company: Dict, max_retries: int = 2) -> Dict:
        """
        Generate 5 personalized emails for a single company
        
        Args:
            company (Dict): Company data
            max_retries (int): Maximum number of API call retries
            
        Returns:
            Dict: Generated emails with metadata
        """
        company_name = company.get('name', 'Unknown Company')
        print(f" Generating 5 personalized emails for: {company_name}")
        
        # Prepare company data for AI
        formatted_company_data = self.prepare_company_for_ai(company)
        
        # Create the full prompt
        full_prompt = self.email_prompt_template.format(
            company_data=formatted_company_data
        )
        
        # Attempt email generation with retries
        for attempt in range(max_retries + 1):
            try:
                print(f"    API call attempt {attempt + 1}...")
                
                # Make API call to DeepSeek R1
                completion = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": self.site_url,
                        "X-Title": self.site_name,
                    },
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                # Extract and parse response
                ai_response = completion.choices[0].message.content
                
                # Parse JSON from AI response
                emails = self._parse_ai_response(ai_response)
                
                if emails and len(emails) == 5:
                    print(f"    Successfully generated 5 emails for {company_name}")
                    
                    return {
                        "company": company,
                        "emails": emails,
                        "generation_timestamp": datetime.now().isoformat(),
                        "ai_model": self.model,
                        "success": True,
                        "error": None
                    }
                else:
                    print(f"    AI generated {len(emails) if emails else 0} emails instead of 5")
                    if attempt < max_retries:
                        time.sleep(2)  # Brief delay before retry
                        continue
                        
            except Exception as e:
                print(f"    API call failed: {str(e)}")
                if attempt < max_retries:
                    time.sleep(3)  # Longer delay on error
                    continue
                else:
                    return {
                        "company": company,
                        "emails": [],
                        "generation_timestamp": datetime.now().isoformat(),
                        "ai_model": self.model,
                        "success": False,
                        "error": str(e)
                    }
        
        # If we reach here, all attempts failed
        return {
            "company": company,
            "emails": [],
            "generation_timestamp": datetime.now().isoformat(),
            "ai_model": self.model,
            "success": False,
            "error": "All generation attempts failed"
        }

    def _parse_ai_response(self, ai_response: str) -> List[Dict]:
        """
        Parse AI response and extract email data
        
        Args:
            ai_response (str): Raw AI response
            
        Returns:
            List[Dict]: Parsed email data
        """
        try:
            # Find JSON array in the response
            json_match = re.search(r'\[[\s\S]*\]', ai_response)
            if json_match:
                json_str = json_match.group(0)
                emails = json.loads(json_str)
                
                # Validate email structure
                valid_emails = []
                for email in emails:
                    if (isinstance(email, dict) and 
                        'subject_line' in email and 
                        'email_body' in email):
                        valid_emails.append(email)
                
                return valid_emails
            else:
                print("   ⚠️ No valid JSON array found in AI response")
                return []
                
        except json.JSONDecodeError as e:
            print(f"    JSON parsing error: {str(e)}")
            return []
        except Exception as e:
            print(f"    Response parsing error: {str(e)}")
            return []

    def generate_emails_for_all_companies(self, companies: List[Dict], 
                                        delay_between_calls: float = 1.0) -> List[Dict]:
        """
        Generate emails for all companies with rate limiting
        
        Args:
            companies (List[Dict]): List of company data
            delay_between_calls (float): Delay between API calls in seconds
            
        Returns:
            List[Dict]: Results for all companies
        """
        print(f" Starting email generation for {len(companies)} companies")
        print(f"⏱ Using {delay_between_calls}s delay between API calls")
        print("=" * 70)
        
        all_results = []
        successful_generations = 0
        
        for i, company in enumerate(companies, 1):
            print(f"\n Company {i}/{len(companies)}")
            
            # Generate emails for this company
            result = self.generate_emails_for_company(company)
            all_results.append(result)
            
            if result['success']:
                successful_generations += 1
            
            # Rate limiting delay (except for last company)
            if i < len(companies):
                time.sleep(delay_between_calls)
        
        print(f"\n EMAIL GENERATION COMPLETE!")
        print(f" Successful: {successful_generations}/{len(companies)} companies")
        print(f" Total emails generated: {successful_generations * 5}")
        
        return all_results

    def save_generated_emails(self, results: List[Dict], output_filename: str = "generated_emails") -> None:
        """
        Save generated emails to files in multiple formats
        
        Args:
            results (List[Dict]): Email generation results
            output_filename (str): Base filename for output
        """
        try:
            # Save detailed JSON
            json_filename = f"{output_filename}_detailed.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f" Detailed results saved to {json_filename}")
            
            # Save readable format
            readable_filename = f"{output_filename}_readable.txt"
            self._save_readable_format(results, readable_filename)
            
            # Save CSV summary
            csv_filename = f"{output_filename}_summary.csv"
            self._save_csv_summary(results, csv_filename)
            
            # Save successful emails only
            successful_results = [r for r in results if r['success']]
            if successful_results:
                success_filename = f"{output_filename}_successful.json"
                with open(success_filename, 'w', encoding='utf-8') as f:
                    json.dump(successful_results, f, indent=2, ensure_ascii=False)
                print(f" Successful emails saved to {success_filename}")
            
        except Exception as e:
            print(f" Error saving results: {str(e)}")

    def _save_readable_format(self, results: List[Dict], filename: str) -> None:
        """Save emails in human-readable format"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("HARDWARE STORE LEAD GENERATION - PERSONALIZED EMAILS\n")
                f.write("=" * 70 + "\n\n")
                
                for i, result in enumerate(results, 1):
                    company = result['company']
                    f.write(f"COMPANY #{i}: {company.get('name', 'Unknown')}\n")
                    f.write(f"Website: {company.get('website', 'N/A')}\n")
                    f.write(f"Industry: {company.get('industry', 'N/A')}\n")
                    f.write(f"Employees: {company.get('employee_count', 'N/A')}\n")
                    f.write(f"Generation Success: {result['success']}\n")
                    
                    if result['success']:
                        f.write(f"Generated: {len(result['emails'])} emails\n")
                        f.write("-" * 50 + "\n")
                        
                        for j, email in enumerate(result['emails'], 1):
                            f.write(f"\nEMAIL VARIATION #{j}:\n")
                            f.write(f"Subject: {email.get('subject_line', 'N/A')}\n")
                            f.write(f"Focus: {email.get('hardware_focus', 'N/A')}\n\n")
                            f.write(f"{email.get('email_body', 'N/A')}\n")
                            if email.get('personalization_notes'):
                                f.write(f"\nPersonalization: {email['personalization_notes']}\n")
                            f.write("-" * 30 + "\n")
                    else:
                        f.write(f"Error: {result.get('error', 'Unknown error')}\n")
                    
                    f.write("\n" + "=" * 70 + "\n\n")
            
            print(f" Readable format saved to {filename}")
            
        except Exception as e:
            print(f" Error saving readable format: {str(e)}")

    def _save_csv_summary(self, results: List[Dict], filename: str) -> None:
        """Save CSV summary of email generation"""
        try:
            import pandas as pd
            
            csv_data = []
            for result in results:
                company = result['company']
                
                # Count emails by focus area
                email_focuses = []
                if result['success'] and result['emails']:
                    email_focuses = [email.get('hardware_focus', 'General') for email in result['emails']]
                
                csv_data.append({
                    'Company Name': company.get('name', ''),
                    'Website': company.get('website', ''),
                    'Industry': company.get('industry', ''),
                    'Employee Count': company.get('employee_count', 0),
                    'Hardware Readiness Score': company.get('hardware_intelligence', {}).get('hardware_readiness_score', 0),
                    'Generation Success': result['success'],
                    'Emails Generated': len(result.get('emails', [])),
                    'Hardware Focus Areas': ' | '.join(set(email_focuses)) if email_focuses else '',
                    'Generation Error': result.get('error', '') if not result['success'] else '',
                    'Generation Timestamp': result.get('generation_timestamp', '')
                })
            
            df = pd.DataFrame(csv_data)
            df.to_csv(filename, index=False)
            print(f" CSV summary saved to {filename}")
            
        except ImportError:
            print(" pandas not available, skipping CSV export")
        except Exception as e:
            print(f" CSV export failed: {str(e)}")

    def display_generation_summary(self, results: List[Dict]) -> None:
        """Display summary of email generation results"""
        total_companies = len(results)
        successful = sum(1 for r in results if r['success'])
        total_emails = sum(len(r.get('emails', [])) for r in results)
        
        print(f"\n EMAIL GENERATION SUMMARY")
        print("=" * 50)
        print(f" Total Companies: {total_companies}")
        print(f" Successful Generations: {successful}")
        print(f" Failed Generations: {total_companies - successful}")
        print(f" Total Emails Generated: {total_emails}")
        print(f" Success Rate: {(successful/total_companies*100):.1f}%")
        
        if successful > 0:
            print(f" Average Emails per Success: {total_emails/successful:.1f}")
        
        # Show sample subjects from successful generations
        sample_subjects = []
        for result in results[:3]:  # First 3 successful results
            if result['success'] and result['emails']:
                for email in result['emails'][:2]:  # First 2 emails per company
                    subject = email.get('subject_line', '')
                    if subject:
                        sample_subjects.append(f"{result['company']['name']}: '{subject}'")
        
        if sample_subjects:
            print(f"\n Sample Subject Lines:")
            for subject in sample_subjects[:5]:
                print(f"    {subject}")

    def get_best_emails_by_score(self, results: List[Dict], min_score: int = 30) -> List[Dict]:
        """
        Get best email results based on company hardware readiness score
        
        Args:
            results (List[Dict]): All generation results
            min_score (int): Minimum hardware readiness score
            
        Returns:
            List[Dict]: Filtered and sorted results
        """
        # Filter by hardware readiness score and successful generation
        qualified_results = []
        for result in results:
            if (result['success'] and 
                result['company'].get('hardware_intelligence', {}).get('hardware_readiness_score', 0) >= min_score):
                qualified_results.append(result)
        
        # Sort by hardware readiness score (descending)
        qualified_results.sort(
            key=lambda x: x['company'].get('hardware_intelligence', {}).get('hardware_readiness_score', 0),
            reverse=True
        )
        
        return qualified_results


# Main execution function for hardware store lead email generation
def generate_hardware_emails_from_json(json_file_path: str, 
                                      openrouter_api_key: str,
                                      site_url: str = "hardware-leads-generator",
                                      site_name: str = "Hardware Sales Assistant",
                                      delay_between_calls: float = 1.5) -> List[Dict]:
    """
    Complete pipeline to generate personalized hardware store emails from JSON lead data
    
    Args:
        json_file_path (str): Path to JSON file with company data
        openrouter_api_key (str): OpenRouter API key
        site_url (str): Site URL for OpenRouter
        site_name (str): Site name for OpenRouter
        delay_between_calls (float): Delay between API calls
        
    Returns:
        List[Dict]: Email generation results
    """
    print(" HARDWARE STORE EMAIL GENERATION PIPELINE")
    print("=" * 60)
    
    # Initialize generator
    generator = HardwareLeadMessageGenerator(
        api_key=openrouter_api_key,
        site_url=site_url,
        site_name=site_name
    )
    
    # Load company data
    companies = generator.load_company_data(json_file_path)
    if not companies:
        print(" No companies loaded. Exiting.")
        return []
    
    # Generate emails for all companies
    results = generator.generate_emails_for_all_companies(
        companies, 
        delay_between_calls=delay_between_calls
    )
    
    # Save results
    generator.save_generated_emails(results, "hardware_store_emails")
    
    # Display summary
    generator.display_generation_summary(results)
    
    # Show best prospects
    best_results = generator.get_best_emails_by_score(results, min_score=20)
    if best_results:
        print(f"\n TOP {len(best_results)} HIGH-POTENTIAL PROSPECTS:")
        for i, result in enumerate(best_results[:5], 1):
            score = result['company'].get('hardware_intelligence', {}).get('hardware_readiness_score', 0)
            company_name = result['company'].get('name', 'Unknown')
            print(f"   {i}. {company_name} (Score: {score}/100, {len(result['emails'])} emails)")
    
    print(f"\n Email generation pipeline completed successfully!")
    print(f" Check generated files for results")
    
    return results


# Quick test function
def test_email_generation(openrouter_api_key: str, sample_company: Dict = None):
    """
    Test email generation with a single company
    
    Args:
        openrouter_api_key (str): OpenRouter API key
        sample_company (Dict): Optional sample company data
    """
    print(" TESTING EMAIL GENERATION")
    print("=" * 40)
    
    if not sample_company:
        # Use sample from your data
        sample_company = {
            "name": "JavaScript Mastery",
            "website": "http://www.jsmastery.com",
            "industry": "e-learning",
            "employee_count": 70,
            "founded_year": 2019,
            "hardware_intelligence": {
                "hardware_readiness_score": 35,
                "tech_stack": ["javascript", "reactjs", "nodejs"],
                "growth_indicators": ["expanding team", "online platform"],
                "technical_pain_points": ["content delivery", "user experience"],
                "scraping_success": True
            }
        }
    
    # Initialize generator
    generator = HardwareLeadMessageGenerator(api_key=openrouter_api_key)
    
    # Generate emails for sample company
    result = generator.generate_emails_for_company(sample_company)
    
    # Display results
    if result['success']:
        print(f" Generated {len(result['emails'])} emails for {sample_company['name']}")
        for i, email in enumerate(result['emails'], 1):
            print(f"\nEmail {i}:")
            print(f"Subject: {email.get('subject_line', 'N/A')}")
            print(f"Focus: {email.get('hardware_focus', 'N/A')}")
            print(f"Body: {email.get('email_body', 'N/A')[:100]}...")
    else:
        print(f" Generation failed: {result.get('error', 'Unknown error')}")
    
    return result


print(" Hardware Store Email Generation System loaded successfully!")
print("\n READY FOR AI-POWERED EMAIL GENERATION!")
print("\n USAGE:")
print(" results = generate_hardware_emails_from_json('your_leads.json', 'your_api_key')")
print(" test_result = test_email_generation('your_api_key')")
print(" generator = HardwareLeadMessageGenerator('your_api_key')")
print("\n This system will:")
print("   • Generate 5 unique emails per company")
print("   • Personalize based on company intelligence") 
print("   • Focus on relevant hardware solutions")
print("   • Maintain professional B2B tone")
print("   • Save results in multiple formats")
print("   • Provide detailed analytics")