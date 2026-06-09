'use client';

import React, { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Target, ArrowLeft, ShieldAlert, Award, Compass, Send, User, MessageSquare, Flame, Lightbulb, AlertTriangle } from 'lucide-react';
import { useWorkflowState } from '../../../../../hooks/useWorkflowState';
import { authService } from '../../../../../services/auth.service';
import { coachService } from '../../../../../services/coach.service';
import { Button } from '../../../../../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../../../components/ui/card';

export default function CoachPage() {
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

  // 2. Poll state and fetch AI Coach insights V2
  const { data: stateData, isLoading: isStateLoading } = useWorkflowState(threadId);

  const { data: insights, isLoading: isInsightsLoading, error: insightsError } = useQuery({
    queryKey: ['coachInsights', goalId],
    queryFn: () => coachService.generateInsights(goalId),
    enabled: !!goalId,
    refetchOnMount: false, // Prevent excessive LLM token calls
  });

  // Chat message thread local state
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([
    { role: 'assistant', content: "Hello! I am your GoalPilot AI Coach. I analyze your completions velocity, identify schedule buffer slips, and help you adapt when timeline drift occurs. What is on your mind?" }
  ]);

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: (message: string) => {
      // Map chat history payload
      const history = chatMessages.map(m => ({
        role: m.role,
        content: m.content
      }));
      return coachService.chatWithCoach(goalId, message, history);
    },
    onSuccess: (data) => {
      setChatMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
    },
  });

  const handleSend = () => {
    if (!chatInput.trim() || chatMutation.isPending) return;
    const msg = chatInput.trim();
    setChatMessages(prev => [...prev, { role: 'user', content: msg }]);
    setChatInput('');
    chatMutation.mutate(msg);
  };

  const state = stateData?.data;

  if (isStateLoading || isInsightsLoading) {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-4">
          <svg className="animate-spin h-8 w-8 text-indigo-500 mx-auto" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-sm text-slate-400 font-medium animate-pulse">Running AI coaching diagnostics...</p>
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
          <Link href={`/goals/${goalId}/coach`} className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-indigo-600 text-white transition">
            AI Coach
          </Link>
          <Link href={`/goals/${goalId}/replan`} className="px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 transition">
            Replan
          </Link>
        </div>
      </header>

      {/* Main split dashboard panel */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-6 md:p-8 grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        
        {/* Left Side: Chat Workspace */}
        <div className="md:col-span-7 flex flex-col h-[600px] border border-slate-800/80 rounded-2xl bg-slate-950/20 overflow-hidden">
          <div className="p-4 border-b border-slate-800/80 bg-slate-950/40 flex items-center space-x-2">
            <MessageSquare className="h-4.5 w-4.5 text-indigo-400" />
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Stateful Conversational Coach</h4>
          </div>

          {/* Messages Bubble List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatMessages.map((msg, i) => {
              const isAssistant = msg.role === 'assistant';
              return (
                <div key={i} className={`flex items-start gap-3 ${isAssistant ? '' : 'flex-row-reverse'}`}>
                  <div className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 text-xs font-bold border ${
                    isAssistant ? 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400' : 'bg-slate-800 border-slate-700 text-slate-200'
                  }`}>
                    {isAssistant ? 'AI' : 'ME'}
                  </div>
                  <div className={`p-3 rounded-2xl text-xs max-w-sm leading-relaxed ${
                    isAssistant ? 'bg-slate-900/80 text-slate-200 border border-slate-800/60' : 'bg-indigo-600 text-white shadow-md'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              );
            })}
            
            {chatMutation.isPending && (
              <div className="flex items-start gap-3">
                <div className="h-8 w-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0 text-xs font-bold">
                  AI
                </div>
                <div className="p-3 bg-slate-900/80 rounded-2xl text-xs text-slate-400 border border-slate-800/60 flex items-center space-x-2">
                  <svg className="animate-spin h-3.5 w-3.5 text-indigo-500" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Formulating recommendations...</span>
                </div>
              </div>
            )}
          </div>

          {/* Input Panel */}
          <div className="p-4 border-t border-slate-800/80 bg-slate-950/45 flex items-center gap-3">
            <input
              type="text"
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Ask for risk mitigations or adjustment ideas..."
              className="flex-1 bg-slate-900/50 border border-slate-800 rounded-xl py-3 px-4 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
            />
            <button
              onClick={handleSend}
              disabled={!chatInput.trim() || chatMutation.isPending}
              className="h-10 w-10 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white flex items-center justify-center shrink-0 transition"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Right Side: Diagnostics Panel */}
        <div className="md:col-span-5 space-y-6">
          <Card className="border-slate-800/80 bg-slate-900/10">
            <CardHeader className="flex flex-row items-center space-x-2 pb-2">
              <Lightbulb className="h-5 w-5 text-indigo-400 shrink-0" />
              <CardTitle className="text-sm font-bold">Daily Briefing</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-slate-300 leading-relaxed font-medium">
                {insights?.daily_briefing || "Your schedule is currently up to date. Keep focus on upcoming time blocks."}
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-800/80">
            <CardHeader className="flex flex-row items-center space-x-2 pb-2">
              <Compass className="h-5 w-5 text-purple-400 shrink-0" />
              <CardTitle className="text-sm font-bold">Progress Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-slate-400 leading-relaxed">
                {insights?.progress_analysis || "Completions are loading..."}
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-800/80">
            <CardHeader className="flex flex-row items-center space-x-2 pb-2">
              <AlertTriangle className="h-5 w-5 text-amber-500 shrink-0" />
              <CardTitle className="text-sm font-bold">Risk Assessment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-xs text-slate-400 leading-relaxed">
                {insights?.risk_assessment || "No immediate scheduling warnings."}
              </p>
              
              {insights?.adaptive_replanning_payload && (
                <div className="pt-3 border-t border-slate-800/50 space-y-2">
                  <div className="flex items-center justify-between text-[10px] font-bold uppercase text-slate-500">
                    <span>Risk Level: {insights.adaptive_replanning_payload.risk_level}</span>
                    <span>Velocity: {insights.adaptive_replanning_payload.velocity_status}</span>
                  </div>
                  {insights.adaptive_replanning_payload.at_risk_tasks?.length > 0 && (
                    <div className="text-[11px] text-amber-300/95 font-semibold">
                      At-risk tasks: {insights.adaptive_replanning_payload.at_risk_tasks.join(', ')}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

      </main>
    </div>
  );
}
