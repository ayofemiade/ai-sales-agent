from app.agent.sales_agent import sales_agent
import app.agent.memory as memory

def run():
    session_id = "cli_test_session"
    
    print("\n--- ConvergsAI Hardened Sales CLI ---")
    print("Ready. Type 'exit' to quit.\n")

    while True:
        # Get current state for display
        stage = memory.session_memory.get_metadata(session_id, "stage")
        turns = memory.session_memory.turns_in_stage(session_id)
        
        user_input = input(f"[{stage.value if hasattr(stage, 'value') else stage} - Turn {turns}] User: ")
        
        if user_input.lower() == "exit":
            break

        response = sales_agent.handle_text(user_input, session_id)
        print(f"Agent: {response}\n")

if __name__ == "__main__":
    run()
