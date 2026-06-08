'use client';

import React, { useState, useEffect } from 'react';
import { 
  Plus, Check, Award, Calendar, MessageSquare, RefreshCw, BarChart2, 
  Settings, User, Lock, Mail, ChevronRight, ChevronLeft, ArrowLeft, AlertTriangle, ArrowRight,
  Sparkles, CheckCircle2, Circle, Clock, Flame, ShieldAlert, Compass, Target
} from 'lucide-react';
import { useGlobalStore } from '../store/global-store';
import { api } from '../services/api';

export default function Home() {
  // Store hooks
  const { token, userEmail, activeGoalId, profile, activeTab, setToken, setActiveGoalId, setProfile, setActiveTab, logout } = useGlobalStore();
  
  // Local UI flow states
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [emailInput, setEmailInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  const [authError, setAuthError] = useState('');
  
  // Onboarding wizard states
  const [onboardingStep, setOnboardingStep] = useState(1);
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedStyle, setSelectedStyle] = useState('');
  const [hoursInput, setHoursInput] = useState(10);
  const [challengeInput, setChallengeInput] = useState('');
  
  // Goal and questionnaire states
  const [goalTitle, setGoalTitle] = useState('');
  const [goalStatus, setGoalStatus] = useState<'none' | 'analyzing' | 'questions' | 'strategies' | 'planning' | 'active'>('none');
  const [activeGoal, setActiveGoal] = useState<any>(null);
  const [intelQuestions, setIntelQuestions] = useState<string[]>([]);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [answersList, setAnswersList] = useState<string[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  
  // Strategy and execution blueprint states
  const [strategies, setStrategies] = useState<any[]>([]);
  const [selectedStratKey, setSelectedStratKey] = useState('');
  const [readinessScore, setReadinessScore] = useState<number | null>(null);
  const [readinessDetails, setReadinessDetails] = useState<any>(null);
  const [planPhases, setPlanPhases] = useState<any[]>([]);
  const [planTasks, setPlanTasks] = useState<any[]>([]);
  const [planDeps, setPlanDeps] = useState<any[]>([]);
  
  // Active execution dashboard details
  const [activeTasks, setActiveTasks] = useState<any[]>([]);
  const [weeklySchedule, setWeeklySchedule] = useState<any[]>([]);
  const [dailySchedule, setDailySchedule] = useState<any[]>([]);
  const [scheduleAnalysis, setScheduleAnalysis] = useState<any>(null);
  const [progressMetrics, setProgressMetrics] = useState<any>({
    completion_percentage: 0,
    streak_count: 0,
    health_score: 100,
    time_spent_total: 0,
    allocated_hours_total: 0
  });
  
  // AI Coach chat states
  const [coachInsight, setCoachInsight] = useState<any>(null);
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<any[]>([
    { role: 'assistant', content: "Hello! I am your AI Execution Coach. I monitor your streaks, analyze daily time allocation buffers, and help you adapt when schedules drift. Ask me anything!" }
  ]);
  const [isCoachLoading, setIsCoachLoading] = useState(false);
  
  // Replanning states
  const [replanHours, setReplanHours] = useState(10);
  const [replanMode, setReplanMode] = useState('Balanced');
  const [replanPreview, setReplanPreview] = useState<any>(null);
  const [isReplanningLoading, setIsReplanningLoading] = useState(false);
  
  // Multiple Goals states
  const [goalsList, setGoalsList] = useState<any[]>([]);
  const [isCreatingNewGoal, setIsCreatingNewGoal] = useState(false);
  const [isLoadingGoals, setIsLoadingGoals] = useState(false);

  // Alert logs
  const [systemLogs, setSystemLogs] = useState<string[]>([]);

  // Add system warning logs helper
  const addLog = (msg: string) => {
    setSystemLogs(prev => [msg, ...prev.slice(0, 5)]);
  };

  // Sync profile details on authentication
  useEffect(() => {
    if (token) {
      fetchUserProfile();
      fetchUserGoals();
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const prof = await api.get<any>('/auth/profile', token);
      setProfile(prof);
      addLog("User profile fetched successfully.");
    } catch (e: any) {
      addLog("No active profile detected. Directing to onboarding.");
      setProfile(null);
    }
  };

  const fetchUserGoals = async () => {
    setIsLoadingGoals(true);
    try {
      const goals = await api.get<any[]>('/goals', token);
      setGoalsList(goals || []);
      addLog("User goals fetched successfully.");
    } catch (e: any) {
      addLog("Failed to fetch goals: " + e.message);
      setGoalsList([]);
    } finally {
      setIsLoadingGoals(false);
    }
  };

  const handleBackToGoals = () => {
    setActiveGoalId(null);
    setActiveGoal(null);
    setGoalStatus('none');
    setIsCreatingNewGoal(false);
    setGoalTitle('');
    fetchUserGoals();
    addLog("Returned to goals landing page.");
  };

  const handleSelectGoal = async (goal: any) => {
    setActiveGoalId(goal.id);
    setActiveGoal(goal);
    addLog(`Loading goal: ${goal.title} (Status: ${goal.status})`);
    
    if (goal.status === 'drafting') {
      setGoalStatus('analyzing');
      try {
        const details = await api.get<any>(`/goals/${goal.id}`, token);
        const questions = (details.qa_context || []).map((q: any) => q.question);
        setIntelQuestions(questions);
        
        const answeredQAs = (details.qa_context || []).filter((q: any) => q.answer && q.answer.trim().length > 0);
        const answeredCount = answeredQAs.length;
        const answers = (details.qa_context || []).map((q: any) => q.answer || '');
        
        setAnswersList(answers.slice(0, answeredCount));
        setCurrentQuestionIdx(answeredCount);
        setCurrentAnswer('');
        setGoalStatus('questions');
        addLog(`Resuming goal discovery questionnaire at question ${answeredCount + 1}.`);
      } catch (err: any) {
        addLog("Failed to fetch goal details: " + err.message);
        setGoalStatus('none');
      }
    } else if (goal.status === 'strat_selection') {
      setGoalStatus('analyzing');
      try {
        const strats = await api.get<any[]>(`/goals/${goal.id}/strategies`, token);
        setStrategies(strats || []);
        setGoalStatus('strategies');
        addLog("Resuming strategy selection stage.");
      } catch (err: any) {
        addLog("Failed to fetch strategies: " + err.message);
        setGoalStatus('none');
      }
    } else if (goal.status === 'planning' || goal.status === 'readiness_check') {
      setGoalStatus('analyzing');
      try {
        const tasks = await api.get<any[]>(`/goals/${goal.id}/tasks`, token);
        const readiness = await api.get<any>(`/goals/${goal.id}/readiness`, token);
        setReadinessScore(readiness.overall_readiness_score);
        setReadinessDetails(readiness);
        setPlanTasks(tasks || []);
        setGoalStatus('planning');
        addLog("Resuming blueprint execution planning stage.");
      } catch (err: any) {
        addLog("Failed to fetch tasks/readiness: " + err.message);
        setGoalStatus('none');
      }
    } else if (goal.status === 'active') {
      setGoalStatus('analyzing');
      try {
        const sched = await api.get<any>(`/goals/${goal.id}/schedule`, token);
        const metrics = await api.get<any>(`/goals/${goal.id}/progress`, token);
        
        try {
          const deps = await api.get<any[]>(`/goals/${goal.id}/dependencies`, token);
          setPlanDeps(deps || []);
        } catch (e) {
          setPlanDeps([]);
        }

        loadActiveScheduleDetails(sched);
        setProgressMetrics(metrics);
        
        try {
          const coach = await api.get<any>(`/goals/${goal.id}/coaching`, token);
          setCoachInsight(coach);
        } catch (e) {
          // If no coach insights yet
        }
        
        setGoalStatus('active');
        setActiveTab('dashboard');
        addLog("Active cockpit workspace loaded.");
      } catch (err: any) {
        addLog("Failed to load active schedule/metrics: " + err.message);
        setGoalStatus('none');
      }
    }
  };

  // Auth operations
  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError('');
    try {
      if (authMode === 'register') {
        await api.post('/auth/register', { email: emailInput, password: passwordInput });
        addLog("Registration complete! Signing in...");
      }
      
      const formData = new URLSearchParams();
      formData.append('username', emailInput);
      formData.append('password', passwordInput);
      
      const res = await api.postForm<any>('/auth/token', formData);
      setToken(res.access_token, emailInput);
      addLog("Successfully logged in.");
    } catch (err: any) {
      setAuthError(err.message || 'Authentication failed');
      addLog("Authentication failed: " + err.message);
    }
  };

  // Profile onboarding creation
  const handleProfileOnboarding = async () => {
    try {
      const profData = {
        role: selectedRole,
        work_style: selectedStyle,
        weekly_hours_available: Number(hoursInput),
        biggest_challenge: challengeInput,
        full_name: emailInput.split('@')[0]
      };
      const res = await api.post<any>('/auth/profile', profData, token);
      setProfile(res);
      addLog("Onboarding profile saved.");
    } catch (e: any) {
      // Offline fallback profile save
      setProfile({
        role: selectedRole,
        work_style: selectedStyle,
        weekly_hours_available: Number(hoursInput),
        biggest_challenge: challengeInput,
        full_name: emailInput.split('@')[0]
      });
      addLog("Offline mode: Simulated profile onboarding.");
    }
  };

  // Goal Creation flow (Goal Discovery Node)
  const handleGoalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalTitle.trim()) return;
    setGoalStatus('analyzing');
    
    try {
      const res = await api.post<any>('/goals', { title: goalTitle }, token);
      setActiveGoalId(res.goal_id);
      setActiveGoal({ id: res.goal_id, title: goalTitle, status: 'drafting' });
      setIntelQuestions(res.questions || []);
      setCurrentQuestionIdx(0);
      setAnswersList([]);
      setGoalStatus('questions');
      setIsCreatingNewGoal(false);
      addLog("Goal initialized. Discovery Node questions loaded.");
    } catch (err: any) {
      // Mock Fallback structure
      setActiveGoalId("mock-goal-123");
      setActiveGoal({ id: "mock-goal-123", title: goalTitle, status: 'drafting' });
      setIntelQuestions([
        "How much experience do you have with this goal type?",
        "What specific toolkits or resources do you have access to?",
        "Are there any hard deadlines you need to respect?",
        "How will you measure weekly completion?",
        "What is the first major milestone you want to secure?"
      ]);
      setCurrentQuestionIdx(0);
      setAnswersList([]);
      setGoalStatus('questions');
      setIsCreatingNewGoal(false);
      addLog("Fallback mode: Generated goal intake questions locally.");
    }
  };

  // Intake Questionnaire step
  const handleAnswerSubmit = () => {
    if (!currentAnswer.trim()) return;
    
    const newAnswers = [...answersList, currentAnswer];
    setAnswersList(newAnswers);
    setCurrentAnswer('');
    
    if (currentQuestionIdx + 1 < intelQuestions.length) {
      setCurrentQuestionIdx(currentQuestionIdx + 1);
    } else {
      // Submit questionnaire answers (Strategy Node)
      submitContextAnswers(newAnswers);
    }
  };

  const submitContextAnswers = async (answers: string[]) => {
    setGoalStatus('analyzing');
    const answersPayload = intelQuestions.map((q, idx) => ({
      question: q,
      answer: answers[idx] || ''
    }));
    
    try {
      const res = await api.post<any>(`/goals/${activeGoalId}/answers`, { answers: answersPayload }, token);
      setStrategies(res.strategies || []);
      setGoalStatus('strategies');
      addLog("Context answers logged. Strategy options generated.");
    } catch (e) {
      // Simulated strategies response
      setStrategies([
        {
          strategy_key: "micro_sprints",
          title: "Micro-Habits Sprint Build",
          description: "Focuses on daily 30-minute high-focus blocks to protect against consistency blocks.",
          pros: ["Extremely low time entry barrier", "Creates rapid daily feedback loops"],
          cons: ["Longer overall timeline to final delivery"],
          is_recommended: true
        },
        {
          strategy_key: "deep_work_blocks",
          title: "Deep Work Focus Blocks",
          description: "Organizes execution into 2-3 hour block tasks mapping directly to your morning focus times.",
          pros: ["Maximizes features complexity capacity", "Fewer context switches"],
          cons: ["High mental resistance risk when fatigued"],
          is_recommended: false
        },
        {
          strategy_key: "parallel_staging",
          title: "Parallel Milestone Execution",
          description: "Runs research, setup, and build tasks in parallel to compress deadline delivery dates.",
          pros: ["Fastest delivery roadmap velocity"],
          cons: ["Higher cognitive overhead", "Potential burnout risk"],
          is_recommended: false
        }
      ]);
      setGoalStatus('strategies');
      addLog("Fallback mode: Generated strategy suggestions locally.");
    }
  };

  // Strategy selection selection (Readiness Check, Planning Nodes)
  const handleSelectStrategy = async (key: string) => {
    setSelectedStratKey(key);
    setGoalStatus('analyzing');
    
    try {
      const res = await api.post<any>(`/goals/${activeGoalId}/select-strategy`, { strategy_key: key }, token);
      setReadinessScore(res.readiness.overall_readiness_score);
      setReadinessDetails(res.readiness);
      setPlanPhases(res.execution_plan.phases || []);
      setPlanTasks(res.tasks || []);
      setPlanDeps(res.dependencies || []);
      setGoalStatus('planning');
      addLog("Strategy locked. Readiness Audit & Checklist ready.");
    } catch (e) {
      // Mock plan & readiness fallback
      setReadinessScore(80);
      setReadinessDetails({
        overall_readiness_score: 80,
        dimension_scores: { skills: 85, resources: 90, time: 70 },
        identified_gaps: ["Potential scheduling conflict during weekend commitments"],
        remediation_steps: ["Protect 2 hours buffer time explicitly inside active weeks"]
      });
      setPlanTasks([
        { task_id_alias: "T1", phase_number: 1, phase_name: "Phase 1: Environment Setup", name: "Configure backend schema models and DB pooling", allocated_hours: 2 },
        { task_id_alias: "T2", phase_number: 1, phase_name: "Phase 1: Environment Setup", name: "Setup API routes and token authentication handlers", allocated_hours: 3 },
        { task_id_alias: "T3", phase_number: 2, phase_name: "Phase 2: Core Build", name: "Implement LangGraph orchestrator workflows", allocated_hours: 4 },
        { task_id_alias: "T4", phase_number: 2, phase_name: "Phase 2: Core Build", name: "Develop frontend Zustand state and visual cards", allocated_hours: 3 },
        { task_id_alias: "T5", phase_number: 3, phase_name: "Phase 3: Launch Staging", name: "Deploy Docker images and configure Railway hostings", allocated_hours: 2 }
      ]);
      setPlanDeps([
        { task_id_alias: "T2", depends_on_alias: "T1" },
        { task_id_alias: "T3", depends_on_alias: "T2" },
        { task_id_alias: "T4", depends_on_alias: "T3" },
        { task_id_alias: "T5", depends_on_alias: "T4" }
      ]);
      setGoalStatus('planning');
      addLog("Fallback mode: Initialized execution plan locally.");
    }
  };

  // Approve Blueprint (Scheduling node activation)
  const handleApproveBlueprint = async () => {
    setGoalStatus('analyzing');
    try {
      const res = await api.post<any>(`/goals/${activeGoalId}/approve-blueprint`, { approved: true }, token);
      
      try {
        const deps = await api.get<any[]>(`/goals/${activeGoalId}/dependencies`, token);
        setPlanDeps(deps || []);
      } catch (e) {
        // Keep existing planDeps
      }

      loadActiveScheduleDetails(res.schedule);
      setGoalStatus('active');
      addLog("Execution blueprint approved. Deterministic schedule allocated.");
    } catch (e) {
      // Simulated schedule calculation locally
      simulateScheduleLocal();
      setGoalStatus('active');
      addLog("Fallback mode: Allocated local calendar blocks.");
    }
  };

  const simulateScheduleLocal = () => {
    const weekly = [
      { week_number: 1, focus: "Setup & Init", allocated_hours: 5, tasks: [
        { task_id: "T1", name: "Configure backend schema models", allocated_hours: 2 },
        { task_id: "T2", name: "Setup API routes and token authentication", allocated_hours: 3 }
      ]},
      { week_number: 2, focus: "Core Logic Build", allocated_hours: 7, tasks: [
        { task_id: "T3", name: "Implement LangGraph orchestrator workflows", allocated_hours: 4 },
        { task_id: "T4", name: "Develop frontend Zustand state", allocated_hours: 3 }
      ]},
      { week_number: 3, focus: "Launch and Deploy", allocated_hours: 2, tasks: [
        { task_id: "T5", name: "Deploy Docker images", allocated_hours: 2 }
      ]}
    ];
    
    const daily = [
      { week_number: 1, day_number: 1, day_name: "Monday", total_hours: 2, time_blocks: [
        { task_id: "T1", name: "Configure backend schema models", time_slot: "09:00 - 11:00", duration_hours: 2, type: "Deep Work" }
      ]},
      { week_number: 1, day_number: 2, day_name: "Tuesday", total_hours: 3, time_blocks: [
        { task_id: "T2", name: "Setup API routes and authentication", time_slot: "09:00 - 12:00", duration_hours: 3, type: "Deep Work" }
      ]},
      { week_number: 2, day_number: 8, day_name: "Monday", total_hours: 4, time_blocks: [
        { task_id: "T3", name: "Implement LangGraph workflows", time_slot: "09:00 - 13:00", duration_hours: 4, type: "Deep Work" }
      ]},
      { week_number: 2, day_number: 9, day_name: "Tuesday", total_hours: 3, time_blocks: [
        { task_id: "T4", name: "Develop frontend Zustand state", time_slot: "09:00 - 12:00", duration_hours: 3, type: "Deep Work" }
      ]},
      { week_number: 3, day_number: 15, day_name: "Monday", total_hours: 2, time_blocks: [
        { task_id: "T5", name: "Deploy Docker images", time_slot: "09:00 - 11:00", duration_hours: 2, type: "Deep Work" }
      ]}
    ];
    
    const analysis = {
      confidence_score: 85,
      goal_completion_forecast: "On track for completion in 3 weeks",
      buffer_time_allocation: "20% allocation buffer applied to Friday buffers",
      deadline_feasibility_analysis: "Weekly workload fits within your 10h/week limit."
    };
    
    loadActiveScheduleDetails({ weekly_schedule: weekly, daily_schedule: daily, schedule_analysis: analysis });
  };

  const loadActiveScheduleDetails = (sched: any) => {
    setWeeklySchedule(sched.weekly_schedule || []);
    setDailySchedule(sched.daily_schedule || []);
    setScheduleAnalysis(sched.schedule_analysis || null);
    
    // Convert scheduling tasks to flat active list
    const tasks: any[] = [];
    (sched.weekly_schedule || []).forEach((w: any) => {
      w.tasks.forEach((t: any) => {
        tasks.push({
          task_id_alias: t.task_id,
          name: t.name,
          allocated_hours: t.allocated_hours,
          is_completed: false,
          phase_name: w.focus
        });
      });
    });
    setActiveTasks(tasks);
  };

  // Toggle tasks execution state (Execution Engine update)
  const handleToggleTask = async (alias: string, completed: boolean) => {
    // Update local immediately for latency-free aesthetics
    const updated = activeTasks.map(t => {
      if (t.task_id_alias === alias) return { ...t, is_completed: completed };
      return t;
    });
    setActiveTasks(updated);
    
    // Calculate new local completions percentage
    const completedCount = updated.filter(t => t.is_completed).length;
    const completionPct = Math.round((completedCount / updated.length) * 100);
    
    setProgressMetrics((prev: any) => ({
      ...prev,
      completion_percentage: completionPct,
      streak_count: completed ? prev.streak_count + 1 : Math.max(0, prev.streak_count - 1),
      health_score: completed ? Math.min(100, prev.health_score + 5) : prev.health_score
    }));
    
    try {
      await api.post(`/goals/${activeGoalId}/tasks/${alias}/toggle`, { is_completed: completed }, token);
      addLog(`Task ${alias} status synced with backend.`);
    } catch (e) {
      addLog(`Task ${alias} status updated locally.`);
    }
  };

  // AI Coach dialogue endpoints
  const handleSendCoachMsg = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput;
    setChatMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatInput('');
    setIsCoachLoading(true);
    
    try {
      const res = await api.post<any>(`/goals/${activeGoalId}/coaching/chat`, { message: userMsg }, token);
      setChatMessages(prev => [...prev, { role: 'assistant', content: res.reply }]);
    } catch (e) {
      // Mock coach responses
      setTimeout(() => {
        setChatMessages(prev => [...prev, {
          role: 'assistant', 
          content: `I've analyzed your progress metrics. You have completed ${progressMetrics.completion_percentage}% of your roadmap. Maintain consistency on your Morning Deep Work blocks. Your risk level remains Low.`
        }]);
      }, 800);
    } finally {
      setIsCoachLoading(false);
    }
  };

  // Adaptive Replanning preview
  const handleTriggerReplan = async () => {
    setIsReplanningLoading(true);
    try {
      const res = await api.post<any>(`/goals/${activeGoalId}/replan`, {
        replanning_mode: replanMode,
        new_hours_per_week: Number(replanHours)
      }, token);
      setReplanPreview(res);
      addLog("Adaptive replan preview generated.");
    } catch (e) {
      // Local preview fallback
      setTimeout(() => {
        setReplanPreview({
          roadmap_health_score: 95,
          completion_probability: 90,
          goal_completion_forecast: "On track (extended by 3 days)",
          risk_analysis: `Hours adjusted to ${replanHours}/week. Redistributed workloads safely.`,
          recommended_adjustments: ["Spill 2 hours into standard buffers", "Delay Phase 3 start date by 2 days"]
        });
      }, 700);
    } finally {
      setIsReplanningLoading(false);
    }
  };

  // Apply Replan (Checkpoint 3)
  const handleApplyReplan = async () => {
    try {
      const res = await api.post<any>(`/goals/${activeGoalId}/apply-replan`, {
        replanning_mode: replanMode,
        new_hours_per_week: Number(replanHours)
      }, token);
      loadActiveScheduleDetails(res.schedule);
      setReplanPreview(null);
      setActiveTab('dashboard');
      addLog("Replanned version successfully applied!");
    } catch (e) {
      // Apply locally
      if (replanPreview) {
        setScheduleAnalysis((prev: any) => ({
          ...prev,
          confidence_score: replanPreview.completion_probability,
          goal_completion_forecast: replanPreview.goal_completion_forecast,
          deadline_feasibility_analysis: replanPreview.risk_analysis
        }));
      }
      setReplanPreview(null);
      setActiveTab('dashboard');
      addLog("Applied fallback reschedule adjustments locally.");
    }
  };

  // Topological sorting and grid layout mapping for Visual DAG Graph
  const isTaskBlocked = (alias: string) => {
    const prerequisites = planDeps.filter(d => d.task_id_alias === alias).map(d => d.depends_on_alias);
    if (prerequisites.length === 0) return false;
    return prerequisites.some(pre => {
      const preTask = activeTasks.find(at => at.task_id_alias === pre);
      return preTask ? !preTask.is_completed : true;
    });
  };

  const getDagLayout = () => {
    if (!activeTasks || activeTasks.length === 0) {
      return { nodes: [], edges: [], width: 800, height: 400 };
    }

    const taskMap = new Map<string, any>();
    activeTasks.forEach(t => taskMap.set(t.task_id_alias, t));

    const levels = new Map<string, number>();
    activeTasks.forEach(t => levels.set(t.task_id_alias, 0));
    
    let changed = true;
    let iterations = 0;
    while (changed && iterations < 100) {
      changed = false;
      iterations++;
      planDeps.forEach(dep => {
        const fromLevel = levels.get(dep.depends_on_alias) ?? 0;
        const toLevel = levels.get(dep.task_id_alias) ?? 0;
        if (toLevel <= fromLevel) {
          levels.set(dep.task_id_alias, fromLevel + 1);
          changed = true;
        }
      });
    }

    const columns: string[][] = [];
    levels.forEach((level, alias) => {
      if (!columns[level]) columns[level] = [];
      columns[level].push(alias);
    });

    const activeColumns = columns.filter(col => col && col.length > 0);

    const colWidth = 240;
    const rowHeight = 110;
    const xOffset = 80;
    const yOffset = 50;
    
    const nodes: any[] = [];
    const nodeCoords = new Map<string, { x: number; y: number }>();

    const maxRows = Math.max(...activeColumns.map(col => col.length));
    const height = Math.max(400, maxRows * rowHeight + yOffset * 2);
    const width = Math.max(800, activeColumns.length * colWidth + xOffset * 2);

    activeColumns.forEach((colTasks, colIdx) => {
      const x = xOffset + colIdx * colWidth;
      const totalColHeight = colTasks.length * rowHeight;
      const colYOffset = (height - totalColHeight) / 2;

      colTasks.sort().forEach((alias, rowIdx) => {
        const y = colYOffset + rowIdx * rowHeight + (rowHeight / 2);
        const task = taskMap.get(alias);
        if (task) {
          nodes.push({
            id: alias,
            name: task.name,
            allocated_hours: task.allocated_hours,
            is_completed: task.is_completed,
            phase_name: task.phase_name,
            x,
            y
          });
          nodeCoords.set(alias, { x, y });
        }
      });
    });

    const edges: any[] = [];
    planDeps.forEach(dep => {
      const fromCoord = nodeCoords.get(dep.depends_on_alias);
      const toCoord = nodeCoords.get(dep.task_id_alias);
      const fromTask = taskMap.get(dep.depends_on_alias);
      const toTask = taskMap.get(dep.task_id_alias);
      
      if (fromCoord && toCoord) {
        edges.push({
          id: `${dep.depends_on_alias}-${dep.task_id_alias}`,
          from: fromCoord,
          to: toCoord,
          fromAlias: dep.depends_on_alias,
          toAlias: dep.task_id_alias,
          isCompleted: (fromTask?.is_completed && toTask?.is_completed)
        });
      }
    });

    return { nodes, edges, width, height };
  };

  return (
    <div className="min-h-screen flex flex-col text-slate-100">
      
      {/* 1. Header Branding Navigation */}
      <header className="border-b border-slate-800 bg-[#0f172a]/60 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Target className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">Agent OnboardX</h1>
            <p className="text-[10px] text-indigo-400 font-semibold uppercase tracking-widest">AI Goal Operating System</p>
          </div>
        </div>

        {token && (
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700">
              <User className="h-4 w-4 text-indigo-400" />
              <span className="text-xs font-semibold text-slate-300">{userEmail}</span>
            </div>
            <button 
              onClick={logout}
              className="text-xs font-medium text-slate-400 hover:text-red-400 transition"
            >
              Sign Out
            </button>
          </div>
        )}
      </header>

      {/* Main Container */}
      <main className="flex-1 flex flex-col">
        
        {/* ==========================================
            UNAUTHENTICATED GATEWAY CARD
            ========================================== */}
        {!token && (
          <div className="flex-grow flex items-center justify-center p-6 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-950/20 via-[#0b0f19] to-[#0b0f19]">
            <div className="w-full max-w-md glass-panel p-8 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-full filter blur-[60px] opacity-20 pointer-events-none" />
              
              <div className="text-center mb-8">
                <span className="px-3 py-1 rounded-full text-[10px] font-bold tracking-wider bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 uppercase">
                  Production Version 1.0
                </span>
                <h2 className="text-3xl font-extrabold tracking-tight mt-4 gradient-text">Welcome to OnboardX</h2>
                <p className="text-sm text-slate-400 mt-2">
                  Transform outcomes through LangGraph-powered AI stateful coaching.
                </p>
              </div>

              {authError && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-300 text-xs p-3 rounded-lg mb-6 flex items-center space-x-2">
                  <ShieldAlert className="h-4 w-4" />
                  <span>{authError}</span>
                </div>
              )}

              <form onSubmit={handleAuth} className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Email Address</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3.5 h-4 w-4 text-slate-500" />
                    <input 
                      type="email" 
                      value={emailInput}
                      onChange={e => setEmailInput(e.target.value)}
                      placeholder="you@example.com"
                      className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm focus:outline-none focus:border-indigo-500 transition text-slate-100"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3.5 h-4 w-4 text-slate-500" />
                    <input 
                      type="password" 
                      value={passwordInput}
                      onChange={e => setPasswordInput(e.target.value)}
                      placeholder="••••••••"
                      className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm focus:outline-none focus:border-indigo-500 transition text-slate-100"
                      required
                    />
                  </div>
                </div>

                <button 
                  type="submit" 
                  className="w-full py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm transition shadow-lg shadow-indigo-500/20 active:translate-y-[1px]"
                >
                  {authMode === 'login' ? 'Sign In' : 'Create Account'}
                </button>
              </form>

              <div className="text-center mt-6">
                <button 
                  onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                >
                  {authMode === 'login' ? "Don't have an account? Sign Up" : 'Already have an account? Log In'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ==========================================
            STAGE 1: PROFILE ONBOARDING WIZARD
            ========================================== */}
        {token && !profile && (
          <div className="flex-grow flex items-center justify-center p-6 bg-slate-950/20">
            <div className="w-full max-w-lg glass-panel p-8 relative">
              
              {/* Onboarding wizard step indicator */}
              <div className="flex justify-between items-center mb-8">
                <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Step {onboardingStep} of 3</span>
                <div className="flex space-x-1">
                  {[1, 2, 3].map(step => (
                    <div 
                      key={step} 
                      className={`h-1.5 w-6 rounded-full transition ${step <= onboardingStep ? 'bg-indigo-500' : 'bg-slate-800'}`} 
                    />
                  ))}
                </div>
              </div>

              {onboardingStep === 1 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold tracking-tight">Who are you?</h2>
                    <p className="text-xs text-slate-400 mt-1">Select the persona archetype that fits your profile.</p>
                  </div>
                  <div className="space-y-2">
                    {['Student', 'Working Professional', 'Founder', 'Freelancer', 'Job Seeker'].map(role => (
                      <button
                        key={role}
                        onClick={() => setSelectedRole(role)}
                        className={`w-full p-4 rounded-xl text-left border text-sm font-semibold transition ${selectedRole === role ? 'bg-indigo-500/10 border-indigo-500 text-indigo-300' : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:bg-slate-900/80'}`}
                      >
                        {role}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {onboardingStep === 2 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold tracking-tight">What is your core focus slot?</h2>
                    <p className="text-xs text-slate-400 mt-1">We schedule workloads around your productivity styles.</p>
                  </div>
                  <div className="space-y-2">
                    {['Morning Focus', 'Evening Sprints', 'Pomodoro intervals', 'Deep Work Block'].map(style => (
                      <button
                        key={style}
                        onClick={() => setSelectedStyle(style)}
                        className={`w-full p-4 rounded-xl text-left border text-sm font-semibold transition ${selectedStyle === style ? 'bg-indigo-500/10 border-indigo-500 text-indigo-300' : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:bg-slate-900/80'}`}
                      >
                        {style}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {onboardingStep === 3 && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold tracking-tight">Set Availability & Challenges</h2>
                    <p className="text-xs text-slate-400 mt-1">Identify your constraints to construct safety margin buffers.</p>
                  </div>
                  
                  <div>
                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Weekly availability (Hours)</label>
                    <div className="flex items-center space-x-4">
                      <input 
                        type="range" 
                        min="2" 
                        max="40" 
                        value={hoursInput} 
                        onChange={e => setHoursInput(Number(e.target.value))}
                        className="flex-1 accent-indigo-500 h-1.5 bg-slate-800 rounded-lg"
                      />
                      <span className="w-16 text-center text-sm font-extrabold bg-slate-900/50 py-1.5 px-3 rounded-lg border border-slate-800">{hoursInput} hrs</span>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Your biggest consistency roadblock?</label>
                    <input 
                      type="text"
                      value={challengeInput}
                      onChange={e => setChallengeInput(e.target.value)}
                      placeholder="e.g. Procrastination, busy weekday schedules..."
                      className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3 px-4 text-sm focus:outline-none focus:border-indigo-500 transition text-slate-100"
                    />
                  </div>
                </div>
              )}

              {/* Wizard navigation bar */}
              <div className="mt-8 pt-4 border-t border-slate-900 flex justify-between">
                {onboardingStep > 1 ? (
                  <button 
                    onClick={() => setOnboardingStep(onboardingStep - 1)}
                    className="px-5 py-2.5 rounded-lg border border-slate-800 hover:bg-slate-900/50 text-xs font-semibold"
                  >
                    Back
                  </button>
                ) : <div />}

                {onboardingStep < 3 ? (
                  <button 
                    onClick={() => setOnboardingStep(onboardingStep + 1)}
                    disabled={onboardingStep === 1 && !selectedRole || onboardingStep === 2 && !selectedStyle}
                    className="px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-xs font-semibold text-white flex items-center space-x-1"
                  >
                    <span>Continue</span>
                    <ChevronRight className="h-4 w-4" />
                  </button>
                ) : (
                  <button 
                    onClick={handleProfileOnboarding}
                    className="px-6 py-2.5 rounded-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-xs font-semibold text-white flex items-center space-x-1"
                  >
                    <span>Complete Profile</span>
                    <Sparkles className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ==========================================
            STAGE 2: GOALS LANDING OR GOAL INTAKE & DISCOVERY
            ========================================== */}
        {token && profile && goalStatus === 'none' && (
          <div className="flex-grow p-8 max-w-5xl mx-auto w-full space-y-8">
            {(!isCreatingNewGoal && goalsList.length > 0) ? (
              // 2a. Goals directory landing page
              <div className="space-y-8">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800/80 pb-6">
                  <div>
                    <h2 className="text-3xl font-extrabold tracking-tight gradient-text">Your Goal Operating System</h2>
                    <p className="text-sm text-slate-400 mt-1">Select a goal workspace to track, or define a new outcome strategy.</p>
                  </div>
                  <button
                    onClick={() => setIsCreatingNewGoal(true)}
                    className="px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-xs flex items-center justify-center space-x-2 transition shadow-lg shadow-indigo-500/20 active:translate-y-[1px]"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Create New Goal</span>
                  </button>
                </div>

                {isLoadingGoals ? (
                  <div className="flex flex-col items-center justify-center py-12 space-y-2">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-500" />
                    <span className="text-xs text-slate-500">Loading goals directory...</span>
                  </div>
                ) : (
                  <div className="grid md:grid-cols-2 gap-6">
                    {goalsList.map((goal) => {
                      const isActive = goal.status === 'active';
                      const isDrafting = goal.status === 'drafting';
                      const isStrategy = goal.status === 'strat_selection';
                      const isPlanning = goal.status === 'planning' || goal.status === 'readiness_check';
                      
                      let badgeColor = 'bg-slate-800 border-slate-700 text-slate-400';
                      let statusText = 'Drafting Context';
                      if (isActive) {
                        badgeColor = 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400';
                        statusText = 'Active Execution';
                      } else if (isStrategy) {
                        badgeColor = 'bg-purple-500/10 border-purple-500/30 text-purple-400';
                        statusText = 'Strategy Selection';
                      } else if (isPlanning) {
                        badgeColor = 'bg-amber-500/10 border-amber-500/30 text-amber-400';
                        statusText = 'Blueprint Planning';
                      }

                      return (
                        <div
                          key={goal.id}
                          className="glass-panel p-6 flex flex-col justify-between hover:border-slate-700 hover:shadow-lg hover:shadow-indigo-500/5 transition duration-300 group"
                        >
                          <div className="space-y-4">
                            <div className="flex items-start justify-between gap-4">
                              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border uppercase tracking-wider ${badgeColor}`}>
                                {statusText}
                              </span>
                              <span className="text-[10px] text-slate-500 font-mono">
                                {new Date(goal.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                              </span>
                            </div>
                            <h3 className="text-lg font-bold text-slate-200 leading-snug group-hover:text-white transition">
                              {goal.title}
                            </h3>
                          </div>

                          <button
                            onClick={() => handleSelectGoal(goal)}
                            className={`w-full mt-6 py-3 rounded-xl border text-xs font-semibold flex items-center justify-center space-x-2 transition ${isActive ? 'bg-indigo-600 hover:bg-indigo-500 border-indigo-600 text-white' : 'bg-slate-900/50 hover:bg-indigo-500/5 border-slate-800 hover:border-indigo-500 text-slate-300'}`}
                          >
                            <span>{isActive ? 'Enter Cockpit Workspace' : 'Resume Planning Flow'}</span>
                            <ArrowRight className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ) : (
              // 2b. Goal intake & discovery form
              <div className="max-w-lg mx-auto glass-panel p-8 text-center space-y-6">
                <div className="h-14 w-14 rounded-full bg-indigo-500/10 flex items-center justify-center mx-auto border border-indigo-500/20">
                  <Compass className="h-8 w-8 text-indigo-400" />
                </div>
                
                <div>
                  <h2 className="text-3xl font-extrabold tracking-tight gradient-text">What would you like to achieve?</h2>
                  <p className="text-sm text-slate-400 mt-2">
                    Define your goal, and our stateful LangGraph workflow will sequence and track your execution path.
                  </p>
                </div>

                <form onSubmit={handleGoalSubmit} className="space-y-4 text-left">
                  <textarea 
                    value={goalTitle}
                    onChange={e => setGoalTitle(e.target.value)}
                    placeholder="e.g. Build a FastAPI SaaS in 30 days, train for a half-marathon, learn intermediate conversational Spanish..."
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl p-4 text-sm focus:outline-none focus:border-indigo-500 transition text-slate-100 min-h-[100px] resize-none"
                    required
                  />
                  
                  <div className="flex gap-4">
                    {goalsList.length > 0 && (
                      <button 
                        type="button"
                        onClick={() => setIsCreatingNewGoal(false)}
                        className="flex-1 py-3.5 rounded-xl border border-slate-800 hover:bg-slate-900/50 text-slate-400 font-semibold text-sm transition"
                      >
                        Cancel
                      </button>
                    )}
                    <button 
                      type="submit" 
                      className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition flex items-center justify-center space-x-2 shadow-lg shadow-indigo-500/10"
                    >
                      <span>Initialize Goal Discovery</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        )}

        {/* ==========================================
            LLM LOADING RUN STATE
            ========================================== */}
        {token && goalStatus === 'analyzing' && (
          <div className="flex-grow flex flex-col items-center justify-center p-6 text-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500" />
            <h3 className="text-lg font-bold text-slate-300">LangGraph Nodes Executing...</h3>
            <p className="text-xs text-slate-500 max-w-xs">Querying Gemini API, performing gap assessments, and scheduling execution paths...</p>
          </div>
        )}

        {/* ==========================================
            STAGE 3: DYNAMIC CONTEXT QUESTIONNAIRE
            ========================================== */}
        {token && goalStatus === 'questions' && (
          <div className="flex-grow flex items-center justify-center p-6">
            <div className="w-full max-w-xl glass-panel p-8 space-y-6">
              
              <button
                onClick={handleBackToGoals}
                className="flex items-center space-x-1 text-xs text-indigo-400 hover:text-indigo-300 font-semibold mb-2"
              >
                <ChevronLeft className="h-4 w-4" />
                <span>Back to Goals Directory</span>
              </button>

              {/* Ingestion wizard progression tracker */}
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Question {currentQuestionIdx + 1} of {intelQuestions.length}</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 uppercase">
                  Goal Intelligence Ingest
                </span>
              </div>

              <div className="p-5 rounded-xl border border-slate-800/80 bg-slate-900/30">
                <h4 className="text-lg font-semibold text-slate-200">{intelQuestions[currentQuestionIdx]}</h4>
              </div>

              <textarea 
                value={currentAnswer}
                onChange={e => setCurrentAnswer(e.target.value)}
                placeholder="Type your response here..."
                className="w-full bg-slate-900/50 border border-slate-800 rounded-xl p-4 text-sm focus:outline-none focus:border-indigo-500 transition text-slate-100 min-h-[120px] resize-none"
              />

              <button 
                onClick={handleAnswerSubmit}
                disabled={!currentAnswer.trim()}
                className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition flex items-center justify-center space-x-2 shadow-lg shadow-indigo-500/10 disabled:opacity-50"
              >
                <span>{currentQuestionIdx + 1 === intelQuestions.length ? 'Finalize Context Ingest' : 'Next Question'}</span>
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {/* ==========================================
            STAGE 4: STRATEGY AUDIT SELECTION
            ========================================== */}
        {token && goalStatus === 'strategies' && (
          <div className="flex-grow p-8 max-w-5xl mx-auto space-y-8">
            <button
              onClick={handleBackToGoals}
              className="flex items-center space-x-1 text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
            >
              <ChevronLeft className="h-4 w-4" />
              <span>Back to Goals Directory</span>
            </button>

            <div className="text-center">
              <span className="px-3 py-1 rounded-full text-[10px] font-bold tracking-wider bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 uppercase">
                Checkpoint 1
              </span>
              <h2 className="text-3xl font-extrabold tracking-tight mt-3 gradient-text">Select Strategy Framework</h2>
              <p className="text-sm text-slate-400 mt-2">
                We have generated 3 customized strategy directions. Review recommended framework and select to construct blueprints.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {strategies.map((strat, idx) => (
                <div 
                  key={idx} 
                  className={`glass-panel p-6 flex flex-col justify-between relative overflow-hidden transition hover:-translate-y-1 ${strat.is_recommended ? 'border-indigo-500/40 shadow-lg shadow-indigo-500/5' : ''}`}
                >
                  {strat.is_recommended && (
                    <span className="absolute top-3 right-3 px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest bg-indigo-500 text-white shadow-md shadow-indigo-500/20">
                      Recommended
                    </span>
                  )}
                  
                  <div className="space-y-4">
                    <h3 className="text-lg font-bold text-slate-200">{strat.title}</h3>
                    <p className="text-xs text-slate-400 leading-relaxed">{strat.description}</p>
                    
                    <div className="space-y-2 border-t border-slate-800/80 pt-4">
                      <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Pros</h4>
                      <ul className="text-xs space-y-1">
                        {strat.pros.map((pro: string, i: number) => (
                          <li key={i} className="text-emerald-400 flex items-start space-x-1">
                            <span className="mt-0.5">•</span>
                            <span>{pro}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="space-y-2">
                      <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Cons</h4>
                      <ul className="text-xs space-y-1">
                        {strat.cons.map((con: string, i: number) => (
                          <li key={i} className="text-red-400 flex items-start space-x-1">
                            <span className="mt-0.5">•</span>
                            <span>{con}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <button 
                    onClick={() => handleSelectStrategy(strat.strategy_key)}
                    className="w-full mt-6 py-2.5 rounded-lg border border-slate-700 hover:border-indigo-500 text-xs font-semibold transition bg-slate-900/50 hover:bg-indigo-500/5 text-slate-200"
                  >
                    Select Strategy
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ==========================================
            STAGE 5: EXECUTION PLAN APPROVAL (BLUEPRINT)
            ========================================== */}
        {token && goalStatus === 'planning' && (
          <div className="flex-grow p-8 max-w-4xl mx-auto space-y-8">
            <button
              onClick={handleBackToGoals}
              className="flex items-center space-x-1 text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
            >
              <ChevronLeft className="h-4 w-4" />
              <span>Back to Goals Directory</span>
            </button>

            <div className="text-center">
              <span className="px-3 py-1 rounded-full text-[10px] font-bold tracking-wider bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 uppercase">
                Checkpoint 2
              </span>
              <h2 className="text-3xl font-extrabold tracking-tight mt-3 gradient-text">Review Execution Blueprint</h2>
              <p className="text-sm text-slate-400 mt-2">
                We have generated a sequential task roadmap. Approve to build and distribute daily calendar blocks.
              </p>
            </div>

            {/* Ingestion Diagnostics and Readiness summary */}
            <div className="grid md:grid-cols-3 gap-6">
              <div className="glass-panel p-6 text-center border-l-4 border-emerald-500">
                <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Overall Readiness</span>
                <div className="text-4xl font-extrabold text-emerald-400 mt-2">{readinessScore}%</div>
                <p className="text-[10px] text-slate-500 mt-2 leading-relaxed">Score calculated based on availability and skills alignment.</p>
              </div>

              <div className="glass-panel p-6 md:col-span-2 space-y-2 text-xs">
                <h4 className="font-bold text-slate-300 uppercase tracking-widest text-[10px]">Identified Readiness Roadblocks</h4>
                {readinessDetails?.identified_gaps.map((gap: string, idx: number) => (
                  <div key={idx} className="flex items-center space-x-2 text-slate-400 bg-slate-900/30 p-2 rounded-lg border border-slate-900">
                    <AlertTriangle className="h-4 w-4 text-amber-400 flex-shrink-0" />
                    <span>{gap}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Checklist Blueprint rendering */}
            <div className="glass-panel p-8 space-y-6">
              <h3 className="text-lg font-bold text-slate-200 pb-3 border-b border-slate-900">Task Sequencing Checklist</h3>
              
              <div className="space-y-4">
                {planTasks.map((t, idx) => (
                  <div key={idx} className="flex items-start justify-between p-4 rounded-xl bg-slate-900/30 border border-slate-900">
                    <div className="flex space-x-3 items-start">
                      <span className="text-xs font-bold text-indigo-400 px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 uppercase mt-0.5">{t.task_id_alias}</span>
                      <div>
                        <h4 className="text-sm font-semibold text-slate-200">{t.name}</h4>
                        <p className="text-[10px] text-slate-500 mt-1">{t.phase_name}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-1 text-slate-400 text-xs font-semibold">
                      <Clock className="h-3.5 w-3.5 text-indigo-400" />
                      <span>{t.allocated_hours} hrs</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-center pt-4">
              <button 
                onClick={handleApproveBlueprint}
                className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold rounded-xl text-sm transition shadow-lg shadow-indigo-500/20 active:translate-y-[1px]"
              >
                Approve Blueprint & Allocate Schedule
              </button>
            </div>
          </div>
        )}

        {/* ==========================================
            STAGE 6: ACTIVE SaaS DASHBOARD COCKPIT
            ========================================== */}
        {token && profile && goalStatus === 'active' && (
          <div className="flex-grow flex flex-col md:flex-row">
            
            {/* 6a. Side Control Navigation */}
            <aside className="w-full md:w-64 bg-[#0f172a]/40 border-r border-slate-800/80 p-5 space-y-8 flex flex-col justify-between">
              
              <div className="space-y-6">
                
                {/* Back to Goals button */}
                <button
                  onClick={handleBackToGoals}
                  className="flex items-center space-x-2 px-3 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-indigo-300 hover:bg-slate-900/30 w-full transition border border-transparent hover:border-slate-800/80"
                >
                  <ArrowLeft className="h-4 w-4" />
                  <span>Back to Goals</span>
                </button>

                {/* User status widgets */}
                <div className="glass-panel p-4 flex items-center justify-between border-indigo-500/20 bg-indigo-950/5">
                  <div className="flex items-center space-x-2">
                    <Flame className="h-5 w-5 text-amber-500 fill-amber-500 animate-pulse" />
                    <div>
                      <div className="text-xs font-black uppercase text-slate-500 tracking-wider">Active Streak</div>
                      <div className="text-base font-extrabold text-amber-500">{progressMetrics.streak_count} Days</div>
                    </div>
                  </div>
                </div>

                {/* Dashboard Tab Buttons */}
                <nav className="space-y-1.5">
                  {[
                    { id: 'dashboard', label: 'Goals Cockpit', icon: Target },
                    { id: 'timeline', label: 'Gantt Timeline', icon: BarChart2 },
                    { id: 'calendar', label: 'Daily Sprints', icon: Calendar },
                    { id: 'coach', label: 'AI Coach Hub', icon: MessageSquare },
                    { id: 'replanning', label: 'Replanning Center', icon: RefreshCw },
                  ].map(tab => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-xs font-semibold transition ${activeTab === tab.id ? 'bg-indigo-500/10 text-indigo-300 border-l-4 border-indigo-500' : 'text-slate-400 hover:bg-slate-900/30'}`}
                      >
                        <Icon className="h-4 w-4" />
                        <span>{tab.label}</span>
                      </button>
                    );
                  })}
                </nav>

              </div>

              {/* System Warning Console Log (Hackathon Diagnostic) */}
              <div className="bg-black/40 border border-slate-900 rounded-xl p-3 text-[10px] font-mono text-indigo-400 space-y-1 max-h-[140px] overflow-y-auto">
                <div className="text-slate-500 font-bold uppercase tracking-wider border-b border-slate-900 pb-1 mb-1">System Console</div>
                {systemLogs.length === 0 ? <div className="italic text-slate-600">No events logged.</div> : null}
                {systemLogs.map((log, idx) => (
                  <div key={idx} className="leading-tight">{`> ${log}`}</div>
                ))}
              </div>

            </aside>

            {/* 6b. Main Views Section */}
            <section className="flex-1 p-6 overflow-y-auto bg-[#0b0f19] max-w-6xl">
              
              {/* TAB 1: DASHBOARD VIEW */}
              {activeTab === 'dashboard' && (
                <div className="space-y-6">
                  <div className="flex justify-between items-center">
                    <h2 className="text-2xl font-bold tracking-tight">Active Goals Cockpit</h2>
                    <span className="text-xs text-slate-400 font-semibold">{scheduleAnalysis?.goal_completion_forecast}</span>
                  </div>

                  {/* Top Stats panel row */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="glass-panel p-4 text-center">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Progress</span>
                      <div className="text-3xl font-extrabold text-indigo-400 mt-1">{progressMetrics.completion_percentage}%</div>
                    </div>
                    <div className="glass-panel p-4 text-center">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Goal Health</span>
                      <div className="text-3xl font-extrabold text-emerald-400 mt-1">{progressMetrics.health_score}%</div>
                    </div>
                    <div className="glass-panel p-4 text-center">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Logged Hours</span>
                      <div className="text-3xl font-extrabold text-amber-500 mt-1">{progressMetrics.time_spent_total} hrs</div>
                    </div>
                    <div className="glass-panel p-4 text-center">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Target Hours</span>
                      <div className="text-3xl font-extrabold text-slate-300 mt-1">{progressMetrics.allocated_hours_total} hrs</div>
                    </div>
                  </div>

                  {/* Task Board Board panel */}
                  <div className="glass-panel p-6 space-y-6">
                    <h3 className="text-base font-bold text-slate-200">Execution Task Board</h3>
                    <div className="space-y-2">
                      {activeTasks.map((t, idx) => (
                        <div 
                          key={idx} 
                          onClick={() => handleToggleTask(t.task_id_alias, !t.is_completed)}
                          className={`flex items-center justify-between p-3.5 rounded-xl border transition cursor-pointer ${t.is_completed ? 'bg-slate-900/20 border-slate-900 text-slate-500' : 'bg-slate-900/50 border-slate-800/80 text-slate-200 hover:border-slate-700'}`}
                        >
                          <div className="flex items-center space-x-3">
                            {t.is_completed ? (
                              <CheckCircle2 className="h-5 w-5 text-indigo-500" />
                            ) : (
                              <Circle className="h-5 w-5 text-slate-500" />
                            )}
                            <div>
                              <span className={`text-sm font-semibold ${t.is_completed ? 'line-through' : ''}`}>{t.name}</span>
                              <span className="text-[8px] font-bold px-1.5 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400 uppercase tracking-wider ml-3">{t.task_id_alias}</span>
                            </div>
                          </div>
                          
                          <span className="text-xs font-semibold text-slate-400">{t.allocated_hours} hrs</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: TIMELINE (GANTT DAG) VIEW */}
              {activeTab === 'timeline' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold tracking-tight">Milestone Dependency DAG</h2>
                    <p className="text-xs text-slate-400 mt-1">Interactive roadmap sequencing paths generated by Planning Engine. Click nodes to toggle completion.</p>
                  </div>

                  {(() => {
                    const { nodes, edges, width, height } = getDagLayout();
                    if (nodes.length === 0) {
                      return (
                        <div className="glass-panel p-12 text-center text-slate-500 italic text-sm">
                          No tasks loaded.
                        </div>
                      );
                    }
                    return (
                      <div className="w-full overflow-x-auto overflow-y-auto border border-slate-800/80 bg-[#070b13] rounded-2xl p-4 shadow-inner max-h-[600px] scrollbar-thin scrollbar-thumb-slate-800">
                        <div style={{ width: width, height: height, position: 'relative' }} className="mx-auto">
                          <svg width={width} height={height} className="absolute inset-0 pointer-events-none">
                            <defs>
                              <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#334155" />
                              </marker>
                              <marker id="arrow-active" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#6366f1" />
                              </marker>
                            </defs>
                            
                            {/* Draw Edges */}
                            {edges.map(edge => {
                              const fromX = edge.from.x + 95;
                              const fromY = edge.from.y;
                              const toX = edge.to.x - 95;
                              const toY = edge.to.y;
                              
                              const controlX = (fromX + toX) / 2;
                              const pathD = `M ${fromX} ${fromY} C ${controlX} ${fromY}, ${controlX} ${toY}, ${toX} ${toY}`;
                              
                              const isEdgeCompleted = edge.isCompleted;
                              
                              return (
                                <path
                                  key={edge.id}
                                  d={pathD}
                                  fill="none"
                                  stroke={isEdgeCompleted ? '#6366f1' : '#1e293b'}
                                  strokeWidth={isEdgeCompleted ? 2.5 : 1.5}
                                  markerEnd={isEdgeCompleted ? 'url(#arrow-active)' : 'url(#arrow)'}
                                  className="transition duration-300"
                                />
                              );
                            })}
                          </svg>
                          
                          {/* Render Node Cards */}
                          {nodes.map(node => {
                            const isBlocked = isTaskBlocked(node.id);
                            const cardStyle = node.is_completed
                              ? 'border-emerald-500/20 bg-emerald-950/5 hover:border-emerald-500/40 text-slate-400'
                              : isBlocked
                              ? 'border-slate-800/80 bg-slate-900/10 opacity-40 text-slate-500 cursor-not-allowed'
                              : 'border-indigo-500 bg-indigo-950/10 shadow-lg shadow-indigo-500/5 hover:border-indigo-400 text-slate-200';
                              
                            return (
                              <div
                                key={node.id}
                                onClick={() => {
                                  if (!isBlocked) {
                                    handleToggleTask(node.id, !node.is_completed);
                                  }
                                }}
                                style={{
                                  position: 'absolute',
                                  left: node.x - 95,
                                  top: node.y - 45,
                                  width: 190,
                                  height: 90,
                                }}
                                className={`border rounded-xl p-3 flex flex-col justify-between transition duration-200 cursor-pointer select-none active:scale-[0.98] ${cardStyle}`}
                              >
                                <div className="flex items-start justify-between gap-1">
                                  <span className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded uppercase ${node.is_completed ? 'bg-emerald-500/10 text-emerald-400' : isBlocked ? 'bg-slate-800 text-slate-500' : 'bg-indigo-500/10 text-indigo-400'}`}>
                                    {node.id}
                                  </span>
                                  <span className="text-[9px] font-semibold text-slate-500">
                                    {node.allocated_hours} hrs
                                  </span>
                                </div>
                                
                                <h4 className="text-[11px] font-bold tracking-tight line-clamp-2 leading-tight">
                                  {node.name}
                                </h4>
                                
                                <div className="text-[8px] font-semibold text-slate-500 uppercase tracking-widest truncate">
                                  {node.phase_name}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })()}
                </div>
              )}

              {/* TAB 3: CALENDAR VIEW */}
              {activeTab === 'calendar' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold tracking-tight">Deterministic Daily Sprints</h2>
                    <p className="text-xs text-slate-400 mt-1">Calendar time slots calculated locally in Python based on productivity slots.</p>
                  </div>

                  <div className="space-y-4">
                    {dailySchedule.map((day, idx) => (
                      <div key={idx} className="glass-panel p-5 space-y-3">
                        <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                          <h4 className="text-sm font-bold text-slate-200">{day.day_name} (Week {day.week_number})</h4>
                          <span className="text-xs font-semibold text-slate-400">{day.total_hours} hrs scheduled</span>
                        </div>
                        
                        <div className="space-y-2">
                          {day.time_blocks.length === 0 ? (
                            <div className="text-xs text-slate-500 italic py-2">Buffer Rest Day</div>
                          ) : null}
                          {day.time_blocks.map((block: any, bidx: number) => {
                            const isCompleted = activeTasks.find(at => at.task_id_alias === block.task_id)?.is_completed;
                            return (
                              <div 
                                key={bidx} 
                                className={`flex justify-between items-center p-3 rounded-lg border-l-4 text-xs ${isCompleted ? 'bg-slate-900/10 border-slate-900 border-l-slate-700 text-slate-500' : 'bg-slate-900/30 border-slate-800 border-l-indigo-500 text-slate-300'}`}
                              >
                                <div>
                                  <span className="font-black text-slate-500 block text-[9px] uppercase tracking-widest">{block.type}</span>
                                  <span className={`font-semibold ${isCompleted ? 'line-through' : ''}`}>{block.name}</span>
                                </div>
                                <div className="text-right">
                                  <span className="font-bold text-indigo-400 block">{block.time_slot}</span>
                                  <span className="text-[10px] text-slate-500">{block.duration_hours} hrs</span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* TAB 4: AI COACH HUB VIEW */}
              {activeTab === 'coach' && (
                <div className="space-y-6 flex flex-col h-[520px]">
                  <div>
                    <h2 className="text-2xl font-bold tracking-tight">AI Coaching Hub</h2>
                    <p className="text-xs text-slate-400 mt-1">Interactive stateful guidance direct-connected to Gemini Orchestrator.</p>
                  </div>

                  <div className="flex-1 glass-panel p-4 flex flex-col justify-between overflow-hidden">
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2 mb-4 scroll-smooth">
                      {chatMessages.map((msg, idx) => (
                        <div 
                          key={idx} 
                          className={`max-w-[80%] p-3.5 rounded-xl text-xs leading-relaxed ${msg.role === 'assistant' ? 'bg-indigo-500/10 text-slate-200 self-start mr-auto border border-indigo-500/20' : 'bg-slate-800 text-slate-100 self-end ml-auto'}`}
                        >
                          {msg.content}
                        </div>
                      ))}
                      {isCoachLoading && (
                        <div className="text-xs text-slate-500 italic flex items-center space-x-1">
                          <span className="animate-pulse">AI Coach is thinking...</span>
                        </div>
                      )}
                    </div>

                    <div className="flex space-x-2 pt-3 border-t border-slate-900">
                      <input 
                        type="text" 
                        value={chatInput}
                        onChange={e => setChatInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSendCoachMsg()}
                        placeholder="Ask your coach for replanning guidance..."
                        className="flex-1 bg-slate-900/50 border border-slate-800 rounded-xl py-2.5 px-4 text-xs focus:outline-none focus:border-indigo-500 transition text-slate-100"
                      />
                      <button 
                        onClick={handleSendCoachMsg}
                        className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition"
                      >
                        Send
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 5: REPLANNING CENTER */}
              {activeTab === 'replanning' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold tracking-tight">Adaptive Replanning Center</h2>
                    <p className="text-xs text-slate-400 mt-1">Re-evaluate availability limits, calculate delays, and update calendar allocation bounds.</p>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="glass-panel p-6 space-y-6">
                      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-widest text-[10px]">Adjust Constraints</h3>
                      
                      <div>
                        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Adjust Weekly availability (Hours)</label>
                        <div className="flex items-center space-x-4">
                          <input 
                            type="range" 
                            min="2" 
                            max="40" 
                            value={replanHours} 
                            onChange={e => setReplanHours(Number(e.target.value))}
                            className="flex-1 accent-indigo-500 h-1.5 bg-slate-800 rounded-lg"
                          />
                          <span className="w-16 text-center text-sm font-extrabold bg-slate-900/50 py-1.5 px-3 rounded-lg border border-slate-800">{replanHours} hrs</span>
                        </div>
                      </div>

                      <div>
                        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Replanning Mode</label>
                        <select 
                          value={replanMode}
                          onChange={e => setReplanMode(e.target.value)}
                          className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-2.5 px-3 text-xs focus:outline-none focus:border-indigo-500 text-slate-300"
                        >
                          <option value="Balanced">Balanced (Standard distribution)</option>
                          <option value="Catch Up">Catch Up (Aggressively compress remaining)</option>
                          <option value="Low Stress">Low Stress (Push dates out, lower hours)</option>
                        </select>
                      </div>

                      <button 
                        onClick={handleTriggerReplan}
                        className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-lg transition"
                      >
                        Generate Replan Forecast Preview
                      </button>
                    </div>

                    {/* Replanning preview card */}
                    <div className="glass-panel p-6 flex flex-col justify-between">
                      {isReplanningLoading ? (
                        <div className="flex-grow flex flex-col items-center justify-center space-y-2">
                          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-500" />
                          <span className="text-xs text-slate-500">Recalculating forecast parameters...</span>
                        </div>
                      ) : replanPreview ? (
                        <div className="space-y-4 flex-grow flex flex-col justify-between">
                          <div className="space-y-4">
                            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-widest text-[10px]">Replan Preview Forecast</h3>
                            
                            <div className="grid grid-cols-2 gap-4">
                              <div className="bg-slate-900/40 p-3 rounded-lg border border-slate-900 text-center">
                                <span className="text-[8px] font-black uppercase text-slate-500 tracking-wider">Health Index</span>
                                <div className="text-xl font-bold text-emerald-400 mt-1">{replanPreview.roadmap_health_score}%</div>
                              </div>
                              <div className="bg-slate-900/40 p-3 rounded-lg border border-slate-900 text-center">
                                <span className="text-[8px] font-black uppercase text-slate-500 tracking-wider">Feasibility</span>
                                <div className="text-xl font-bold text-indigo-400 mt-1">{replanPreview.completion_probability}%</div>
                              </div>
                            </div>

                            <div className="space-y-1.5 text-xs text-slate-300">
                              <div className="font-bold text-[10px] uppercase tracking-wider text-slate-500">Timeline Impact</div>
                              <p className="bg-slate-900/20 p-2.5 rounded-lg border border-slate-900/80 leading-relaxed italic">{replanPreview.goal_completion_forecast}</p>
                            </div>

                            <div className="space-y-1.5 text-xs">
                              <div className="font-bold text-[10px] uppercase tracking-wider text-slate-500">Suggested Adjustments</div>
                              {replanPreview.recommended_adjustments.map((adj: string, idx: number) => (
                                <div key={idx} className="flex items-center space-x-1 text-slate-400">
                                  <span>•</span>
                                  <span>{adj}</span>
                                </div>
                              ))}
                            </div>
                          </div>

                          <button 
                            onClick={handleApplyReplan}
                            className="w-full mt-4 py-3 bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-semibold text-xs rounded-lg transition"
                          >
                            Apply Replanned Schedule (Checkpoint 3)
                          </button>
                        </div>
                      ) : (
                        <div className="flex-grow flex flex-col items-center justify-center text-center space-y-2">
                          <RefreshCw className="h-10 w-10 text-slate-700 animate-spin" style={{ animationDuration: '10s' }} />
                          <h4 className="text-xs font-semibold text-slate-500">No Preview Active</h4>
                          <p className="text-[10px] text-slate-600 max-w-xs">Adjust weekly hour limit and request preview to evaluate risk profiles prior to commits.</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

            </section>
          </div>
        )}

      </main>
      
    </div>
  );
}
