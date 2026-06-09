'use client';

import React, { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Target, ArrowLeft, ShieldAlert, Award, Compass, Clock, CheckCircle2, ChevronRight, AlertTriangle, Play, RefreshCw, BarChart } from 'lucide-react';
import { useWorkflowState } from '../../../../../hooks/useWorkflowState';
import { authService } from '../../../../../services/auth.service';
import { replanningService } from '../../../../../services/replanning.service';
import { Button } from '../../../../../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../../../components/ui/card';

export default function ReplanPage() {
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

  // 2. Poll state
  const { data: stateData, isLoading: isStateLoading } = useWorkflowState(threadId);

  // Local state for configuration inputs
  const [newHours, setNewHours] = useState<number>(10);
  const [replanMode, setReplanMode] = useState<string>('Balanced');
  const [previewData, setPreviewData] = useState<any | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Mutations
  const previewMutation = useMutation({
    mutationFn: () => replanningService.previewReplan(goalId, newHours, replanMode),
    onSuccess: (data) => {
      setPreviewData(data);
    },
    onError: (err: any) => {
      setSubmitError(err.message || 'Failed to generate preview. Try adjusting parameters.');
    },
  });

  const applyMutation = useMutation({
    mutationFn: () => replanningService.applyReplan(goalId, newHours, replanMode),
    onSuccess: () => {
      setPreviewData(null);
      // Invalidate queries to refresh progress checklist and metrics
      queryClient.invalidateQueries({ queryKey: ['progressMetrics', goalId] });
      queryClient.invalidateQueries({ queryKey: ['workflowState', threadId] });
      router.push(`/goals/${goalId}/progress`);
    },
    onError: (err: any) => {
      setSubmitError(err.message || 'Failed to apply schedule re-allocation.');
    },
  });

  const handlePreview = () => {
    setSubmitError(null);
    previewMutation.mutate();
  };

  const handleApply = () => {
    setSubmitError(null);
    applyMutation.mutate();
  };

  const handleDiscard = () => {
    setPreviewData(null);
    setSubmitError(null);
  };

  const state = stateData?.data;

  // Set default hours when profile loads
  React.useEffect(() => {
    if (profile?.weekly_hours_available) {
      setNewHours(profile.weekly_hours_available);
    }
  }, [profile]);

  if (isStateLoading) {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-4">
          <svg className="animate-spin h-8 w-8 text-indigo-500 mx-auto" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-sm text-slate-400 font-medium animate-pulse">Syncing schedule parameters...</p>
        </div>
      </div>
    );
  }

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
          <Link href={`/goals/${goalId}/progress`} className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 transition">
            Checklist
          </Link>
          <Link href={`/goals/${goalId}/coach`} className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 transition">
            AI Coach
          </Link>
          <Link href={`/goals/${goalId}/replan`} className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-indigo-600 text-white transition">
            Replan
          </Link>
        </div>
      </header>

      {/* Cockpit Content */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-6 md:p-8 space-y-8">
        
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-3xl font-extrabold tracking-tight gradient-text">Timeline Rescheduling Cockpit</h2>
          <p className="text-sm text-slate-400">
            If your circumstances change, customize weekly available work hours and preview re-sequenced timeline metrics instantly.
          </p>
        </div>

        {submitError && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-300 text-sm p-4 rounded-xl flex items-center space-x-3 max-w-xl mx-auto">
            <ShieldAlert className="h-5 w-5 shrink-0" />
            <span>{submitError}</span>
          </div>
        )}

        {/* Configuration Row */}
        {!previewData && (
          <Card className="max-w-xl mx-auto border-slate-800/80">
            <CardHeader>
              <CardTitle className="text-sm font-bold">Reschedule Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  New Weekly Available Hours
                </label>
                <div className="relative">
                  <Clock className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
                  <input
                    type="number"
                    value={newHours}
                    onChange={e => setNewHours(Number(e.target.value))}
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 pl-11 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                  Replanning Mode
                </label>
                <select
                  value={replanMode}
                  onChange={e => setReplanMode(e.target.value)}
                  className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 px-4 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 transition cursor-pointer"
                >
                  <option value="Balanced" className="bg-slate-950">Balanced (Safe Buffer)</option>
                  <option value="Aggressive" className="bg-slate-950">Aggressive (Compress Dates)</option>
                  <option value="Slow" className="bg-slate-950">Relaxed (Distribute workloads)</option>
                </select>
              </div>

              <Button
                onClick={handlePreview}
                isLoading={previewMutation.isPending}
                className="w-full py-3.5 mt-4 text-sm font-semibold"
              >
                Generate Replan Preview
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Preview Output Details */}
        {previewData && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
            
            {/* Quick Metrics Comparisons */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="border-slate-800/80">
                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">New Health Score</p>
                <h4 className="text-xl font-extrabold text-slate-200 mt-2">{previewData.roadmap_health_score}%</h4>
              </Card>

              <Card className="border-slate-800/80">
                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Completion Probability</p>
                <h4 className="text-xl font-extrabold text-slate-200 mt-2">{previewData.completion_probability}%</h4>
              </Card>

              <Card className="border-slate-800/80">
                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Timeline Forecast</p>
                <h4 className="text-sm font-extrabold text-slate-300 mt-2.5 truncate">{previewData.goal_completion_forecast}</h4>
              </Card>
            </div>

            {/* Risk Analysis details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-slate-800/80">
                <CardHeader className="flex flex-row items-center space-x-2 pb-2">
                  <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0" />
                  <CardTitle className="text-sm font-bold">Rescheduling Risk Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-slate-300 leading-relaxed">{previewData.risk_analysis}</p>
                </CardContent>
              </Card>

              <Card className="border-slate-800/80">
                <CardHeader className="flex flex-row items-center space-x-2 pb-2">
                  <Compass className="h-5 w-5 text-indigo-400 shrink-0" />
                  <CardTitle className="text-sm font-bold">Recommended Adjustments</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="text-xs text-slate-300 space-y-2 list-disc pl-4 mt-1">
                    {previewData.recommended_adjustments?.map((adj: string, i: number) => <li key={i}>{adj}</li>)}
                  </ul>
                </CardContent>
              </Card>
            </div>

            {/* Apply / Discard Actions */}
            <div className="flex items-center justify-center space-x-4">
              <Button
                variant="secondary"
                onClick={handleDiscard}
                className="px-6 py-3 font-semibold text-xs"
              >
                Discard Preview
              </Button>
              <Button
                onClick={handleApply}
                isLoading={applyMutation.isPending}
                className="px-8 py-3.5 font-semibold text-xs flex items-center space-x-2"
              >
                <Play className="h-3.5 w-3.5" />
                <span>Apply & Reschedule Calendar</span>
              </Button>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
