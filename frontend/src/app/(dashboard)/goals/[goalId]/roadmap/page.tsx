'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Target, ArrowLeft, ShieldAlert, RefreshCw, Map, Clock, ChevronRight, CheckCircle2 } from 'lucide-react';
import { roadmapService, RoadmapGenerateResponse, TaskItem } from '../../../../../services/roadmap.service';
import { Button } from '../../../../../components/ui/button';

export default function RoadmapPage() {
  const router = useRouter();
  const params = useParams();
  const goalId = params?.goalId as string;

  const [phase, setPhase] = useState<'loading' | 'ready' | 'error'>('loading');
  const [roadmap, setRoadmap] = useState<RoadmapGenerateResponse | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (!goalId) return;
    roadmapService.generateRoadmap(goalId)
      .then((data) => {
        setRoadmap(data);
        setPhase('ready');
      })
      .catch((err) => {
        setLoadError(err.response?.data?.detail || err.message || 'Failed to generate roadmap.');
        setPhase('error');
      });
  }, [goalId]);

  // Group tasks by phase
  const tasksByPhase = roadmap?.tasks.reduce((acc, task) => {
    const key = `Phase ${task.phase_number}: ${task.phase_name}`;
    if (!acc[key]) acc[key] = [];
    acc[key].push(task);
    return acc;
  }, {} as Record<string, TaskItem[]>) || {};

  const totalHours = roadmap?.tasks.reduce((sum, t) => sum + t.allocated_hours, 0) || 0;
  const totalTasks = roadmap?.tasks.length || 0;

  // ── Loading ──────────────────────────────────────────────────────────
  if (phase === 'loading') {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-5 max-w-sm">
          <div className="relative w-20 h-20 mx-auto">
            <div className="absolute inset-0 rounded-full border-2 border-indigo-500/30 animate-ping" />
            <div className="absolute inset-3 rounded-full border-2 border-purple-500/60 animate-pulse" />
            <div className="absolute inset-0 flex items-center justify-center">
              <Map className="h-8 w-8 text-indigo-400 animate-bounce" />
            </div>
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-bold text-slate-100">Building Your Roadmap</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              The AI is generating a phased task breakdown with dependencies...
              <br />
              <span className="text-indigo-400 font-medium">This may take up to 90 seconds.</span>
            </p>
          </div>
          <div className="flex items-center justify-center space-x-1.5">
            {[0, 1, 2].map((i) => (
              <div key={i} className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: `${i * 150}ms` }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ── Error ────────────────────────────────────────────────────────────
  if (phase === 'error') {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-5 max-w-sm">
          <ShieldAlert className="h-12 w-12 text-red-400 mx-auto" />
          <h3 className="text-xl font-bold">Roadmap Generation Failed</h3>
          <p className="text-xs text-red-300 bg-red-500/10 border border-red-500/20 rounded-lg p-3">{loadError}</p>
          <Button onClick={() => { setLoadError(null); setPhase('loading'); window.location.reload(); }} className="flex items-center space-x-2">
            <RefreshCw className="h-4 w-4" />
            <span>Retry</span>
          </Button>
        </div>
      </div>
    );
  }

  // ── Roadmap display ──────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800/80 bg-[#0f172a]/60 backdrop-blur-md px-6 py-4 flex items-center sticky top-0 z-50">
        <button onClick={() => router.push('/dashboard')} className="text-slate-400 hover:text-slate-100 transition mr-4 flex items-center space-x-1 text-sm font-semibold">
          <ArrowLeft className="h-4 w-4" />
          <span>Dashboard</span>
        </button>
        <div className="flex items-center space-x-2 border-l border-slate-700/50 pl-4">
          <Target className="h-5 w-5 text-indigo-500" />
          <span className="text-sm font-bold">Execution Roadmap</span>
        </div>
      </header>

      <main className="flex-1 max-w-4xl w-full mx-auto p-6 md:p-8 space-y-8">
        {/* Title */}
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-extrabold tracking-tight gradient-text">Your Execution Roadmap</h2>
          <p className="text-sm text-slate-400">
            A phased, task-level breakdown generated by the AI Blueprint Engine.
          </p>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-4">
          <div className="glass-panel p-4 rounded-xl border border-slate-800/80 text-center">
            <p className="text-2xl font-black text-indigo-400">{Object.keys(tasksByPhase).length}</p>
            <p className="text-xs text-slate-500 mt-1">Phases</p>
          </div>
          <div className="glass-panel p-4 rounded-xl border border-slate-800/80 text-center">
            <p className="text-2xl font-black text-purple-400">{totalTasks}</p>
            <p className="text-xs text-slate-500 mt-1">Tasks</p>
          </div>
          <div className="glass-panel p-4 rounded-xl border border-slate-800/80 text-center">
            <p className="text-2xl font-black text-amber-400">{totalHours.toFixed(0)}h</p>
            <p className="text-xs text-slate-500 mt-1">Total Hours</p>
          </div>
        </div>

        {/* Phases */}
        <div className="space-y-6">
          {Object.entries(tasksByPhase).map(([phaseName, tasks], phaseIdx) => (
            <div key={phaseName} className="glass-panel rounded-2xl border border-slate-800/80 overflow-hidden">
              {/* Phase header */}
              <div className="px-6 py-4 border-b border-slate-800/80 bg-slate-900/30 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-xs font-black text-white">
                    {phaseIdx + 1}
                  </div>
                  <h3 className="text-sm font-bold text-slate-200">{phaseName}</h3>
                </div>
                <div className="flex items-center space-x-1 text-xs text-slate-500">
                  <Clock className="h-3.5 w-3.5" />
                  <span>{tasks.reduce((s, t) => s + t.allocated_hours, 0).toFixed(0)}h total</span>
                </div>
              </div>

              {/* Tasks */}
              <div className="divide-y divide-slate-800/50">
                {tasks.map((task, i) => (
                  <div key={task.task_id_alias} className="px-6 py-4 flex items-start space-x-4 hover:bg-slate-800/20 transition">
                    <div className="h-5 w-5 rounded-full border border-slate-700 flex items-center justify-center mt-0.5 shrink-0">
                      <CheckCircle2 className="h-3.5 w-3.5 text-slate-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-semibold text-slate-200 truncate">{task.title || task.name}</p>
                        <span className="ml-3 text-[11px] text-slate-500 shrink-0">{task.allocated_hours}h</span>
                      </div>
                      {task.description && (
                        <p className="text-xs text-slate-400 mt-1 leading-relaxed">{task.description}</p>
                      )}
                      <span className="text-[10px] font-mono text-indigo-400/60 mt-1 block">{task.task_id_alias}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="flex justify-center pb-8">
          <Button
            onClick={() => router.push('/dashboard')}
            className="px-8 py-3.5 flex items-center space-x-2 text-sm font-semibold"
          >
            <span>Back to Dashboard</span>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </main>
    </div>
  );
}
