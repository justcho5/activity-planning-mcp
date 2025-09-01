# Activity Planning MCP Server

An intelligent activity planning agent that helps users discover events and places, then seamlessly add them to their calendar. Built as an MCP (Model Context Protocol) server that integrates with Ticketmaster and Google Places APIs.

## Overview

This MCP server acts as an intelligent agent for activity planning, combining event discovery with place recommendations to create complete activity suggestions. It can be used through ChatGPT, Claude, GitHub Copilot, or any MCP-compatible interface.

## Features

- **Event Discovery**: Search for concerts, sports, theater, and other events via Ticketmaster API
- **Place Recommendations**: Find restaurants, parks, museums, and attractions using Google Places API
- **Calendar Integration**: Generate pre-filled Google Calendar URLs for easy event creation
- **Filtering**: Filter by date ranges, ratings, price levels, and keywords
- **Location Flexibility**: Support for both addresses and coordinates with automatic geocoding

## Installation

1. Clone the repository:
```bash
git clone https://github.com/justcho5/activity-planning-mcp.git
cd activity-planning-mcp
```

2. Install dependencies using uv:
```bash
uv sync
source .venv/bin/activate
```

3. Set up API keys:
```bash
# Create .env file
echo "TICKETMASTER_API_KEY=your_ticketmaster_key" >> .env
echo "GOOGLE_PLACES_API_KEY=your_google_places_key" >> .env
```

4. Get API Keys:
   - Ticketmaster: https://developer.ticketmaster.com/
   - Google Places: https://developers.google.com/places/web-service/get-api-key

## Usage

### Using the Deployed Server

The MCP server is deployed at: `https://sudden-aardvark.fastmcp.app/mcp`

Add to MCP client configuration:

```json
{
  "mcpServers": {
    "activity-planning-mcp": {
      "httpUrl": "https://sudden-aardvark.fastmcp.app/mcp"
    }
  }
}
```

### Running Locally for Development

For development with MCP Inspector:
```bash
fastmcp dev main.py
```

## Architecture

```
        ┌─────────────┐     ┌──────────────┐     ┌────────────────┐
        │   MCP       │◄───▶│   FastMCP    │◄───▶│  External APIs │
        │   Client    │     │   Server     │     │                │
        │ (Claude,    │     │              │     │ • Ticketmaster │
        │  ChatGPT)   │     │  Tools:      │     │ • Google Places│
        └─────────────┘     │  • Events    │     │ • Geocoding    │
                            │  • Places    │     └────────────────┘
                            │  • Calendar  │
                            └──────────────┘
```

## Considerations

### How would you test the agent, what are the different failure scenarios, and what tools or methods would you use to manage them?

1. **In-Memory Testing with FastMCP Client**
   - Imports the server object directly into tests
   - Test tool calls
   - No deployment or network overhead required
   - Instant test execution
1. **Unit Tests**: 
   - Test individual functions with mocked API responses
   - `pytest` test framework and `unittest.mock` to mock external dep.
2. **Workflow Tests**: 
   - Test complete user workflows (events → places → calendar)
4. **Failure Scenarios**:
   - API rate limiting
   - Invalid API keys
   - Network timeouts
   - Malformed responses
   - Invalid user inputs

### What are the security considerations of your agent and what are potential ways to defend against them?

**Current Implementation**:
- API keys stored as environment variables using `pydantic.SecretStr`
- Input validation for all user inputs
- Opted to make gcal links instead of writing to Google calendar to mitigate security concerns around writing to external services.

**Security Risks & Mitigations**:

1. **API Key Exposure**:
   - Risk: Keys could leak through error messages or logs
   - Mitigation: Use structured logging, sanitize all error outputs, need better error handling in general (future consideration)

2. **Agent Authorization**:
   - Risk: Unauthorized access to MCP Server and tools
   - Mitigation: Implement authentication for server access, scope tool access or require explicit user approval.

3. **Rate Limiting Abuse**:
   - Risk: Excessive API calls leading to service denial or cost overruns
   - Mitigation: Implement per-user rate limiting, use caching, add circuit breakers

### What are the performance concerns for your agent, how will it scale in throughout, response times, and supported tasks?

**Current Limitations**:
- Sequential API calls without parallelization
- No caching mechanism
- Fixed timeout values
- No connection pooling

**Scaling Strategies**:

1. **Throughput**:
   - Add Redis caching layer for frequently accessed data
   - Implement parallel API calls using `asyncio.gather()`
   - Use connection pooling with `httpx.AsyncClient`

2. **Response Times**:
   - Cache geocoding results (addresses rarely change)
   - Pre-fetch popular events and places


### Caveats & Gotchas

1. **API Limits**: Ticketmaster has strict rate limits (5000 requests/day)
2. **No Auth**: Anyone can access the MCP server and use the tools.

## Future Improvements

1. **Itinerary Export & Storage**:
   - Export itineraries to local files (PDF, Markdown, JSON)
   - Integration with Google Docs API for cloud storage
   - Share itineraries via email or messaging platforms

2. **User Preference & History Management**:
   - Database storage for user preferences and past itineraries
   - Ensure diverse recommendations by avoiding repetition
   - Learn from user feedback on recommendations
   - Preference profiles (adventurous, budget-conscious, family-friendly)
   - Have a knowledge store (like storing user preferences, past itineraries maybe in a vector db) to pull context.

4. **Advanced Features**:
   - Weather integration
   - Transportation planning
   - Budget optimization

5. **Comprehensive Testing Suite**

6. **Enhanced Caching Layer**:
   - Redis for API response caching
   - LRU cache for geocoding results

7. **Monitoring & Observability**:
   - Structured logging with context
   - Metrics collection (Prometheus)
      - how long each tool takes, api latency
      - cache hit rate
      - usage metrics
      - error and reliability metrics
      - cost tracking for api usage

## License

MIT