from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.goal_repository import GoalRepository
from app.repositories.strategy_repository import StrategyRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.progress_repository import ProgressRepository
from app.providers.failover_provider import FailoverProvider
from app.services.goal_service import GoalService
from app.services.strategy_service import StrategyService
from app.services.validation_service import ValidationService
from app.services.blueprint_service import BlueprintService
from app.services.scheduling_service import SchedulingService
from app.services.progress_service import ProgressService
from app.services.coach_service import CoachService
from app.services.replanning_service import ReplanningService

class ServiceFactory:
    def __init__(self, db: Session):
        self.db = db
        self._provider = None
        
    @property
    def provider(self):
        if self._provider is None:
            self._provider = FailoverProvider()
        return self._provider

    def goal_service(self) -> GoalService:
        return GoalService(UserRepository(self.db), GoalRepository(self.db), self.provider)

    def strategy_service(self) -> StrategyService:
        return StrategyService(UserRepository(self.db), GoalRepository(self.db), StrategyRepository(self.db), self.provider)

    def validation_service(self) -> ValidationService:
        return ValidationService(UserRepository(self.db), GoalRepository(self.db), StrategyRepository(self.db), self.provider)

    def blueprint_service(self) -> BlueprintService:
        return BlueprintService(UserRepository(self.db), GoalRepository(self.db), StrategyRepository(self.db), self.provider)

    def scheduling_service(self) -> SchedulingService:
        return SchedulingService(UserRepository(self.db), GoalRepository(self.db), ScheduleRepository(self.db))

    def progress_service(self) -> ProgressService:
        return ProgressService(GoalRepository(self.db), ProgressRepository(self.db))

    def coach_service(self) -> CoachService:
        return CoachService(UserRepository(self.db), GoalRepository(self.db), ScheduleRepository(self.db), ProgressRepository(self.db), self.provider)

    def replanning_service(self) -> ReplanningService:
        return ReplanningService(UserRepository(self.db), GoalRepository(self.db), ScheduleRepository(self.db), ProgressRepository(self.db), self.provider)
