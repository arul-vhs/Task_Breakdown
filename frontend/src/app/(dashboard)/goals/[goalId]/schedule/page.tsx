'use client';

import React from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Target, ArrowLeft, ShieldAlert, Calendar, Award, Compass, BarChart, ChevronRight } from 'lucide-react';
import { useWorkflowState } from '../../../../../hooks/useWorkflowState';
import { authService } from '../../../../../services/auth.service';
import { Button } from '../../../../../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../../../components/ui/card';
import { CalendarWrapper } from '../../../../../components/schedule/CalendarWrapper';

export default function SchedulePage() {
  const router = useRouter();
  const params = useParams();
  const goalId = params?.goalId as string;

  // 1. Fetch profile to construct thread ID
  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: authService.getProfile,
  });

  const userId = profile?.user_id;
  const threadId = userId && goalId ? `user_${userId}_goal_${goalId}` : null;

  // 2. Poll workflow state
  const { data: stateData, isLoading: isStateLoading } = useWorkflowState(threadId);

  const state = stateData?.data;
  const currentStage = state?.current_stage;
  const activeSchedule = state?.active_schedule;

  // Auto redirect if workflow stage has advanced past scheduling
  React.useEffect(() => {
    if (currentStage && currentStage !== 'scheduling') {
      if (currentStage === 'strategy_selection') {
        router.push(`/goals/${goalId}/strategy`);
      } else if (currentStage === 'validation') {
        router.push(`/goals/${goalId}/intake`);
      } else if (currentStage === 'roadmap_generation') {
        router.push(`/goals/${goalId}/roadmap`);
      } else if (currentStage === 'execution' || currentStage === 'coaching') {
        router.push(`/goals/${goalId}/progress`);
      }
    }
  }, [currentStage, goalId, router]);

  if (isStateLoading) {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-4">
          <svg className="animate-spin h-8 w-8 text-indigo-500 mx-auto" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-sm text-slate-400 font-medium">Allocating calendar time slots...</p>
        </div>
      </div>
    );
  }

  const analysis = activeSchedule?.schedule_analysis;
  const dailySchedule = activeSchedule?.daily_schedule || [];

  const handleProceed = () => {
    router.push(`/goals/${goalId}/progress`);
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800/80 bg-[#0f172a]/60 backdrop-blur-md px-6 py-4 flex items-center sticky top-0 z-50">
        <button 
          onClick={() => router.push('/dashboard')}
          className="text-slate-400 hover:text-slate-100 transition mr-4 flex items-center space-x-1 text-sm font-semibold"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Dashboard</span>
        </button>
        <div className="flex items-center space-x-2 border-l border-slate-700/50 pl-4">
          <Target className="h-5 w-5 text-indigo-500" />
          <span className="text-sm font-bold">{state?.goal_title || 'Active Goal'}</span>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-8 space-y-8">
        
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-3xl font-extrabold tracking-tight gradient-text">Your Allocated Schedule</h2>
          <p className="text-sm text-slate-400">
            Kahn's sequencing algorithm has mapped your strategy roadmap onto a weekly time-blocked calendar grid.
          </p>
        </div>

        {/* Schedule Analysis Diagnostics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-slate-800/80">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Confidence Forecast</p>
                <h4 className="text-xl font-extrabold text-slate-200 mt-2">{analysis?.confidence_score}% Score</h4>
              </div>
              <div className="h-9 w-9 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 shrink-0">
                <BarChart className="h-4.5 w-4.5" />
              </div>
            </div>
            <p className="text-[11px] text-slate-400 mt-3 leading-normal">{analysis?.goal_completion_forecast}</p>
          </Card>

          <Card className="border-slate-800/80">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Buffer Allocation</p>
                <h4 className="text-xl font-extrabold text-slate-200 mt-2">Time-Blocked</h4>
              </div>
              <div className="h-9 w-9 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 shrink-0">
                <Compass className="h-4.5 w-4.5" />
              </div>
            </div>
            <p className="text-[11px] text-slate-400 mt-3 leading-normal">{analysis?.buffer_time_allocation}</p>
          </Card>

          <Card className="border-slate-800/80">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Feasibility Status</p>
                <h4 className="text-xl font-extrabold text-slate-200 mt-2">Optimal</h4>
              </div>
              <div className="h-9 w-9 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 shrink-0">
                <Calendar className="h-4.5 w-4.5" />
              </div>
            </div>
            <p className="text-[11px] text-slate-400 mt-3 leading-normal">{analysis?.deadline_feasibility_analysis}</p>
          </Card>
        </div>

        {/* Visual Calendar */}
        <CalendarWrapper dailySchedule={dailySchedule} />

        {/* Proceed Button */}
        <div className="flex justify-center">
          <Button
            onClick={handleProceed}
            className="px-8 py-3.5 flex items-center space-x-2 text-sm font-semibold"
          >
            <span>Launch Active Cockpit</span>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </main>
    </div>
  );
}
