#!/usr/bin/env python
# coding: utf-8

import json
import os
import http.client
import urllib.parse
from crewai import Agent, Task, Crew
from crewai_tools import tool
from typing import Dict, Any

# Set defaults if not provided via environment
os.environ.setdefault('NEWS_API_TOKEN', '')
os.environ.setdefault('base_url', 'api.thenewsapi.com')
os.environ.setdefault('OPENAI_MODEL_NAME', 'gpt-4o-mini')

# ============================================================================
# RESEARCH AGENT 
# ============================================================================

def _perform_news_search(search_terms: str, api_token: str, base_url: str) -> list:
    conn = http.client.HTTPSConnection(base_url)

    params = urllib.parse.urlencode({
        'api_token': api_token,
        'search': search_terms,
        'limit': 10,
        'locale': 'us,ca'
    })

    try:
        conn.request('GET', f'/v1/news/all?{params}')
        response = conn.getresponse()
        data = response.read()
        result = json.loads(data.decode('utf-8'))
        return result.get('data', [])
    except Exception as e:
        print(f"Error searching news: {e}")
        return []
    finally:
        conn.close()

@tool
def site_impact_research_tool(location: str = None) -> str:
    """Researches news articles for moratoriums, environmental restrictions, and site development impacts using news API."""
    
    api_token = os.environ.get('NEWS_API_TOKEN')
    base_url = 'api.thenewsapi.com'

    if not api_token:
        return "Error: NEWS_API_TOKEN environment variable not set"
    
    search_terms_list = [
        'solar development moratorium',
        'solar project restriction', 
        'renewable energy policy',
        'solar zoning restriction',
        'solar panel installation ban',
        'solar incentive program',
        'solar permit requirement',
        'utility interconnection solar'
    ]
            
    if location:
        search_terms_list = [f"{term} {location}" for term in search_terms_list]
    
    all_articles = []
    
    for term in search_terms_list:
        articles = _perform_news_search(term, api_token, base_url)
        all_articles.extend(articles)
    
    unique_articles = []
    seen_titles = set()
    
    for article in all_articles:
        title = article.get('title', '')
        if title not in seen_titles and title:
            seen_titles.add(title)
            unique_articles.append(article)
    
    return json.dumps({
        'total_articles': len(unique_articles),
        'articles': unique_articles[:10],
        'search_location': location or 'General'
    })

research_agent = Agent(
    role="Solar Site Feasibility Research Specialist",
    goal="Research and assess site feasibility for solar project development",
    backstory="You analyze regulatory environment for solar projects",
    allow_delegation=False,
    verbose=True,
    tools=[site_impact_research_tool]
)

# ============================================================================
# PERMITTING AGENT
# ============================================================================

JURISDICTION_RULES = {
    "los_angeles": {
        "jurisdiction_name": "City of Los Angeles",
        "permit_type": "Solar Installation Permit",
        "requirements": [
            "Site plan with solar array layout",
            "Electrical single-line diagram", 
            "Structural calculations",
            "Interconnection application",
            "LADBS permit application"
        ],
        "fees": 500,
        "processing_time": "4-6 weeks",
        "contact": "ladbs.lacity.org"
    },
    "san_francisco": {
        "jurisdiction_name": "City of San Francisco",
        "permit_type": "Solar Photovoltaic System Permit",
        "requirements": [
            "Solar system plans and specifications",
            "Electrical permit application",
            "Building permit (if roof modifications)",
            "Fire department clearance form",
            "Utility interconnection agreement"
        ],
        "fees": 750,
        "processing_time": "3-4 weeks", 
        "contact": "sfdbi.org"
    },
    "california_default": {
        "jurisdiction_name": "California County (Generic)",
        "permit_type": "Residential Solar Permit",
        "requirements": [
            "Solar system design plans",
            "Electrical diagram",
            "Building department application",
            "Utility notification form"
        ],
        "fees": 300,
        "processing_time": "2-4 weeks",
        "contact": "Local building department"
    }
}

PERMIT_TEMPLATE = {
    "applicant_name": "",
    "property_address": "",
    "jurisdiction": "",
    "permit_type": "",
    "system_size_kw": "",
    "panel_count": "",
    "inverter_type": "",
    "installation_company": "",
    "contractor_license": "",
    "estimated_cost": "",
    "requirements_checklist": [],
    "fees": 0,
    "processing_time": "",
    "submission_date": "",
    "status": "Draft"
}

@tool
def classify_jurisdiction_tool(address: str) -> str:
    """Classifies the jurisdiction based on address and returns permitting rules as a JSON string."""
    
    address_lower = address.lower()
    
    if "los angeles" in address_lower or "la" in address_lower:
        jurisdiction = "los_angeles"
    elif "san francisco" in address_lower or "sf" in address_lower:
        jurisdiction = "san_francisco"  
    else:
        jurisdiction = "california_default"
    
    rules = JURISDICTION_RULES[jurisdiction]
    
    return json.dumps({
        "address": address,
        "classified_jurisdiction": jurisdiction,
        "jurisdiction_info": rules
    })

