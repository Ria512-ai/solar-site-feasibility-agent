# Solar Feasibility Assessment App

AI-powered solar site feasibility assessment using CrewAI agents.

## Quick Start

1. **Clone and setup**:
```bash
git clone <repo-url>
cd solar-feasibility-app
cp .env.example .env
```

2. **Add API keys to .env**:
```bash
NEWS_API_TOKEN=your_news_api_token
OPENAI_API_KEY=your_openai_api_key
```

3. **Run with Docker**:
```bash
docker-compose up --build
```

## Usage

The app assesses solar feasibility by analyzing:
- Permitting requirements and costs
- Local regulations and restrictions
- News impact on solar development

Default test runs assessment for Los Angeles address with 7kW system.

## API Keys Required

- **OpenAI API**: For CrewAI agents
- **NewsAPI**: For regulatory research (thenewsapi.com)