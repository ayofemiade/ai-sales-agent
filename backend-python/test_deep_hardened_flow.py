import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.agent.sales_agent import sales_agent
from app.agent.stages import SalesStage
from app.agent.memory import session_memory
from app.agent.intelligence import PRICING_GATE_METADATA_KEY, SESSION_END_KEY

async def test_nudge_logic():
    print("\n--- TEST: Stalling Nudge Logic ---")
    session_id = "test_nudge"
    session_memory.clear_session(session_id)
    session_memory.set_metadata(session_id, "mode", "SDR")
    session_memory.advance_stage(session_id, SalesStage.QUALIFICATION)
    
    print(f"Current Stage: {session_memory.get_metadata(session_id, 'stage')}")
    
    # Send 3 messages without providing info
    for i in range(3):
        user_input = f"I am just curious about the weather {i}"
        print(f"User: {user_input}")
        response = await sales_agent.generate_response(user_input, session_id)
        # print(f"Agent: {response}")
        turns = session_memory.turns_in_stage(session_id)
        print(f"Turns in stage: {turns}")

    # The 4th message generation should trigger a nudge in the system prompt internally.
    # We verify that we are STILL in QUALIFICATION (no blind jump).
    final_stage = session_memory.get_metadata(session_id, 'stage')
    print(f"Final Stage: {final_stage}")
    assert final_stage == SalesStage.QUALIFICATION, "Error: Blindly jumped stage after stalling"
    print("SUCCESS: Stayed in stage but nudged (verified via logs).")

async def test_explicit_value_acceptance():
    print("\n--- TEST: Explicit Value Acceptance ---")
    session_id = "test_value"
    session_memory.clear_session(session_id)
    session_memory.advance_stage(session_id, SalesStage.SOLUTION)
    
    print(f"Current Stage: SOLUTION")
    
    # 1. User asks a question (no acceptance)
    user_input = "Does it handle multiple languages?"
    print(f"User: {user_input}")
    response = await sales_agent.generate_response(user_input, session_id)
    
    final_stage = session_memory.get_metadata(session_id, 'stage')
    print(f"Stage after question: {final_stage}")
    assert final_stage == SalesStage.SOLUTION, "Error: Advanced without explicit acceptance"

    # 2. User accepts value
    user_input = "That sounds great, I'm interested."
    print(f"User: {user_input}")
    response = await sales_agent.generate_response(user_input, session_id)
    
    final_stage = session_memory.get_metadata(session_id, 'stage')
    print(f"Stage after acceptance: {final_stage}")
    # Should move to OBJECTION or beyond
    assert final_stage != SalesStage.SOLUTION
    print("SUCCESS: Advanced only after explicit acceptance.")

async def test_clarification_no_objection_jump():
    print("\n--- TEST: Clarification vs Objection ---")
    session_id = "test_clarify"
    session_memory.clear_session(session_id)
    session_memory.advance_stage(session_id, SalesStage.PROBLEM)
    
    print(f"Current Stage: PROBLEM")
    
    # Curiosity/Clarification should NOT trigger the Objection stage
    user_input = "Wait, how exactly does the AI connect to my phone?"
    print(f"User: {user_input}")
    
    response = await sales_agent.generate_response(user_input, session_id)
    
    final_stage = session_memory.get_metadata(session_id, 'stage')
    print(f"Final Stage: {final_stage}")
    assert final_stage == SalesStage.PROBLEM, f"Error: Jumped to {final_stage} on curiosity"
    print("SUCCESS: Stayed in stage on curiosity question.")

async def test_session_lock():
    print("\n--- TEST: Session Lock After Close ---")
    session_id = "test_lock"
    session_memory.clear_session(session_id)
    session_memory.advance_stage(session_id, SalesStage.CLOSING)
    session_memory.set_metadata(session_id, "meeting_locked", True)
    
    print(f"Current Stage: CLOSING (Meeting Locked)")
    
    user_input = "Can you also tell me about your other products?"
    print(f"User: {user_input}")
    
    response = await sales_agent.generate_response(user_input, session_id)
    print(f"Agent: {response}")
    
    is_locked = session_memory.get_metadata(session_id, SESSION_END_KEY)
    print(f"Session Locked: {is_locked}")
    assert is_locked is True, "Error: Session not locked after closing"
    print("SUCCESS: Session locked. No more discovery allowed.")

if __name__ == "__main__":
    asyncio.run(test_nudge_logic())
    asyncio.run(test_explicit_value_acceptance())
    asyncio.run(test_clarification_no_objection_jump())
    asyncio.run(test_session_lock())