@tool 
def generate_permit_form_tool(address: str, jurisdiction_data: str, system_details: str = "") -> str:
    """Generates a filled permit form based on jurisdiction rules and system details."""
    
    def _extract_json_from_text(text: str) -> dict:
        text = text.strip()
        if text.startswith('```json') and text.endswith('```'):
            text = text[len('```json'):-len('```')].strip()
        elif text.startswith('```') and text.endswith('```'):
            text = text[len('```'):-len('```')].strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"DEBUG: Failed to decode JSON from '{text[:100]}...' Error: {e}")
            return {}
    
    jurisdiction_info = _extract_json_from_text(jurisdiction_data)
    
    if not jurisdiction_info or "jurisdiction_info" not in jurisdiction_info:
        return "Error: Invalid or unparseable jurisdiction data provided to generate_permit_form_tool."
    
    rules = jurisdiction_info["jurisdiction_info"]
    permit_form = PERMIT_TEMPLATE.copy()
    
    permit_form["property_address"] = address
    permit_form["jurisdiction"] = rules["jurisdiction_name"]
    permit_form["permit_type"] = rules["permit_type"]
    permit_form["requirements_checklist"] = rules["requirements"]
    permit_form["fees"] = rules["fees"]
    permit_form["processing_time"] = rules["processing_time"]
    permit_form["submission_date"] = "2024-07-18"
    
    if system_details:
        details = _extract_json_from_text(system_details) 
        permit_form.update({k: v for k, v in details.items() if k in permit_form})
    
    return json.dumps({
        "permit_form": permit_form,
        "jurisdiction_contact": rules["contact"],
        "next_steps": [
            "Complete all required documents",
            f"Pay permit fee of ${rules['fees']}",
            "Submit application to jurisdiction",
            f"Wait {rules['processing_time']} for approval"
        ]
    })

permitting_agent = Agent(
    role="Solar Permitting Specialist",
    goal="Process addresses to classify jurisdictions and generate accurate solar permit applications",
    backstory="""You are an expert in solar permitting across California jurisdictions. 
    You know the specific requirements, forms, and processes for each city and county.
    You excel at auto-filling permit applications with accurate information.""",
    allow_delegation=False,
    verbose=True,
    tools=[classify_jurisdiction_tool, generate_permit_form_tool]
)

def create_permitting_task(address: str, system_size: str = "5kW", panel_count: str = "20"):
    system_details_json_str = json.dumps({
        "system_size_kw": system_size,
        "panel_count": panel_count,
        "estimated_cost": "$0",
        "inverter_type": "Unknown"
    })

    return Task(
        description=f'''
        For the solar permit application at the address: {address}
        
        **Your plan:**
        1. Use `classify_jurisdiction_tool` with the address "{address}" to determine the jurisdiction.
           **Important:** Extract only the pure JSON output from this tool's response.
        2. Then, use `generate_permit_form_tool` with the original address,
           the **exact JSON string output from `classify_jurisdiction_tool`** as the `jurisdiction_data` argument,
           and the following system details as the `system_details` argument: `{system_details_json_str}`.
        
        **Your final output MUST be a JSON object containing the complete solar permit package.**
        ''',
        
        expected_output=f'''Complete solar permit package in JSON format for {address}, including:
        1. Jurisdiction classification
        2. Fully filled permit application form
        3. Requirements checklist for that jurisdiction
        4. Fee information and processing timeline
        5. Contact information for the permit office
        6. Next steps for permit submission
        7. All boilerplate fields auto-filled (e.g., applicant_name, installation_company, contractor_license)''',
        
        agent=permitting_agent
    )

def create_permitting_crew(address: str, system_size: str = "5kW", panel_count: str = "20"):
    task = create_permitting_task(address, system_size, panel_count)
    
    crew = Crew(
        agents=[permitting_agent],
        tasks=[task],
        verbose=True
    )
    
    return crew

# ============================================================================
# FEASIBILITY SYSTEM - COMBINES BOTH AGENTS
# ============================================================================

def get_crew_answer(crew_result):
    """Extract answer from crew result"""
    try:
        if hasattr(crew_result, 'raw') and crew_result.raw:
            if isinstance(crew_result.raw, dict):
                return crew_result.raw
            return json.loads(crew_result.raw)
        elif hasattr(crew_result, 'tasks_output') and crew_result.tasks_output:
            last_task_output = crew_result.tasks_output[-1].result
            return json.loads(last_task_output)
        return str(crew_result)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from crew result: {e}")
        return str(crew_result)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return str(crew_result)

def extract_location_from_address(address: str) -> str:
    """Simple function to extract location for research"""
    address_lower = address.lower()
    
    if "los angeles" in address_lower or "la" in address_lower:
        return "Los Angeles California"
    elif "san francisco" in address_lower or "sf" in address_lower:
        return "San Francisco California"  
    else:
        return "California"

