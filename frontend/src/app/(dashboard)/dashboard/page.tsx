'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { Target, Plus, CheckCircle2, AlertCircle, Compass, Flame, TrendingUp } from 'lucide-react';
import { goalService } from '../../../services/goal.service';
import { authService } from '../../../services/auth.service';
import { useUIStore } from '../../../store/ui.store';
import { useAuthStore } from '../../../store/auth.store';
import { Button } from '../../../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../components/ui/card';

export default function DashboardPage() {
  const router = useRouter();
  const setSelectedGoalId = useUIStore((s) => s.setSelectedGoalId);
  const logout = useAuthStore((s) => s.logout);

  // 1. Fetch user profile - if missing, redirect to onboarding page
  const { data: profile, isLoading: isProfileLoading, error: profileError } = useQuery({
    queryKey: ['profile'],
    queryFn: authService.getProfile,
    retry: false,
  });

  // 2. Fetch goals list
  const { data: goals, isLoading: isGoalsLoading, error: goalsError } = useQuery({
    queryKey: ['goals'],
    queryFn: goalService.listGoals,
    enabled: !!profile, // Only fetch goals once profile exists
  });

  useEffect(() => {
    if (!isProfileLoading && (profileError || !profile)) {
      console.log("No profile detected, routing to new profile onboarding page.");
      router.push('/profile/new');
    }
  }, [profile, isProfileLoading, profileError, router]);

  if (isProfileLoading || isGoalsLoading) {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-4">
          <svg className="animate-spin h-8 w-8 text-indigo-500 mx-auto" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-sm text-slate-400 font-medium animate-pulse">Syncing environment workspace...</p>
        </div>
      </div>
    );
  }

  const handleSelectGoal = (goalId: string, currentStatus: string) => {
    setSelectedGoalId(goalId);
    
    // Map backend status to routes
    if (currentStatus === 'drafting') {
      router.push(`/goals/${goalId}/intake`);
    } else if (currentStatus === 'strat_selection') {
      router.push(`/goals/${goalId}/strategy`);
    } else if (currentStatus === 'readiness_check') {
      router.push(`/goals/${goalId}/validation`);
    } else if (currentStatus === 'planning') {
      router.push(`/goals/${goalId}/roadmap`);
    } else if (currentStatus === 'active') {
      router.push(`/goals/${goalId}/progress`);
    } else {
      router.push(`/goals/${goalId}/intake`);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      
      {/* Navigation Header */}
      <header className="border-b border-slate-800/80 bg-[#0f172a]/60 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Target className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">OnboardX</h1>
            <p className="text-[10px] text-indigo-400 font-semibold uppercase tracking-widest">AI Goal Operating System</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700/50">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            <span className="text-xs font-semibold text-slate-300">{profile?.full_name}</span>
          </div>
          <button 
            onClick={() => logout()}
            className="text-xs font-medium text-slate-400 hover:text-red-400 transition"
          >
            Sign Out
          </button>
        </div>
      </header>

      {/* Content Container */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-8 space-y-8">
        
        {/* Top Header Card */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-tr from-indigo-950/20 via-slate-900/40 to-slate-900/10 p-6 rounded-2xl border border-slate-800/50">
          <div>
            <h2 className="text-2xl font-bold text-slate-100">Welcome back, {profile?.full_name}!</h2>
            <p className="text-sm text-slate-400 mt-1">
              Your workflow style is configured to <span className="text-indigo-400 font-semibold">{profile?.work_style}</span> with <span className="text-indigo-400 font-semibold">{profile?.weekly_hours_available}h/week</span>.
            </p>
          </div>
          <Link href="/goals/new">
            <Button className="shrink-0 flex items-center space-x-2">
              <Plus className="h-4 w-4" />
              <span>Create New Goal</span>
            </Button>
          </Link>
        </div>

        {/* Core Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Goals</p>
                <h3 className="text-3xl font-extrabold text-slate-100 mt-2">{goals?.length || 0}</h3>
              </div>
              <div className="h-10 w-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                <Target className="h-5 w-5" />
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Work Hours Buffer</p>
                <h3 className="text-3xl font-extrabold text-slate-100 mt-2">{profile?.weekly_hours_available}h</h3>
              </div>
              <div className="h-10 w-10 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400">
                <Compass className="h-5 w-5" />
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Streak Calendar</p>
                <h3 className="text-3xl font-extrabold text-slate-100 mt-2">Active</h3>
              </div>
              <div className="h-10 w-10 rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-400">
                <Flame className="h-5 w-5" />
              </div>
            </div>
          </Card>
        </div>

        {/* Active Goals Listing */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-100">Your Goals</h3>
            <span className="text-xs text-slate-500">Click a card to resume its active node</span>
          </div>

          {goalsError && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-300 text-sm p-4 rounded-xl flex items-center space-x-3">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <span>Failed to load active goals. Please reload or check your server configuration.</span>
            </div>
          )}

          {goals && goals.length === 0 ? (
            <Card className="text-center py-12 border border-dashed border-slate-800">
              <Target className="h-12 w-12 text-slate-600 mx-auto mb-4" />
              <CardTitle className="text-lg font-bold text-slate-300">No active goals found</CardTitle>
              <CardDescription className="text-slate-500 mt-1 max-w-sm mx-auto">
                Begin by initializing a goal. Stateful LangGraph checkpoints will sequence your roadmap.
              </CardDescription>
              <Link href="/goals/new" className="inline-block mt-6">
                <Button variant="secondary" className="flex items-center space-x-2">
                  <Plus className="h-4 w-4" />
                  <span>Create First Goal</span>
                </Button>
              </Link>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {goals?.map((goal) => {
                const statusLabels: Record<string, string> = {
                  drafting: 'Discovery Intake',
                  strat_selection: 'Strategy Selection',
                  readiness_check: 'Readiness Audit',
                  planning: 'Roadmap Builder',
                  active: 'Active Cockpit',
                };
                
                return (
                  <div 
                    key={goal.id}
                    onClick={() => handleSelectGoal(goal.id, goal.status)}
                    className="glass-panel p-6 border border-slate-800/60 hover:border-slate-700/50 cursor-pointer transition duration-300 group hover:translate-y-[-2px] relative overflow-hidden"
                  >
                    <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-tr from-indigo-500/10 to-transparent rounded-full filter blur-md opacity-30 pointer-events-none" />
                    
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                          {statusLabels[goal.status] || goal.status}
                        </span>
                        <h4 className="text-lg font-bold text-slate-100 mt-3 group-hover:text-indigo-300 transition duration-300">
                          {goal.title}
                        </h4>
                        <p className="text-xs text-slate-500 mt-1.5">
                          Initialized on {new Date(goal.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <CheckCircle2 className="h-5 w-5 text-indigo-500 opacity-60 group-hover:opacity-100 transition shrink-0" />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
