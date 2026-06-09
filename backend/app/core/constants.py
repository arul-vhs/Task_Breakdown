from enum import Enum

class UserRole(str, Enum):
    STUDENT = "Student"
    FOUNDER = "Founder"
    WORKING_PROFESSIONAL = "Working Professional"
    FREELANCER = "Freelancer"
    JOB_SEEKER = "Job Seeker"

class WorkStyle(str, Enum):
    MORNING = "Morning"
    EVENING = "Evening"
    POMODORO = "Pomodoro"
    DEEP_WORK = "Deep Work"

class GoalStatus(str, Enum):
    DRAFT = "draft"
    STRAT_SELECTION = "strat_selection"
    READINESS_CHECK = "readiness_check"
    PLANNING = "planning"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class BlueprintRefinement(str, Enum):
    MINIMALIST = "Minimalist"
    STANDARD = "Standard"
    COMPREHENSIVE = "Comprehensive"

class ReplanningMode(str, Enum):
    BALANCED = "Balanced"
    CATCH_UP = "Catch Up"
    LOW_STRESS = "Low Stress"
    AGGRESSIVE = "Aggressive"
