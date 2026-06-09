'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Target, ArrowLeft, ShieldAlert, CheckCircle2, ChevronRight, Award, Clock, Flame, RefreshCw } from 'lucide-react';
import { strategyService, StrategyItem } from '../../../../../services/strategy.service';
import { Button } from '../../../../../components/ui/button';
import { Card, CardContent } from '../../../../../components/ui/card';

export default function StrategyPage() {
  const router = useRouter();
  const params = useParams();
  const goalId = params?.goalId as string;

  const [phase, setPhase] = useState<'loading' | 'selecting' | 'submitting' | 'error'>('loading');
  const [strategies, setStrategies] = useState<StrategyItem[]>([]);
  const [recommendedKey, setRecommendedKey] = useState('');
  const [explanation, setExplanation] = useState('');
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // On mount: generate strategies via REST API
  useEffect(() => {
    if (!goalId) return;
    setPhase('loading');
    strategyService.generateStrategies(goalId)
      .then((data) => {
        setStrategies(data.strategies);
        setRecommendedKey(data.recommended_strategy_key);
        setExplanation(data.recommendation_explanation);
        setSelectedKey(data.recommended_strategy_key); // pre-select recommended
        setPhase('selecting');
      })
      .catch((err) => {
        setLoadError(
          err.response?.data?.detail ||
          err.message ||
          'Failed to generate strategies. Please try again.'
        );
        setPhase('error');
      });
  }, [goalId]);

  const handleSelectStrategy = async () => {
    if (!selectedKey) return;
    setPhase('submitting');
    setSubmitError(null);
    try {
      await strategyService.selectStrategy(goalId, selectedKey);
      router.push(`/goals/${goalId}/validation`);
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || err.message || 'Failed to select strategy.');
      setPhase('selecting');
    }
  };

  const getIcon = (key: string) => {
    if (key.includes('mvp') || key.includes('sprint') || key.includes('micro') || key.includes('fast')) {
      return <Clock className="h-5 w-5 text-indigo-400" />;
    }
    if (key.includes('growth') || key.includes('deep') || key.includes('balanced')) {
      return <Award className="h-5 w-5 text-purple-400" />;
    }
    return <Flame className="h-5 w-5 text-amber-400" />;
  };

  // ── Loading ──────────────────────────────────────────────────────────
  if (phase === 'loading') {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-5 max-w-sm">
          <div className="relative w-20 h-20 mx-auto">
            <div className="absolute inset-0 rounded-full border-2 border-indigo-500/30 animate-ping" />
            <div className="absolute inset-2 rounded-full border-2 border-indigo-500/60 animate-pulse" />
            <svg className="animate-spin h-20 w-20 text-indigo-500 absolute inset-0" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
              <path className="opacity-80" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-bold text-slate-100">Generating Strategy Pathways</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              The AI Orchestrator is formulating three personalized execution strategies...
              <br />
              <span className="text-indigo-400 font-medium">This may take up to 60 seconds.</span>
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
          <h3 className="text-xl font-bold text-slate-100">Strategy Generation Failed</h3>
          <p className="text-xs text-red-300 bg-red-500/10 border border-red-500/20 rounded-lg p-3">{loadError}</p>
          <Button onClick={() => { setLoadError(null); setPhase('loading'); window.location.reload(); }} className="flex items-center space-x-2">
            <RefreshCw className="h-4 w-4" />
            <span>Retry</span>
          </Button>
        </div>
      </div>
    );
  }

  // ── Submitting ───────────────────────────────────────────────────────
  if (phase === 'submitting') {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-4">
          <svg className="animate-spin h-8 w-8 text-indigo-500 mx-auto" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-sm text-slate-400 font-medium">Locking in your strategy...</p>
        </div>
      </div>
    );
  }

  // ── Strategy selection UI ────────────────────────────────────────────
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
          <span className="text-sm font-bold">Select Execution Strategy</span>
        </div>
      </header>

      <main className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-8 space-y-8">
        {/* Title */}
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-3xl font-extrabold tracking-tight gradient-text">Choose Your Strategy</h2>
          <p className="text-sm text-slate-400">
            Based on your profile and goal context, the AI has formulated three pathways. Select the one that matches your timeline.
          </p>
        </div>

        {/* Recommendation banner */}
        {explanation && (
          <div className="max-w-2xl mx-auto bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-4 text-xs text-slate-300 leading-relaxed">
            <span className="font-bold text-indigo-400 uppercase tracking-wider text-[10px]">AI Recommendation · </span>
            {explanation}
          </div>
        )}

        {submitError && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-300 text-sm p-4 rounded-xl flex items-center space-x-3 max-w-2xl mx-auto">
            <ShieldAlert className="h-5 w-5 shrink-0" />
            <span>{submitError}</span>
          </div>
        )}

        {/* Strategy cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {strategies.map((strat) => {
            const isSelected = selectedKey === strat.strategy_key;
            return (
              <div
                key={strat.strategy_key}
                onClick={() => setSelectedKey(strat.strategy_key)}
                className={`glass-panel p-6 border transition-all duration-300 cursor-pointer flex flex-col justify-between select-none ${
                  isSelected
                    ? 'border-indigo-500 bg-indigo-500/5 ring-1 ring-indigo-500/30 translate-y-[-2px]'
                    : 'border-slate-800/80 hover:border-slate-700/50'
                }`}
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="h-10 w-10 rounded-xl bg-slate-800 flex items-center justify-center">
                      {getIcon(strat.strategy_key)}
                    </div>
                    {strat.strategy_key === recommendedKey && (
                      <span className="px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        Recommended
                      </span>
                    )}
                  </div>

                  <div>
                    <h4 className="text-lg font-bold text-slate-100">{strat.title}</h4>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">{strat.description}</p>
                  </div>

                  <div className="space-y-3 pt-2">
                    {strat.pros?.length > 0 && (
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Pros</p>
                        <ul className="text-xs text-slate-300 mt-1 space-y-1 list-disc pl-4">
                          {strat.pros.map((pro, i) => <li key={i}>{pro}</li>)}
                        </ul>
                      </div>
                    )}
                    {strat.cons?.length > 0 && (
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Cons</p>
                        <ul className="text-xs text-slate-400 mt-1 space-y-1 list-disc pl-4">
                          {strat.cons.map((con, i) => <li key={i}>{con}</li>)}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800/50 flex items-center justify-between">
                  <span className="text-[11px] font-semibold text-slate-500">Click to select</span>
                  <div className={`h-5 w-5 rounded-full border flex items-center justify-center ${isSelected ? 'border-indigo-500 bg-indigo-500 text-white' : 'border-slate-700'}`}>
                    {isSelected && <CheckCircle2 className="h-3.5 w-3.5" />}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Submit */}
        <div className="flex justify-center pt-4">
          <Button
            onClick={handleSelectStrategy}
            disabled={!selectedKey}
            className="px-8 py-3.5 flex items-center space-x-2 text-sm font-semibold"
          >
            <span>Proceed to Validation</span>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </main>
    </div>
  );
}
