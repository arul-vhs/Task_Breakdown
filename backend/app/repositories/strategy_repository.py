import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.models.strategy import Strategy, ReadinessAnalysis

class StrategyRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_strategies(self, goal_id: uuid.UUID, strategies_list: List[Dict[str, Any]]) -> List[Strategy]:
        # Delete old strategies associated with the goal
        self.db.query(Strategy).filter(Strategy.goal_id == goal_id).delete()
        
        db_strategies = []
        for item in strategies_list:
            strat = Strategy(
                goal_id=goal_id,
                strategy_key=item["strategy_key"],
                title=item["title"],
                description=item["description"],
                pros=item.get("pros", []),
                cons=item.get("cons", []),
                is_recommended=item.get("is_recommended", False),
                is_selected=False,
                strategy_json=item.get("strategy_json", item)
            )
            self.db.add(strat)
            db_strategies.append(strat)
        self.db.commit()
        return db_strategies

    def select_strategy(self, goal_id: uuid.UUID, strategy_key: str) -> Optional[Strategy]:
        # Deselect all strategies for this goal
        self.db.query(Strategy).filter(Strategy.goal_id == goal_id).update({Strategy.is_selected: False})
        
        # Select targeted strategy
        target = self.db.query(Strategy).filter(
            and_(Strategy.goal_id == goal_id, Strategy.strategy_key == strategy_key)
        ).first()
        if target:
            target.is_selected = True
            self.db.commit()
            self.db.refresh(target)
        return target

    def get_selected(self, goal_id: uuid.UUID) -> Optional[Strategy]:
        return self.db.query(Strategy).filter(
            and_(Strategy.goal_id == goal_id, Strategy.is_selected == True)
        ).first()

    def get_all_by_goal(self, goal_id: uuid.UUID) -> List[Strategy]:
        return self.db.query(Strategy).filter(Strategy.goal_id == goal_id).all()

    def save_readiness_analysis(
        self,
        goal_id: uuid.UUID,
        overall_score: int,
        dimension_scores: Dict[str, int],
        identified_gaps: List[str],
        remediation_steps: List[str],
        analysis_json: Optional[Dict[str, Any]] = None
    ) -> ReadinessAnalysis:
        analysis = self.db.query(ReadinessAnalysis).filter(ReadinessAnalysis.goal_id == goal_id).first()
        if analysis:
            analysis.overall_readiness_score = overall_score
            analysis.dimension_scores = dimension_scores
            analysis.identified_gaps = identified_gaps
            analysis.remediation_steps = remediation_steps
            if analysis_json is not None:
                analysis.analysis_json = analysis_json
        else:
            analysis = ReadinessAnalysis(
                goal_id=goal_id,
                overall_readiness_score=overall_score,
                dimension_scores=dimension_scores,
                identified_gaps=identified_gaps,
                remediation_steps=remediation_steps,
                analysis_json=analysis_json
            )
            self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_readiness_analysis(self, goal_id: uuid.UUID) -> Optional[ReadinessAnalysis]:
        return self.db.query(ReadinessAnalysis).filter(ReadinessAnalysis.goal_id == goal_id).first()