def calculate_feasibility_score(permitting_data: dict, research_data: dict) -> dict:
    """Calculate overall feasibility score from both agents' results"""
    
    try:
        if isinstance(permitting_data, str):
            permitting_data = json.loads(permitting_data)
        
        fees = 500
        processing_weeks = 4
        
        if 'permit_form' in permitting_data:
            permit_form = permitting_data['permit_form']
            fees = permit_form.get('fees', 500)
            processing_time = permit_form.get('processing_time', '4 weeks')
            if 'week' in processing_time:
                processing_weeks = int(processing_time.split('-')[0])
        
        permit_score = max(0, 100 - (fees / 10) - (processing_weeks * 5))
        
    except:
        permit_score = 60
    
    try:
        if isinstance(research_data, str):
            research_data = json.loads(research_data)
        
        total_articles = research_data.get('total_articles', 0)
        research_score = max(20, min(80, 70 - (total_articles * 2)))
        
    except:
        research_score = 60
    
    overall_score = (permit_score * 0.6) + (research_score * 0.4)
    
    if overall_score >= 70:
        decision = "GO"
        risk_level = "Low"
    elif overall_score >= 50:
        decision = "CONDITIONAL GO"  
        risk_level = "Medium"
    else:
        decision = "NO-GO"
        risk_level = "High"
    
    return {
        "overall_score": round(overall_score, 1),
        "decision": decision,
        "risk_level": risk_level,
        "permit_score": round(permit_score, 1),
        "research_score": round(research_score, 1),
        "fees": fees,
        "processing_weeks": processing_weeks
    }

def assess_solar_site_feasibility(address: str, system_size: str = "5kW", panel_count: str = "20") -> dict:
    """
    Main function: Assess overall solar site feasibility
    Uses both existing agents and returns Go/No-Go decision
    """
    
    print(f"\n🔍 SOLAR FEASIBILITY ASSESSMENT")
    print(f"Address: {address}")
    print(f"System: {system_size}, {panel_count} panels")
    print("="*50)
    
    # Step 1: Run Permitting Agent
    print("⚡ Running Permitting Analysis...")
    
    permitting_crew = create_permitting_crew(address, system_size, panel_count)
    permitting_result = permitting_crew.kickoff()
    permitting_data = get_crew_answer(permitting_result)
    
    # Step 2: Run Research Agent
    print("🔍 Running Site Research Analysis...")
    
    location = extract_location_from_address(address)
    
    research_task = Task(
        description=f'''Research solar development feasibility for a specific site in {location}.
        
        Use the Site Impact News Research Tool with location parameter "{location}" to:
        1. Search for recent solar development moratoriums in the area
        2. Identify area-specific solar and renewable energy restrictions
        3. Find headlines affecting solar project development
        4. Research solar incentives and net metering policies
        5. Check for utility interconnection issues or solar permitting delays
        
        Provide analysis specific to the area's solar regulatory environment.''',
        
        expected_output=f'''Solar site feasibility analysis including:
        1. Solar regulatory environment assessment
        2. Local solar moratoriums or restrictions identified  
        3. Solar incentives and policies found
        4. Environmental factors affecting solar development
        5. Risk assessment for solar projects in {location}''',
        
        agent=research_agent
    )
    
    research_crew = Crew(
        agents=[research_agent], 
        tasks=[research_task],
        verbose=False
    )
    
    research_result = research_crew.kickoff()
    research_data = get_crew_answer(research_result)
    
    # Step 3: Calculate Final Feasibility
    print("📊 Calculating Final Feasibility Score...")
    
    feasibility = calculate_feasibility_score(permitting_data, research_data)
    
    # Step 4: Generate Final Report
    final_report = {
        "address": address,
        "system_specs": f"{system_size} system, {panel_count} panels",
        "assessment_date": "2024-07-18",
        "feasibility_score": feasibility["overall_score"],
        "decision": feasibility["decision"],
        "risk_level": feasibility["risk_level"],
        "breakdown": {
            "permitting_score": feasibility["permit_score"],
            "research_score": feasibility["research_score"]
        },
        "key_factors": {
            "estimated_fees": f"${feasibility['fees']}",
            "processing_time": f"{feasibility['processing_weeks']} weeks",
            "location_research": location
        },
        "justification": f"""
        DECISION: {feasibility['decision']}
        
        Reasoning:
        • Permitting Score: {feasibility['permit_score']}/100 (fees: ${feasibility['fees']}, time: {feasibility['processing_weeks']} weeks)
        • Research Score: {feasibility['research_score']}/100 (regulatory environment analysis)
        • Overall Score: {feasibility['overall_score']}/100
        
        Risk Level: {feasibility['risk_level']}
        """.strip(),
        "raw_permitting_data": permitting_data,
        "raw_research_data": research_data
    }
    
    return final_report

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    test_address = "8770 W Olympic Blvd, Los Angeles, California 90035"
    
    result = assess_solar_site_feasibility(
        address=test_address,
        system_size="7kW", 
        panel_count="24"
    )
    
    print("\n" + "="*60)
    print("🎯 FINAL FEASIBILITY REPORT")
    print("="*60)
    print(f"Address: {result['address']}")
    print(f"System: {result['system_specs']}")
    print(f"Overall Score: {result['feasibility_score']}/100")
    print(f"Decision: {result['decision']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"\nJustification:")
    print(result['justification'])
    print("="*60)