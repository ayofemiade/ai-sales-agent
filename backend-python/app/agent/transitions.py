from app.agent.stages import SalesStage

ALLOWED_TRANSITIONS = {
    SalesStage.GREETING: [SalesStage.QUALIFICATION],
    SalesStage.QUALIFICATION: [SalesStage.PROBLEM],
    SalesStage.PROBLEM: [SalesStage.SOLUTION],
    SalesStage.SOLUTION: [SalesStage.OBJECTION],
    SalesStage.OBJECTION: [SalesStage.CLOSING],
    SalesStage.CLOSING: [],
}
