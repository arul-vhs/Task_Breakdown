# Import Base and all models here for Alembic / Base.metadata imports
from app.database.session import Base
from app.models.user import User
from app.models.profile import Profile
from app.models.goal import Goal, GoalContext
from app.models.strategy import Strategy
from app.models.task import Task, TaskDependency
from app.models.schedule import Schedule, ScheduleVersion
from app.models.progress import ProgressLog
from app.models.reflection import Reflection, CoachInsight, ReplanningHistory
from app.models.analytics import AnalyticsEvent, DailyActivity, StreakHistory
from app.models.notification import Notification, NotificationPreference
from app.models.event_store import GoalEvent, TaskEvent, ScheduleEvent
