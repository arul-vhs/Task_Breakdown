'use client';

import React, { useState } from 'react';
import { useRouter, useParams, usePathname } from 'next/navigation';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Target, ArrowLeft, ShieldAlert, Award, Compass, BarChart, CheckCircle2, Circle, Flame, MessageSquare, AlertTriangle, RefreshCw } from 'lucide-react';
import { useWorkflowState } from '../../../../../hooks/useWorkflowState';
import { authService } from '../../../../../services/auth.service';
import { progressService } from '../../../../../services/progress.service';
import { Button } from '../../../../../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../../../components/ui/card';
import { Progress } from '../../../../../components/ui/progress';

export default function ProgressPage() {
  const router = useRouter();
  const params = useParams();
  const goalId = params?.goalId as string;
  const queryClient = useQueryClient();

  // 1. Fetch profile to construct thread ID
  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: authService.getProfile,
  });

  const userId = profile?.user_id;
  const threadId = userId && goalId ? `user_${userId}_goal_${goalId}` : null;

  // 2. Fetch/Poll state and progress metrics
  const { data: stateData, isLoading: isStateLoading } = useWorkflowState(threadId);

  const { data: progressMetrics, isLoading: isMetricsLoading } = useQuery({
    queryKey: ['progressMetrics', goalId],
    queryFn: () => progressService.getProgressMetrics(goalId),
    enabled: !!goalId,
  });

  // Toggle task completion mutation
  const toggleMutation = useMutation({
    mutationFn: (variables: { taskAlias: string; isCompleted: boolean }) =>
      progressService.updateProgress(goalId, variables.taskAlias, variables.isCompleted),
    onSuccess: (data) => {
      // Optimistically invalidate cache queries to refresh metrics and graph state
      queryClient.invalidateQueries({ queryKey: ['progressMetrics', goalId] });
      queryClient.invalidateQueries({ queryKey: ['workflowState', threadId] });
    },
  });

  const state = stateData?.data;
  const tasks = state?.tasks || [];
  const currentStage = state?.current_stage;

  if (isStateLoading || isMetricsLoading) {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-4">
          <svg className="animate-spin h-8 w-8 text-indigo-500 mx-auto" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-sm text-slate-400 font-medium">Synchronizing cockpit telemetry...</p>
        </div>
      </div>
    );
  }

  // Group tasks by phase
  const phasesMap: Record<string, typeof tasks> = {};
  tasks.forEach((t: any) => {
    const pName = t.phase_name || `Phase ${t.phase_number}`;
    if (!phasesMap[pName]) phasesMap[pName] = [];
    phasesMap[pName].push(t);
  });

  // Calculate dynamic completed status from metrics or local state mapping
  // Since progress metrics holds database count, we cross check with task checklist
  const metrics = progressMetrics || {
    completion_percentage: 0,
    streak_count: 0,
    health_score: 100,
    total_tasks_count: 0,
    completed_tasks_count: 0,
    overdue_tasks_count: 0
  };

  const handleToggle = (taskAlias: string, isCompleted: boolean) => {
    toggleMutation.mutate({ taskAlias, isCompleted });
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      {/* Navigation Header */}
      <header className="border-b border-slate-800/80 bg-[#0f172a]/60 backdrop-blur-md px-6 py-4 flex items-center sticky top-0 z-50">
        <button 
          onClick={() => router.push('/dashboard')}
          className="text-slate-400 hover:text-slate-100 transition mr-4 flex items-center space-x-1 text-sm font-semibold"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Dashboard</span>
        </button>
        <div className="flex items-center space-x-2 border-l border-slate-700/50 pl-4 mr-6">
          <Target className="h-5 w-5 text-indigo-500" />
          <span className="text-sm font-bold">{state?.goal_title || 'Active Goal'}</span>
        </div>

        {/* Cockpit Nav tabs */}
        <div className="flex items-center space-x-1 bg-slate-900/50 p-1 rounded-xl border border-slate-800 shrink-0">
          <Link href={`/goals/${goalId}/progress`} className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-indigo-600 text-white transition">
            Checklist
          </Link>
          <Link href={`/goals/${goalId}/coach`} className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 transition">
            AI Coach
          </Link>
          <Link href={`/goals/${goalId}/replan`} className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 transition">
            Replan
          </Link>
        </div>
      </header>

      {/* Cockpit Content */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-8 space-y-8">
        
        {/* Cockpit Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="border-slate-800/80">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Goal Progress</p>
            <h3 className="text-3xl font-extrabold text-slate-100 mt-2">{metrics.completion_percentage}%</h3>
            <Progress value={metrics.completion_percentage} className="mt-3.5" />
          </Card>

          <Card className="border-slate-800/80">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Streak Count</p>
                <h3 className="text-3xl font-extrabold text-slate-100 mt-2">{metrics.streak_count} Days</h3>
              </div>
              <Flame className="h-7 w-7 text-amber-500 shrink-0" />
            </div>
          </Card>

          <Card className="border-slate-800/80">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Timeline Health</p>
                <h3 className="text-3xl font-extrabold text-slate-100 mt-2">{metrics.health_score}%</h3>
              </div>
              <CheckCircle2 className="h-7 w-7 text-emerald-400 shrink-0" />
            </div>
          </Card>

          <Card className="border-slate-800/80">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Remaining Tasks</p>
                <h3 className="text-3xl font-extrabold text-slate-100 mt-2">
                  {metrics.total_tasks_count - metrics.completed_tasks_count}
                </h3>
              </div>
              <Compass className="h-7 w-7 text-indigo-400 shrink-0" />
            </div>
          </Card>
        </div>

        {/* Task Checklist Grouped by Phase */}
        <div className="space-y-6">
          <h3 className="text-lg font-bold text-slate-100">Tasks Checklist</h3>
          
          <div className="space-y-6">
            {Object.entries(phasesMap).map(([phaseName, phaseTasks]) => (
              <Card key={phaseName} className="border-slate-800/80">
                <CardHeader className="border-b border-slate-800/50 pb-3">
                  <CardTitle className="text-sm font-bold text-indigo-400 capitalize">{phaseName}</CardTitle>
                </CardHeader>
                <CardContent className="divide-y divide-slate-800/40 pt-2">
                  {phaseTasks.map((t: any) => {
                    // Check if task is completed
                    // In progress updates, we query database, let's toggle optimistically
                    const isCompleted = state?.progress?.completed_tasks?.includes(t.task_id_alias) || false;

                    return (
                      <div key={t.task_id_alias} className="py-3.5 flex items-center justify-between text-xs gap-4">
                        <div className="flex items-center space-x-3 select-none cursor-pointer" onClick={() => handleToggle(t.task_id_alias, !isCompleted)}>
                          <div className="shrink-0 text-indigo-500">
                            {isCompleted ? (
                              <CheckCircle2 className="h-5 w-5 fill-indigo-500/10" />
                            ) : (
                              <Circle className="h-5 w-5 text-slate-700" />
                            )}
                          </div>
                          <div className="space-y-1">
                            <span className={`font-semibold ${isCompleted ? 'text-slate-500 line-through' : 'text-slate-200'}`}>
                              {t.name || t.title}
                            </span>
                            {t.description && <p className="text-slate-500 leading-normal max-w-xl">{t.description}</p>}
                          </div>
                        </div>
                        <span className="shrink-0 text-[10px] font-mono text-slate-500 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
                          {t.allocated_hours}h
                        </span>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Routing warnings / instructions if health is low */}
        {metrics.health_score < 50 && (
          <div className="bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs p-4 rounded-xl flex items-center justify-between gap-4">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 shrink-0" />
              <span>Goal health is low. Re-sequencing timelines is advised to prevent milestones slippage.</span>
            </div>
            <Link href={`/goals/${goalId}/replan`}>
              <Button variant="danger" className="py-2 px-4 text-xs font-bold">
                Run Rescheduling
              </Button>
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}
