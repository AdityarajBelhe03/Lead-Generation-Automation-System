import streamlit as st
import re

def parse_email_data(content):
    """Parse the email content into structured data"""
    companies = []
    
    # Split by company sections
    company_blocks = content.split("======================================================================")
    
    for block in company_blocks:
        if not block.strip() or "HARDWARE STORE LEAD GENERATION" in block:
            continue
            
        lines = block.strip().split('\n')
        company_info = {}
        emails = []
        
        # Parse company header info
        for i, line in enumerate(lines):
            if line.startswith("COMPANY #"):
                company_info['name'] = line.split(': ', 1)[1] if ': ' in line else "Unknown"
            elif line.startswith("Website:"):
                company_info['website'] = line.split(': ', 1)[1]
            elif line.startswith("Industry:"):
                company_info['industry'] = line.split(': ', 1)[1]
            elif line.startswith("Employees:"):
                company_info['employees'] = line.split(': ', 1)[1]
            elif line.startswith("Generated:"):
                company_info['email_count'] = line.split(': ', 1)[1]
        
        # Parse individual emails
        email_sections = block.split("EMAIL VARIATION #")
        for section in email_sections[1:]:  # Skip first empty section
            if not section.strip():
                continue
                
            email_data = {}
            section_lines = section.strip().split('\n')
            
            # Get variation number
            if section_lines[0]:
                email_data['variation'] = section_lines[0].split(':')[0]
            
            # Parse email content
            content_started = False
            email_content = []
            
            for line in section_lines:
                if line.startswith('Subject:'):
                    email_data['subject'] = line.replace('Subject: ', '')
                elif line.startswith('Focus:'):
                    email_data['focus'] = line.replace('Focus: ', '')
                elif line.startswith('Personalization:'):
                    email_data['personalization'] = line.replace('Personalization: ', '')
                elif line.strip() == '' and not content_started:
                    continue
                elif line.startswith('Subject:') or line.startswith('Focus:'):
                    continue
                elif line.startswith('Personalization:'):
                    break
                elif line.startswith('-----'):
                    break
                else:
                    if not line.startswith('EMAIL VARIATION') and line.strip():
                        email_content.append(line)
            
            # Clean up email content
            email_data['content'] = '\n'.join(email_content).strip()
            
            if email_data.get('subject'):
                emails.append(email_data)
        
        if company_info and emails:
            company_info['emails'] = emails
            companies.append(company_info)
    
    return companies

# Load and parse the email data
@st.cache_data
def load_email_data():
    try:
        with open("hardware_store_emails_readable.txt", "r", encoding='utf-8') as file:
            content = file.read()
        return parse_email_data(content)
    except FileNotFoundError:
        st.error("Please make sure 'hardware_store_emails_readable.txt' is in your working directory")
        return []

def main():
    st.set_page_config(
        page_title="Hardware Store Email Dashboard",
        page_icon="📬",
        layout="wide"
    )
    
    st.title("📬 AI-Generated Hardware Outreach Emails")
    st.markdown("---")
    
    # Load data
    companies = load_email_data()
    
    if not companies:
        st.warning("No email data found. Please check your data file.")
        return
    
    # Sidebar for company selection
    st.sidebar.header("🏢 Select Company")
    company_names = [f"{comp['name']}" for comp in companies]
    selected_company_idx = st.sidebar.selectbox(
        "Choose a company:",
        range(len(company_names)),
        format_func=lambda x: company_names[x]
    )
    
    selected_company = companies[selected_company_idx]
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    # Company info column
    with col1:
        st.header("📊 Company Information")
        st.markdown(f"**Company:** {selected_company['name']}")
        st.markdown(f"**Industry:** {selected_company.get('industry', 'N/A')}")
        st.markdown(f"**Employees:** {selected_company.get('employees', 'N/A')}")
        st.markdown(f"**Website:** [{selected_company.get('website', 'N/A')}]({selected_company.get('website', '#')})")
        st.markdown(f"**Generated Emails:** {selected_company.get('email_count', len(selected_company['emails']))}")
        
        st.markdown("---")
        
        # Email variation selector
        st.subheader("📝 Email Variations")
        email_options = [f"Variation {email.get('variation', i+1)}: {email.get('focus', 'General')}" 
                        for i, email in enumerate(selected_company['emails'])]
        
        selected_email_idx = st.selectbox(
            "Select email variation:",
            range(len(email_options)),
            format_func=lambda x: email_options[x]
        )
    
    # Email content column
    with col2:
        st.header("✉️ Email Content")
        
        if selected_company['emails']:
            selected_email = selected_company['emails'][selected_email_idx]
            
            # Email header info
            st.subheader(f"{selected_email.get('subject', 'No Subject')}")
            
            col2a, col2b = st.columns(2)
            with col2a:
                st.markdown(f"**Focus:** {selected_email.get('focus', 'N/A')}")
            with col2b:
                st.markdown(f"**Variation:** #{selected_email.get('variation', 'N/A')}")
            
            st.markdown("---")
            
            # Email body
            st.markdown("**Email Body:**")
            st.text_area(
                "Email Content",
                value=selected_email.get('content', 'No content available'),
                height=400,
                label_visibility="collapsed"
            )
            
            # Personalization notes
            if selected_email.get('personalization'):
                st.markdown("---")
                st.markdown("**🎯 Personalization Strategy:**")
                st.info(selected_email['personalization'])
        else:
            st.warning("No emails found for this company.")
    
    # Statistics section
    st.markdown("---")
    st.header("📈 Dashboard Statistics")
    
    col3, col4, col5, col6 = st.columns(4)
    
    with col3:
        st.metric("Total Companies", len(companies))
    
    with col4:
        total_emails = sum(len(comp['emails']) for comp in companies)
        st.metric("Total Email Variations", total_emails)
    
    with col5:
        avg_emails = total_emails / len(companies) if companies else 0
        st.metric("Avg Emails per Company", f"{avg_emails:.1f}")
    
    with col6:
        industries = set(comp.get('industry', 'Unknown') for comp in companies)
        st.metric("Industries Covered", len(industries))
    
    # Additional insights
    with st.expander("📋 View All Companies Summary"):
        for comp in companies:
            st.markdown(f"**{comp['name']}** - {comp.get('industry', 'N/A')} | {comp.get('employees', 'N/A')} employees | {len(comp['emails'])} email variations")

if __name__ == "__main__":
    main()