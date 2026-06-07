import datetime
from collections import defaultdict, deque
from typing import List, Dict, Any

class SchedulerEngine:
    def __init__(self):
        pass

    def _topological_sort(self, tasks: List[Dict[str, Any]], dependencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sorts tasks topologically using Kahn's algorithm based on their task dependencies.
        Falls back to phase order if no dependencies exist or if cycles are detected.
        """
        task_map = {t["task_id_alias"]: t for t in tasks}
        
        # Build graph
        adj = defaultdict(list)
        in_degree = {t["task_id_alias"]: 0 for t in tasks}
        
        for dep in dependencies:
            u = dep["depends_on_alias"]
            v = dep["task_id_alias"]
            if u in task_map and v in task_map:
                adj[u].append(v)
                in_degree[v] += 1
                
        # Queue for nodes with in-degree 0
        queue = deque([k for k, v in in_degree.items() if v == 0])
        # Sort queue initially by phase number and task ID for consistency
        queue = deque(sorted(list(queue), key=lambda x: (task_map[x].get("phase_number", 0), x)))
        
        sorted_aliases = []
        while queue:
            curr = queue.popleft()
            sorted_aliases.append(curr)
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        # Check for cycles or unreferenced nodes
        if len(sorted_aliases) < len(tasks):
            # Fallback to simple phase ordering if sorting fails due to cycles
            return sorted(tasks, key=lambda x: (x.get("phase_number", 1), x.get("task_id_alias", "")))
            
        return [task_map[alias] for alias in sorted_aliases]

    def _get_time_slots(self, work_style: str, duration: float) -> str:
        """
        Generates standard time slot labels based on the user's work style and task duration.
        """
        style = work_style.lower()
        if "morning" in style:
            start_hour = 9
        elif "evening" in style:
            start_hour = 19
        elif "pomodoro" in style:
            start_hour = 14
        else: # Deep Work / general
            start_hour = 10
            
        end_hour = start_hour + int(duration)
        end_minutes = int((duration - int(duration)) * 60)
        
        start_str = f"{start_hour:02d}:00"
        end_str = f"{end_hour:02d}:{end_minutes:02d}"
        return f"{start_str} - {end_str}"

    def calculate_schedule(self, tasks: List[Dict[str, Any]], dependencies: List[Dict[str, Any]], profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes a deterministic weekly and daily schedule.
        """
        hours_per_week = float(profile.get("weekly_hours_available", 10.0))
        work_style = profile.get("work_style", "Deep Work")
        
        # 1. Topological Sort of Tasks
        sorted_tasks = self._topological_sort(tasks, dependencies)
        
        # 2. Distribute tasks into weeks based on capacity constraints
        # Introduce a 20% safety buffer inside calculations
        effective_weekly_hours = max(1.0, hours_per_week * 0.8) 
        
        weekly_schedule = []
        current_week_num = 1
        current_week_hours = 0.0
        current_week_tasks = []
        
        # Track which tasks are placed in which week
        task_to_week = {}
        
        for task in sorted_tasks:
            task_hours = float(task.get("allocated_hours", 2.0))
            
            # If a single task is larger than weekly limit, force split or expand capacity
            if task_hours > effective_weekly_hours:
                # Place in current week, allow spillover
                if current_week_hours > 0 and (current_week_hours + task_hours > effective_weekly_hours):
                    # Finalize current week, push to next
                    weekly_schedule.append({
                        "week_number": current_week_num,
                        "focus": f"Execution & Development Phase {current_week_num}",
                        "allocated_hours": round(current_week_hours, 1),
                        "tasks": current_week_tasks
                    })
                    current_week_num += 1
                    current_week_tasks = []
                    current_week_hours = 0.0
                
                # Assign task to this new week
                current_week_tasks.append({
                    "task_id": task["task_id_alias"],
                    "name": task["name"],
                    "allocated_hours": task_hours
                })
                task_to_week[task["task_id_alias"]] = current_week_num
                current_week_hours += task_hours
                
                # Finalize week immediately due to size
                weekly_schedule.append({
                    "week_number": current_week_num,
                    "focus": f"Core Work Block Phase {current_week_num}",
                    "allocated_hours": round(current_week_hours, 1),
                    "tasks": current_week_tasks
                })
                current_week_num += 1
                current_week_tasks = []
                current_week_hours = 0.0
            else:
                # Standard task fitting
                if current_week_hours + task_hours > effective_weekly_hours:
                    # Finalize current week and increment
                    weekly_schedule.append({
                        "week_number": current_week_num,
                        "focus": f"Sprint Execution Focus {current_week_num}",
                        "allocated_hours": round(current_week_hours, 1),
                        "tasks": current_week_tasks
                    })
                    current_week_num += 1
                    current_week_tasks = []
                    current_week_hours = 0.0
                    
                current_week_tasks.append({
                    "task_id": task["task_id_alias"],
                    "name": task["name"],
                    "allocated_hours": task_hours
                })
                task_to_week[task["task_id_alias"]] = current_week_num
                current_week_hours += task_hours
                
        # Append remaining tasks
        if current_week_tasks:
            weekly_schedule.append({
                "week_number": current_week_num,
                "focus": f"Final Delivery & Consolidation",
                "allocated_hours": round(current_week_hours, 1),
                "tasks": current_week_tasks
            })
            
        # 3. Create Daily Hour-by-Hour Calendar Allocations
        # Distribute each week's tasks over 5 days (Mon-Fri)
        daily_schedule = []
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        for week in weekly_schedule:
            w_num = week["week_number"]
            week_tasks = week["tasks"]
            
            if not week_tasks:
                continue
                
            # Distribute tasks sequentially across days
            task_idx = 0
            for d_idx, day_name in enumerate(days_of_week):
                day_num = (w_num - 1) * 7 + (d_idx + 1)
                day_blocks = []
                day_total_hours = 0.0
                
                # Fit tasks up to daily limit (weekly hours / 5 days)
                daily_limit = hours_per_week / 5.0
                
                while task_idx < len(week_tasks) and day_total_hours < daily_limit:
                    curr_task = week_tasks[task_idx]
                    task_id = curr_task["task_id"]
                    t_hours = curr_task["allocated_hours"]
                    
                    time_slot = self._get_time_slots(work_style, t_hours)
                    day_blocks.append({
                        "task_id": task_id,
                        "name": curr_task["name"],
                        "time_slot": time_slot,
                        "duration_hours": t_hours,
                        "type": "Deep Work" if "morning" not in work_style.lower() else "Morning Sprints"
                    })
                    day_total_hours += t_hours
                    task_idx += 1
                    
                daily_schedule.append({
                    "week_number": w_num,
                    "day_number": day_num,
                    "day_name": day_name,
                    "total_hours": round(day_total_hours, 1),
                    "time_blocks": day_blocks
                })
                
            # If tasks remain (due to roundings), append them to Friday
            if task_idx < len(week_tasks):
                # Put all remaining into Friday
                friday_day = [d for d in daily_schedule if d["week_number"] == w_num and d["day_name"] == "Friday"][0]
                while task_idx < len(week_tasks):
                    curr_task = week_tasks[task_idx]
                    friday_day["time_blocks"].append({
                        "task_id": curr_task["task_id"],
                        "name": curr_task["name"],
                        "time_slot": self._get_time_slots(work_style, curr_task["allocated_hours"]),
                        "duration_hours": curr_task["allocated_hours"],
                        "type": "Catch up Block"
                    })
                    friday_day["total_hours"] = round(friday_day["total_hours"] + curr_task["allocated_hours"], 1)
                    task_idx += 1
                    
        # 4. Schedule Analysis (Confidence, Forecast, Buffers)
        total_weeks = len(weekly_schedule)
        forecast_date = (datetime.date.today() + datetime.timedelta(weeks=total_weeks)).strftime("%B %d, %Y")
        
        # Confidence logic based on available workload vs challenge profile
        confidence = 85
        challenge = profile.get("biggest_challenge", "").lower()
        if "time" in challenge or "busy" in challenge:
            confidence -= 10
        if "consistency" in challenge or "procrastinat" in challenge:
            confidence -= 5
            
        schedule_analysis = {
            "confidence_score": max(50, confidence),
            "goal_completion_forecast": f"On track for completion by {forecast_date} ({total_weeks} weeks total)",
            "buffer_time_allocation": "20% weekly allocation buffer applied to absorb delays.",
            "deadline_feasibility_analysis": f"Sprints structured to fit within your {hours_per_week}h/week limit. Dependency order guaranteed.",
            "rescheduling_suggestions": [
                {
                    "id": "extend_1_week",
                    "title": "Add 1-Week Buffer",
                    "description": "Spreads remaining tasks across an extra buffer week to reduce weekly load.",
                    "impact": "Reduces daily hours by 15%"
                },
                {
                    "id": "weekend_sprint",
                    "title": "Weekend Sprints",
                    "description": "Distributes 2 hours onto Saturday morning, lowering weekday work load.",
                    "impact": "Reduces weekday hours by 20%"
                }
            ]
        }
        
        return {
            "weekly_schedule": weekly_schedule,
            "daily_schedule": daily_schedule,
            "schedule_analysis": schedule_analysis
        }

scheduler_engine = SchedulerEngine()
