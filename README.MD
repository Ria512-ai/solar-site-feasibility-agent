# Solar Feasibility Assessment App

AI-powered solar site feasibility assessment using CrewAI agents.

## How to Run

1. **Clone and setup**:
```bash
git clone <repo-url>
cd solar-site-feasibility-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


```

2. **Add API keys to .env**:
```bash
export NEWS_API_TOKEN="your_token"
export OPENAI_API_KEY="your_key"
export OPENAI_MODEL_NAME="gpt-4o-mini"

```

3. **Run with python3.10.13 **:
```
python3 main.py

```

## Agents Implemented

### 1. Solar Permitting Specialist Agent
**Why**: Solar projects require complex permitting across different jurisdictions with varying requirements, fees, and timelines.

**Capabilities**:
- Classifies jurisdiction based on address (Los Angeles, San Francisco, or generic California)
- Retrieves jurisdiction-specific permit requirements and fees
- Auto-generates permit application forms with system specifications
- Provides processing timelines and next steps

**Tools**:
- `classify_jurisdiction_tool`: Maps addresses to permitting jurisdictions
- `generate_permit_form_tool`: Creates filled permit applications

### 2. Solar Site Feasibility Research Specialist Agent  
**Why**: Local regulations, moratoriums, and policy changes significantly impact solar project viability.

**Capabilities**:
- Searches news APIs for solar-related regulatory changes
- Identifies moratoriums, restrictions, and policy updates
- Analyzes local solar incentive programs
- Assesses utility interconnection issues

**Tools**:
- `site_impact_research_tool`: Performs targeted news searches for solar development impacts

### 3. Feasibility Scoring System
**Why**: Combines both agents' outputs into actionable Go/No-Go decisions.

**Capabilities**:
- Calculates weighted feasibility scores (60% permitting, 40% research)
- Provides risk assessment (Low/Medium/High)
- Generates final recommendations with justification

## Known Limitations & Shortcuts

### Time Constraints
1. **Limited Jurisdiction Coverage**: Only implements 3 jurisdictions (LA, SF, generic CA) vs. hundreds of real jurisdictions
2. **Mock Permitting Data**: Uses hardcoded permit requirements instead of live government API integration
3. **Simple Address Parsing**: Basic string matching for jurisdiction classification vs. geocoding APIs
4. **No Database**: All data stored in memory, no persistence layer

### API Limitations
1. **News API Dependency**: Requires external NewsAPI token, may hit rate limits
2. **No Real-time Data**: Permit data is static mock data from 2024
3. **OpenAI Model Dependency**: Requires OpenAI API access, costs money per request

### Scoring Simplifications  
1. **Basic Scoring Logic**: Simple linear formulas vs. complex machine learning models
2. **Limited Risk Factors**: Only considers fees, timing, and article count vs. comprehensive risk analysis
3. **No Historical Data**: No trend analysis or seasonal considerations

### Production Readiness
1. **No Error Recovery**: Limited retry logic for API failures
2. **No Authentication**: Web API has no security layer
3. **No Monitoring**: No logging, metrics, or health monitoring
4. **No Testing**: No unit tests or integration tests implemented

### Future Improvements
- Integrate real government permitting APIs
- Add geocoding for accurate jurisdiction mapping  
- Implement machine learning for better feasibility scoring
- Add database for permit tracking and historical analysis
- Include weather data, roof analysis, and utility rate integration

## API Keys Required

- **OpenAI API**: For CrewAI agents
- **NewsAPI**: For regulatory research (thenewsapi.com)
