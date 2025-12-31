from enum import Enum

class SalesStage(str, Enum):
    GREETING = "greeting"
    QUALIFICATION = "qualification"
    PROBLEM = "problem"
    SOLUTION = "solution"
    OBJECTION = "objection"
    CLOSING = "closing"
