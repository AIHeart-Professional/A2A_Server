#!/usr/bin/env python3
"""
Simple test for context manager functionality
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_context_manager():
    """Test context storage and retrieval"""
    print("=== Testing Context Manager ===")
    
    try:
        from Agents.context_manager import context_manager
        print("✓ Context manager imported")
        
        # Test user
        test_user_id = "test_user_123"
        test_session_id = "test_session_456"
        
        # Test 1: Store conversation chunk
        print("\n1. Testing context storage...")
        conversation = "User: My character is Hero, a level 5 warrior with 100 HP.\nAgent: Got it! Hero is your level 5 warrior character with 100 HP. How can I help you with Hero today?"
        
        chunk_id = await context_manager.store_conversation_chunk(
            test_user_id, test_session_id, conversation
        )
        print(f"   ✓ Stored chunk: {chunk_id}")
        
        # Test 2: Retrieve relevant context
        print("\n2. Testing context retrieval...")
        query = "What's my character's level?"
        
        relevant_context = await context_manager.retrieve_relevant_context(
            test_user_id, query, max_chunks=3, max_tokens=500
        )
        
        if relevant_context:
            print(f"   ✓ Retrieved context ({len(relevant_context)} chars):")
            print(f"   {relevant_context}")
        else:
            print("   ✗ No context retrieved")
        
        # Test 3: Get persona context
        print("\n3. Testing persona context...")
        persona_context = await context_manager.get_persona_context(test_user_id)
        
        if persona_context:
            print(f"   ✓ Persona context: {persona_context}")
        else:
            print("   ✗ No persona context")
        
        # Test 4: Store another conversation and test retrieval
        print("\n4. Testing multiple conversations...")
        conversation2 = "User: Can Hero learn magic spells?\nAgent: As a warrior, Hero typically focuses on physical combat, but some warriors can learn basic magic depending on your game system."
        
        chunk_id2 = await context_manager.store_conversation_chunk(
            test_user_id, test_session_id, conversation2
        )
        print(f"   ✓ Stored second chunk: {chunk_id2}")
        
        # Retrieve context about magic
        magic_context = await context_manager.retrieve_relevant_context(
            test_user_id, "magic spells", max_chunks=5, max_tokens=1000
        )
        
        if magic_context:
            print(f"   ✓ Magic context retrieved ({len(magic_context)} chars)")
            print(f"   {magic_context}")
        else:
            print("   ✗ No magic context retrieved")
        
        print("\n=== Context Manager Test Complete ===")
        
    except Exception as e:
        print(f"\n❌ Test failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_context_manager())
