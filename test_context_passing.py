#!/usr/bin/env python3
"""
Test script to verify context passing in agent_executor.py
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from Agents.context_manager import context_manager
    from Agents.Veritas_Agent.agent_executor import AgentExecutor
    from Agents.Veritas_Agent.agent import root_agent
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

async def test_context_passing():
    """Test that context is properly retrieved and passed between calls"""
    print("=== Testing Context Passing ===")
    
    # Initialize agent executor
    executor = AgentExecutor(root_agent, "Veritas_Agent_Test")
    
    # Test user
    test_user_id = "test_user_123"
    
    try:
        # Initialize session
        print("\n1. Initializing session...")
        exec_id = await executor.init(test_user_id)
        print(f"   Created execution ID: {exec_id[:8]}...")
        
        # First conversation - establish some context
        print("\n2. First conversation (establishing context)...")
        first_message = "My character's name is Hero and I'm a level 5 warrior with 100 HP."
        
        print(f"   Sending: {first_message}")
        response_parts = []
        async for event in executor.execute(exec_id, first_message):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_parts.append(part.text)
        
        first_response = ''.join(response_parts)
        print(f"   Response: {first_response[:100]}...")
        
        # Wait a moment for context to be stored
        await asyncio.sleep(1)
        
        # Second conversation - should have context from first
        print("\n3. Second conversation (should include context)...")
        second_message = "What's my character's current level?"
        
        print(f"   Sending: {second_message}")
        response_parts = []
        async for event in executor.execute(exec_id, second_message):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_parts.append(part.text)
        
        second_response = ''.join(response_parts)
        print(f"   Response: {second_response[:100]}...")
        
        # Check if context was retrieved
        print("\n4. Checking stored context...")
        stored_context = await context_manager.retrieve_relevant_context(
            test_user_id, second_message, max_chunks=3, max_tokens=500
        )
        
        if stored_context:
            print(f"   ✓ Context retrieved: {len(stored_context)} characters")
            print(f"   Context preview: {stored_context[:200]}...")
        else:
            print("   ✗ No context retrieved")
        
        # Check persona context
        persona_context = await context_manager.get_persona_context(test_user_id)
        if persona_context:
            print(f"   ✓ Persona context: {persona_context[:100]}...")
        else:
            print("   ✗ No persona context")
        
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"\n❌ Test failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_context_passing())
