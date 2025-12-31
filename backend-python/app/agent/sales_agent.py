import asyncio
from typing import List, Tuple, Dict, Any

from app.agent.base_agent import BaseAgent
import app.agent.memory as memory
from app.agent.stages import SalesStage
from app.agent.transitions import ALLOWED_TRANSITIONS
from app.agent.prompts import (
    SDR_SYSTEM_PROMPT,
    SALES_SYSTEM_PROMPT,
    VOICE_CONVERSATION_WRAPPER,
    STAGE_PROMPTS,
    PRICING_GATE_MODIFIER,
    SEMANTIC_LOCK_MODIFIER,
    NUDGE_MODIFIER,
    CLOSING_STEP_MODIFIER,
)
from app.agent.analyzer import analyzer
from app.agent.intelligence import (
    EXIT_CONDITIONS, 
    PRICING_GATE_METADATA_KEY, 
    SESSION_END_KEY, 
    ALLOWED_ADVANCE_INTENTS
)
from app.services.cerebras import cerebras_service
from app.logging import logger


class SalesAgent(BaseAgent):
    """
    Professional AI Sales Agent.
    Backend controls flow — LLM only generates language.
    """

    def prepare_payload(self, session_id: str) -> Tuple[str, SalesStage]:
        """
        Calculates the correct system prompt and current stage based on memory.
        Applies guardrails, semantic locks, pricing gates, and nudges.
        """
        # ---------- Metadata ----------
        mode = memory.session_memory.get_metadata(session_id, "mode")
        current_stage = memory.session_memory.get_metadata(session_id, "stage")
        value_presented = memory.session_memory.get_metadata(session_id, PRICING_GATE_METADATA_KEY) or False
        is_locked = memory.session_memory.get_metadata(session_id, SESSION_END_KEY) or False
        
        # Ensure current_stage is a SalesStage enum
        if isinstance(current_stage, str):
            current_stage = SalesStage(current_stage)

        # ---------- Guardrail: Stalling Nudge ----------
        turns = memory.session_memory.turns_in_stage(session_id)
        nudge_text = ""
        if turns > 2 and current_stage != SalesStage.CLOSING:
            logger.info(f"[Guardrail] Stalling detected in {current_stage.value}. Preparing nudge.")
            nudge_text = NUDGE_MODIFIER.format(goal=STAGE_PROMPTS.get(current_stage, ""))

        # ---------- Prompt Generation ----------
        system_prompt = (
            SDR_SYSTEM_PROMPT if mode == "SDR" else SALES_SYSTEM_PROMPT
        )
        
        # Add stage-specific precision
        stage_instruction = STAGE_PROMPTS.get(current_stage, "")
        
        # Add Semantic Lock
        system_prompt += SEMANTIC_LOCK_MODIFIER.format(
            stage=current_stage.value,
            goal=stage_instruction
        )
        
        # Add Pricing Gate
        system_prompt += f"\nValue Presented: {value_presented}"
        system_prompt += PRICING_GATE_MODIFIER

        # Add Nudge if stalling
        if nudge_text:
            system_prompt += nudge_text

        # Handle Session Lock
        if is_locked:
            system_prompt += CLOSING_STEP_MODIFIER

        system_prompt += f"\n\n{VOICE_CONVERSATION_WRAPPER}"
        
        return system_prompt, current_stage

    def update_memory(self, session_id: str, role: str, content: str):
        """Update session memory with a new message."""
        memory.session_memory.add_message(session_id, role, content)

    def advance_logic(self, session_id: str, current_stage: SalesStage, analysis: Dict[str, Any]):
        """
        Determines if we should advance based on analyzer recommendation, intents, and exit conditions.
        """
        if current_stage == SalesStage.CLOSING:
            # If meeting is locked, lock the session
            if memory.session_memory.get_metadata(session_id, "meeting_locked"):
                logger.info("[Flow] Meeting locked. Locking session.")
                memory.session_memory.set_metadata(session_id, SESSION_END_KEY, True)
            return

        # 1. Verification: Is the intent allowed for advancing?
        intent = analysis.get("intent")
        allowed_intents = ALLOWED_ADVANCE_INTENTS.get(current_stage, set())
        
        # 2. Check if analyzer recommended advance
        should_advance = analysis.get("recommended_action") == "advance"
        
        if should_advance and intent not in allowed_intents:
            logger.info(f"[Flow] Intent '{intent}' not in advance list for {current_stage.value}. Blocking advance.")
            should_advance = False

        # 3. Verify all exit conditions for the current stage are met in metadata
        required_info = EXIT_CONDITIONS.get(current_stage, [])
        for field in required_info:
            val = memory.session_memory.get_metadata(session_id, field)
            if not val:
                logger.info(f"[Flow] Missing required info '{field}' for stage {current_stage.value}. Staying.")
                should_advance = False
                break

        if should_advance:
            self._advance_stage(session_id, current_stage)
        else:
            logger.info(f"[Flow] Stage Lock: Staying in {current_stage.value}.")

    async def generate_response(self, text: str, session_id: str) -> str:
        # 1. Update user memory
        self.update_memory(session_id, "user", text)
        
        # 2. Get current state
        current_stage = memory.session_memory.get_metadata(session_id, "stage")
        if isinstance(current_stage, str):
            current_stage = SalesStage(current_stage)
            
        history = memory.session_memory.get_history(session_id)

        # 3. Analyze Input (Intent + Info Extraction)
        analysis = await analyzer.analyze(text, history, current_stage)
        logger.info(f"[Analyzer] session={session_id} intent={analysis.get('intent')} action={analysis.get('recommended_action')}")

        # 4. Update Metadata with extracted info
        for key, val in analysis.get("extracted_info", {}).items():
            if val is not None:
                memory.session_memory.set_metadata(session_id, key, val)
                # If we're providing value info, flip the pricing gate
                if key == "value_accepted" and val is True:
                     memory.session_memory.set_metadata(session_id, PRICING_GATE_METADATA_KEY, True)

        # 5. Prepare Payload (Strict Prompting)
        system_prompt, final_stage = self.prepare_payload(session_id)
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)

        turns = memory.session_memory.turns_in_stage(session_id)
        logger.info(
            f"[SalesAgent] session={session_id} stage={final_stage.value} turns={turns}"
        )

        # 6. AI Generation
        # Add extra instruction if intent was vague or evasive
        if analysis.get("is_vague"):
            messages.append({"role": "system", "content": "The user was vague or evasive. Gently but firmly ask for the missing information before proceeding."})

        response = await cerebras_service.chat_completion(messages)

        # 7. Update assistant memory
        self.update_memory(session_id, "assistant", response)

        # 8. Advance Stage Machine logic
        self.advance_logic(session_id, final_stage, analysis)

        return response

    def _advance_stage(self, session_id: str, current_stage: SalesStage):
        allowed = ALLOWED_TRANSITIONS.get(current_stage, [])
        if allowed:
            next_stage = allowed[0]
            logger.info(f"[Transition] {current_stage.value} -> {next_stage.value}")
            memory.session_memory.advance_stage(session_id, next_stage)
        else:
            logger.info(f"[Flow] End of flow reached at {current_stage.value}")

    # ---------- CLI / Text Testing ----------
    def handle_text(self, text: str, session_id: str = "default") -> str:
        return asyncio.run(self.generate_response(text, session_id))


sales_agent = SalesAgent()
