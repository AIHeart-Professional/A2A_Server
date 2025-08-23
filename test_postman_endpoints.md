# Postman Testing Guide for Context Passing

## Setup
1. Start the server: `conda activate RP-MCP && python -m uvicorn api_server:app --reload --port 8001`
2. Watch the console output for context logging messages

## Test Endpoints

### Endpoint 1: `/A2A/handle_request` (Non-streaming)
**Method:** POST  
**URL:** `http://localhost:8001/A2A/handle_request`  
**Headers:** `Content-Type: application/json`

**First Request Body:**
```json
{
  "request": {
    "user_id": "test_user_123",
    "user_query": "My character is Hero, a level 5 warrior with 100 HP and a magic sword",
    "server_id": "test_server"
  },
  "agent_card": ["Veritas_Agent"],
  "agents": {
    "Veritas_Agent": {
      "name": "Veritas",
      "description": "Character management agent"
    }
  }
}
```

**Second Request Body (to test context):**
```json
{
  "request": {
    "user_id": "test_user_123",
    "user_query": "What is my character's level and what weapon do they have?",
    "server_id": "test_server"
  },
  "agent_card": ["Veritas_Agent"],
  "agents": {
    "Veritas_Agent": {
      "name": "Veritas",
      "description": "Character management agent"
    }
  }
}
```

### Endpoint 2: `/A2A/handle_request_stream` (Streaming)
**Method:** POST  
**URL:** `http://localhost:8001/A2A/handle_request_stream`  
**Headers:** `Content-Type: application/json`

Use the same request bodies as above.

## What to Look For in Console Output

### ✅ Success Indicators:
```
🌐 API REQUEST | /A2A/handle_request | user=test_use... | message='My character is Hero, a level 5 warrior...'
🔍 RETRIEVING CONTEXT for user=test_use... query='What is my character's level...'
✅ CONTEXT FOUND for user=test_use... | 1 chunks | 150 chars
💉 INJECTING CONTEXT for user=test_use...
📝 MESSAGE ENHANCED with: CONVERSATION_HISTORY
💾 STORING CONTEXT | user=test_use... | session=test_ses... | chunk=test_user_123_test_session_1234567890 | 45 tokens
🤖 AGENT RESPONSE | user=test_use... | 200 chars | 2.34s
```

### ❌ Failure Indicators:
```
❌ NO CONTEXT found for user=test_use...
📝 MESSAGE NOT ENHANCED (no context available)
❌ CONTEXT ERROR in context_retrieval: SomeError: error message
```

## Testing Steps:
1. Send first request - establishes context
2. Wait for response and check console for "STORING CONTEXT" message
3. Send second request - should show "CONTEXT FOUND" and "INJECTING CONTEXT"
4. Verify second response references information from first request

## Console Log Legend:
- 🌐 = API request received
- 🔍 = Context retrieval started
- ✅ = Context found successfully
- ❌ = No context or error
- 💉 = Context being injected into message
- 📝 = Message enhancement status
- 💾 = Context being stored
- 🤖 = Agent response completed
