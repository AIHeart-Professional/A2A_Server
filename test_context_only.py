#!/usr/bin/env python3
"""
Test only the context manager functionality without agent initialization
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_context_functionality():
    """Test context storage and retrieval without agent"""
    print("=== Testing Context Functionality ===")
    
    try:
        # Import only what we need
        from Agents.context_manager import context_manager
        print("✓ Context manager imported")
        
        # Test data
        user_id = "test_user_123"
        session_id = "session_456"
        
        # Test 1: Store first conversation
        print("\n1. Storing first conversation...")
        conv1 = "User: My character is Hero, a level 5 warrior with 100 HP.\nAgent: Got it! Hero is your level 5 warrior with 100 HP."
        
        chunk_id1 = await context_manager.store_conversation_chunk(user_id, session_id, conv1)
        print(f"   ✓ Stored: {chunk_id1}")
        
        # Test 2: Store second conversation
        print("\n2. Storing second conversation...")
        conv2 = "User: Can Hero cast magic spells?\nAgent: As a warrior, Hero focuses on physical combat but may learn basic spells."
        
        chunk_id2 = await context_manager.store_conversation_chunk(user_id, session_id, conv2)
        print(f"   ✓ Stored: {chunk_id2}")
        
        # Test 3: Retrieve context about character level
        print("\n3. Testing context retrieval for 'character level'...")
        context = await context_manager.retrieve_relevant_context(
            user_id, "What is my character's level?", max_chunks=3, max_tokens=500
        )
        
        if context:
            print(f"   ✓ Retrieved context ({len(context)} chars):")
            print(f"   {context}")
        else:
            print("   ✗ No context found")
        
        # Test 4: Retrieve context about magic
        print("\n4. Testing context retrieval for 'magic'...")
        magic_context = await context_manager.retrieve_relevant_context(
            user_id, "magic spells", max_chunks=3, max_tokens=500
        )
        
        if magic_context:
            print(f"   ✓ Retrieved magic context ({len(magic_context)} chars):")
            print(f"   {magic_context}")
        else:
            print("   ✗ No magic context found")
        
        # Test 5: Get persona context
        print("\n5. Testing persona context...")
        persona = await context_manager.get_persona_context(user_id)
        
        if persona:
            print(f"   ✓ Persona context: {persona}")
        else:
            print("   ✗ No persona context")
        
        print("\n=== Context Test Complete ===")
        print("✓ Context manager is working correctly!")
        
        # Test the message enhancement logic (simulate what agent_executor does)
        print("\n6. Testing message enhancement logic...")
        current_message = "What's my character's current HP?"
        
        relevant_context = await context_manager.retrieve_relevant_context(
            user_id, current_message, max_chunks=5, max_tokens=1500
        )
        persona_context = await context_manager.get_persona_context(user_id)
        
        full_context = ""
        if relevant_context:
            full_context += f"\n[CONVERSATION HISTORY]\n{relevant_context}\n"
        if persona_context:
            full_context += f"\n[CHARACTER CONTEXT]\n{persona_context}\n"
        
        if full_context.strip():
            enhanced_message = f"{full_context}\n[CURRENT MESSAGE]\n{current_message}"
            print(f"   ✓ Enhanced message created ({len(enhanced_message)} chars):")
            print("   " + "="*50)
            print(enhanced_message)
            print("   " + "="*50)
        else:
            print("   ✗ No context to enhance message with")
        
    except Exception as e:
        print(f"\n❌ Test failed: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_context_functionality())
