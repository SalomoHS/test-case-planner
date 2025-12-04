# test-case-planner - Autonomous Itinerary

An AI-powered autonomous travel planning system that generates personalized itineraries using multi-agent architecture. Leverages specialized AI agents to handle hotel bookings, place recommendations, and itinerary creation based on user preferences.

**Demo Video**: [Click Here](https://drive.google.com/file/d/1PTZYXCzjE3urI9lo9Sq2J0K4LAcKbxH8/view?usp=sharing)

## Problem Definition
For Individual travelers, traditional travel planning is time-consuming, fragmented, and requires users to manually coordinate multiple services (hotel booking, attraction research, itinerary creation), leading to suboptimal travel experiences 

## Features

- **Multi-Agent Architecture**: Specialized agents for hotels, places, and itinerary planning
- **Personalized Recommendations**: Uses user profile and preferences for suggestions
- **Human-in-the-Loop**: Optional user confirmation for hotel bookings and searching hotel
- **Real-time Updates**: WebSocket-based frontend for live plan and booking updates
- **Database Integration**: Supabase for storing plans, bookings, hotels, and places data
- **Automated Invoicing**: N8N integration for sending booking confirmations through gmail

## Instructions to Use

### Prerequisites

- Python 3.11+
- Supabase account with configured database
- Google Gemini API key
- N8N webhook endpoint for invoice automation

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd test-case-planner
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:

Create a `.env` file in the root directory:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SECRET_KEY=your_supabase_secret_key
SUPABASE_ANON_KEY=your_supabase_anon_key
```

Also create `agents/.env` with:
```env
N8N_ENDPOINT=your_n8n_websocket
GEMINI_API_KEY=your_gemini_api_key
```

4. Configure user profile:

Edit `user_profile.json` with your preferences:
```json
{
  "name": "your_name",
  "email": "your_email@example.com"
  "preferences": {
    "hotel": {
      "rating": 4,
      "max_price_per_night": 1000000,
      "amenities": ["wifi", "swimming_pool"]
    },
    "attractions": {
      "categories": ["Cultural", "Historical", "Nature"]
    }
  },
  "behavioral_style": "relaxed",
  "constraints": {
    "budget": 5000000,
    "mobility": "normal"
  }
}
```

With payment method:
```json
{
  "name": "your_name",
  "email": "your_email@example.com"
  "preferences": {
    "hotel": {
      "rating": 4,
      "max_price_per_night": 1000000,
      "amenities": ["wifi", "swimming_pool"]
    },
    "attractions": {
      "categories": ["Cultural", "Historical", "Nature"]
    }
  },
  "behavioral_style": "relaxed",
  "constraints": {
    "budget": 5000000,
    "mobility": "normal"
  },
  "payment_method":{
    "method":"credit card",
    "balance": 80000000
  }
}
```


### Running the Application

#### Option 1: CLI Mode (Main Script)

1. Edit `config.py` to set your travel prompt:
```python
prompt = "I want to plan a trip to Jakarta for 1 day from 2 December 2025"
```

2. Run the main script:
```bash
python main.py
```

The agent will:
- Ask if you want to search for hotels (y/n), if yes agent will discover hotel options based on user profile
- Display hotel options and ask if you want to book (y/n), if yes agent will book the hotel and send booking invoice
- Discover place options based on user profile
- Generate a complete itinerary
- Save the plan to the database

#### Option 2: Web Interface (View your plans and bookings)

1. Start the FastAPI backend:
```bash
python backend.py
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

3. The web interface will display:
- All saved plans
- All bookings
- Real-time updates via WebSocket
  
<img width="1808" height="924" alt="image" src="https://github.com/user-attachments/assets/fd6a6808-c798-49f2-9d5a-11a5548cf840" />

## Architecture
<img width="2453" height="1641" alt="image" src="https://github.com/user-attachments/assets/e88f7237-2b7f-4ff4-aa87-ed44cd0f8d6c" />

## Approach and Steps

### Core Workflow Steps

#### 1. User Input Processing
- **Input**: Natural language travel request (e.g., "Plan a 2-day trip to Jakarta")
- **Processing**: Root agent parses destination, duration, dates. Then distribute the task to sub-agents.
- **Output**: Structured travel parameters for sub-agents

#### 2. Hotel Discovery & Booking
- **Agent**: Hotel Agent (`agent_hotel.py`)
- **Process**:
  1. Query Supabase database for hotels matching criteria (city, rating, price, facilities things)
  2. Filter results based on user preferences from `user_profile.json`
  3. Present top options to user
  4. **Human-in-the-Loop**: Request user confirmation for booking
  5. Process payment and create booking record
  6. Send invoice via N8N webhook (optional)

#### 3. Place Discovery
- **Agent**: Place Agent (`agent_place.py`)
- **Process**:
  1. Fetch tourist attractions from database by city
  2. Filter by user-preferred categories (Cultural, Historical, Nature)
  3. Consider behavioral style (relaxed, adventurous, etc.)
  4. Apply mobility and budget constraints
  5. Return top 5 recommendations with descriptions

#### 4. Itinerary Generation
- **Agent**: Itinerary Agent (`agent_itinerary.py`)
- **Process**:
  1. Receive hotel and place data from other agents
  2. Generate schedule optimized for timing
  3. Format output as structured JSON

#### 5. Insert Data
- **Backend**: FastAPI server with WebSocket support
- **Process**:
  1. Save complete itinerary to Supabase database
  2. Store booking data
  3. Broadcast updates to connected frontend clients

### Technical Implementation Steps

#### Phase 1: Environment Setup
1. **Database Configuration**: Set up Supabase schemas (`travel`, `planner`)
2. **API Keys**: Configure Gemini AI and Supabase credentials
3. **Dependencies**: Install Python packages and frameworks
4. **User Profile**: Customize preferences and constraints

#### Phase 2: Agent Development
1. **LLM Integration**: Configure Google Gemini with Strands framework
2. **System Prompts**: Design specialized prompts for each agent type
3. **Database Queries**: Implement Supabase client operations
4. **Integrated Communication**: Establish data flow between agents

#### Phase 3: Integration & Testing
1. **End-to-End Testing**: Verify complete workflow through CLI
2. **Performance Optimization**: Optimize database queries and API calls
3. **Monitoring Setup**: Implement logging and error tracking

#### Phase 4: Backend Services (Done by AI)
1. **FastAPI Server**: Create REST API endpoints
2. **WebSocket Implementation**: Enable real-time frontend updates
3. **CORS Configuration**: Allow cross-origin requests
4. **Error Handling**: Implement robust exception management

#### Phase 5: Frontend Interface (Done by AI)
1. **HTML/JavaScript**: Build responsive web interface
2. **WebSocket Client**: Connect to backend for live updates
3. **Data Visualization**: Display plans and bookings
4. **User Interaction**: Handle form submissions and confirmations


### Decision-Making Process

#### Agent Coordination Strategy
- **Sequential Processing**: Agents execute in logical order (Hotel → Places → Itinerary)
- **Data Sharing**: Each agent receives relevant output from previous agents
- **Error Handling**: Handle cases where agents fail or return no results
- **User Intervention**: Allow manual intervention at critical decision points

#### Quality Assurance Steps
1. **Input Validation**: Sanitize and validate all user inputs
2. **Output Verification**: Ensure agent responses meet expected formats
4. **Error Recovery**: Implement graceful degradation for partial failures

#### Scalability Considerations
- **Modular Agent Design**: Each agent can be scaled independently

### Database Setup

Ensure your Supabase database has the following schemas and tables:

**Schema: `travel` (Simulate travel app API)**
- `hotels` table: id, name, city, rating, price_per_night, swimming_pool, restaurant, wifi, parking, gym
- `places` table: id, name, city, category, description

<img width="557" height="385" alt="image" src="https://github.com/user-attachments/assets/2ad29805-ec84-49db-988c-b59d525d4d33" />


**Schema: `planner` (Simulate user planner app)**
- `plans` table: plan_id, destination, start_date, end_date, itinerary, booking_id
- `bookings` table: booking_id, hotel_name, check_in, check_out, price_per_night
  
<img width="832" height="523" alt="image" src="https://github.com/user-attachments/assets/24d9dedb-83f2-42d9-bdfe-b8e734e71fc0" />



### Component Details

**1. Root Agent (`agents/root_agent.py`)**
- Orchestrates the entire planning workflow
- Manages three specialized sub-agents
- Implements human-in-the-loop for booking confirmations
- Uses Strands framework with Google Gemini LLM

**2. Hotel Agent (`agents/agent_hotel.py`)**
- Queries Supabase for hotels matching user criteria
- Filters by city, rating, price, and facilities
- Handles booking transactions
- Integrates with N8N for invoice automation
- Checks user balance before booking

**3. Place Agent (`agents/agent_place.py`)**
- Fetches tourist attractions from database
- Filters by category (Cultural, Historical, Nature, etc.)
- Considers user behavioral style and constraints
- Returns top 5 recommendations

**4. Itinerary Agent (`agents/agent_itinerary.py`)**
- Generates day-by-day schedule
- Optimizes timing based on user constraints
- Incorporates hotel and place data
- Outputs structured JSON format

**5. Backend (`backend.py`)**
- FastAPI server with WebSocket support
- Real-time data synchronization
- CORS enabled for cross-origin requests
- Serves frontend and handles database queries

**6. Database Layer (`supabaseClient.py`)**
- Supabase client initialization
- Separate admin and anon clients
- Handles all database operations

**7. Booking Invoice**

<img width="592" height="683" alt="image" src="https://github.com/user-attachments/assets/bbe29361-e61e-4d19-aa7e-8d3d5457ba5d" />


## Limitation
- **Not Scalable**: Currently, application only run for one person only
- **AI Error**: Currenty, AI flow is contain error in some executions
- **Monitoring**: Currently, each application can only be monitored separately. There is no unified monitoring mechanism to view all integrated applications in a single dashboard

## Risk Identification & Security Analysis
### 1. Frontend API Key Exposure and Websocket hijacking

**Attack Scenario:**
- View real-time booking and plan data through frontend access

**Likelihood:** High | **Impact:** High

**Mitigation Strategies:**
- Never include API keys in frontend JavaScript code
- Add login system before viewing booking and plan data

**Monitoring**
- Monitor API usage and request for unusual patterns

### 2. Personal Data Leaks
**Attack Scenario:**
- People can see personal data like username, and user email from `user_profile.json`

**Likelihood:** High | **Impact:** High

**Mitigation Strategies:**
- Store personal data securely outside of public repositories

**Monitoring**
- No way directly to view people who see our personal data, currently just monitor API usage and request for unusual patterns

### 3. System prompt Leaks
**Attack Scenario:**
- Internal business logic
- Prompt engineering techniques and strategies
- System vulnerabilities and weaknesses

**Likelihood:** High | **Impact:** High

**Mitigation Strategies:**
- Store system prompts securely outside of public repositories

**Monitoring:**
- Regular code reviews for hardcoded prompts
- Track unusual AI agent behavior patterns

### 4. Database Scema Leaks
**Attack Scenario:**
- Schema and table name are exposed in public repository

**Likelihood:** High | **Impact:** High

**Mitigation Strategies:**
- Use database views instead of direct table access

**Monitoring:**
- Regular security audits of API endpoints

### 5. Depedency Leaks
**Attack Scenario:**
- Internal business logic if store `requirements.txt` in public repository

**Likelihood:** High | **Impact:** High

**Mitigation Strategies:**
- Store system depedency securely outside of public repositories

**Monitoring:**
- Regular audits error of program

## Error Possibility
- AI generate wrong JSON format
- AI ignore user preferences, cause to no places or hotel will be choose
- Gemini API reach token limit

## Tools & Resources Used

### AI & LLM
- **Strands Framework**: Multi-agent orchestration framework
- **Gemini Model**: `gemini-2.5-flash` for AI Agent
- **ChatGPT**: For research needs
- **Claude Sonnet**: `Claude Sonnet 3.5` for code assist

### Backend & Database
- **FastAPI**: Modern Python web framework for building APIs & websocket
- **Supabase**: PostgreSQL database 
- **Python-dotenv**: Environment variable management

### Development Tools
- **Rich**: Beautiful terminal output and error tracing
- **Uvicorn**: ASGI server for FastAPI

### External Integrations
- **N8N**: Workflow automation for invoice sending

### Security & Best Practices
- Environment variable isolation
- Parameterized database queries
- CORS middleware for API security
- Human-in-the-loop for critical operations

### Documentation & Resources
- [Strands Documentation](https://strandsagents.com/latest/documentation/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Google Gemini API](https://ai.google.dev/docs)
- [N8N Documentation](https://docs.n8n.io/)
