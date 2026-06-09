'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Target, ArrowLeft, ShieldAlert, ChevronRight, ChevronLeft, Shield, RefreshCw, CheckCircle, AlertTriangle } from 'lucide-react';
import { validationService, ReadinessEvaluateResponse } from '../../../../../services/validation.service';
import { Button } from '../../../../../components/ui/button';
import { Card, CardHeader, CardContent } from '../../../../../components/ui/card';

export default function ValidationPage() {
  const router = useRouter();
  const params = useParams();
  const goalId = params?.goalId as string;

  const [phase, setPhase] = useState<'loading' | 'questions' | 'submitting' | 'results' | 'error'>('loading');
  const [questions, setQuestions] = useState<string[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentIdx, setCurrentIdx] = useState(0);
  const [results, setResults] = useState<ReadinessEvaluateResponse | null>(null);

  // On mount: fetch validation questions
  useEffect(() => {
    if (!goalId) return;
    validationService.getValidationQuestions(goalId)
      .then((data) => {
        setQuestions(data.validation_questions);
        setPhase('questions');
      })
      .catch((err) => {
        setLoadError(err.response?.data?.detail || err.message || 'Failed to load validation questions.');
        setPhase('error');
      });
  }, [goalId]);

  const currentQuestion = questions[currentIdx] || '';
  const currentAnswer = answers[currentQuestion] || '';

  const handleNext = () => {
    if (!currentAnswer.trim()) return;
    if (currentIdx + 1 < questions.length) {
      setCurrentIdx(currentIdx + 1);
    } else {
      handleSubmitAnswers();
    }
  };

  const handlePrev = () => {
    if (currentIdx > 0) setCurrentIdx(currentIdx - 1);
  };

  const handleSubmitAnswers = async () => {
    setPhase('submitting');
    setSubmitError(null);

    const formattedAnswers = questions.map((q) => ({
      question: q,
      answer: answers[q] || '',
    }));

    try {
      const evalResult = await validationService.evaluateReadiness(goalId, formattedAnswers);
      setResults(evalResult);
      setPhase('results');
    } catch (err: any) {
      // err.message already has the extracted backend error from api-client interceptor
      const msg = err.message || 'Failed to evaluate readiness. Please try again.';
      setSubmitError(msg);
      setPhase('questions'); // stay on questions so user can retry
    }
  };


  const handleProceedToRoadmap = () => {
    router.push(`/goals/${goalId}/roadmap`);
  };

  // ── Loading ──────────────────────────────────────────────────────────
  if (phase === 'loading') {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-5 max-w-sm">
          <div className="relative w-20 h-20 mx-auto">
            <div className="absolute inset-0 rounded-full border-2 border-indigo-500/30 animate-ping" />
            <div className="absolute inset-3 rounded-full border-2 border-purple-500/60 animate-pulse" />
            <div className="absolute inset-0 flex items-center justify-center">
              <Shield className="h-8 w-8 text-indigo-400 animate-bounce" />
            </div>
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-bold text-slate-100">Generating Validation Audit</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Formulating readiness validation questions based on your selected strategy...
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
          <h3 className="text-xl font-bold">Validation Failed</h3>
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
          <p className="text-sm text-slate-400 font-medium">Evaluating your readiness...</p>
        </div>
      </div>
    );
  }

  // ── Results ──────────────────────────────────────────────────────────
  if (phase === 'results' && results) {
    const score = results.overall_readiness_score;
    const isReady = score >= 60;
    const scoreColor = score >= 80 ? 'text-emerald-400' : score >= 60 ? 'text-amber-400' : 'text-red-400';
    const scoreBg = score >= 80 ? 'bg-emerald-500/10 border-emerald-500/20' : score >= 60 ? 'bg-amber-500/10 border-amber-500/20' : 'bg-red-500/10 border-red-500/20';

    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
        <header className="border-b border-slate-800/80 bg-[#0f172a]/60 backdrop-blur-md px-6 py-4 flex items-center sticky top-0 z-50">
          <button onClick={() => router.push('/dashboard')} className="text-slate-400 hover:text-slate-100 transition mr-4 flex items-center space-x-1 text-sm font-semibold">
            <ArrowLeft className="h-4 w-4" />
            <span>Dashboard</span>
          </button>
          <div className="flex items-center space-x-2 border-l border-slate-700/50 pl-4">
            <Target className="h-5 w-5 text-indigo-500" />
            <span className="text-sm font-bold">Readiness Assessment Results</span>
          </div>
        </header>

        <main className="flex-1 max-w-3xl w-full mx-auto p-6 md:p-8 space-y-8">
          {/* Score banner */}
          <div className={`rounded-2xl border p-6 flex items-center justify-between ${scoreBg}`}>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Overall Readiness Score</p>
              <p className={`text-5xl font-black mt-1 ${scoreColor}`}>{score}<span className="text-2xl text-slate-500">/100</span></p>
            </div>
            <div className="text-right">
              {isReady ? (
                <div className="flex items-center space-x-2 text-emerald-400">
                  <CheckCircle className="h-6 w-6" />
                  <span className="font-bold text-sm">Ready for Roadmap</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2 text-amber-400">
                  <AlertTriangle className="h-6 w-6" />
                  <span className="font-bold text-sm">Gaps Identified</span>
                </div>
              )}
            </div>
          </div>

          {/* Dimension scores */}
          {Object.keys(results.dimension_scores).length > 0 && (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 space-y-4">
              <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Dimension Scores</h3>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(results.dimension_scores).map(([dim, dimScore]) => (
                  <div key={dim} className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-slate-400 capitalize">{dim.replace(/_/g, ' ')}</span>
                      <span className="text-xs font-bold text-slate-300">{dimScore}</span>
                    </div>
                    <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-700"
                        style={{ width: `${dimScore}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Gaps & remediation */}
          {results.identified_gaps.length > 0 && (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 space-y-3">
              <h3 className="text-sm font-bold text-amber-400 uppercase tracking-wider">Identified Gaps</h3>
              <ul className="space-y-2">
                {results.identified_gaps.map((gap, i) => (
                  <li key={i} className="flex items-start space-x-2 text-xs text-slate-300">
                    <AlertTriangle className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                    <span>{gap}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {results.remediation_steps.length > 0 && (
            <div className="glass-panel p-6 rounded-2xl border border-slate-800/80 space-y-3">
              <h3 className="text-sm font-bold text-indigo-400 uppercase tracking-wider">Remediation Steps</h3>
              <ul className="space-y-2">
                {results.remediation_steps.map((step, i) => (
                  <li key={i} className="flex items-start space-x-2 text-xs text-slate-300">
                    <ChevronRight className="h-3.5 w-3.5 text-indigo-400 shrink-0 mt-0.5" />
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* CTA */}
          <div className="flex justify-center">
            <Button onClick={handleProceedToRoadmap} className="px-8 py-3.5 flex items-center space-x-2 text-sm font-semibold">
              <span>{isReady ? 'Generate Roadmap' : 'Proceed to Roadmap Anyway'}</span>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </main>
      </div>
    );
  }

  // ── Questions wizard ─────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      <header className="border-b border-slate-800/80 bg-[#0f172a]/60 backdrop-blur-md px-6 py-4 flex items-center sticky top-0 z-50">
        <button onClick={() => router.push('/dashboard')} className="text-slate-400 hover:text-slate-100 transition mr-4 flex items-center space-x-1 text-sm font-semibold">
          <ArrowLeft className="h-4 w-4" />
          <span>Dashboard</span>
        </button>
        <div className="flex items-center space-x-2 border-l border-slate-700/50 pl-4">
          <Target className="h-5 w-5 text-indigo-500" />
          <span className="text-sm font-bold">Readiness Validation</span>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-lg">
          <Card className="border border-slate-700/50 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-full filter blur-[60px] opacity-20 pointer-events-none" />

            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Shield className="h-4 w-4 text-indigo-400" />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                    Validation {currentIdx + 1} of {questions.length}
                  </span>
                </div>
                <span className="text-xs text-slate-500 font-mono">
                  {Math.round(((currentIdx + 1) / questions.length) * 100)}% Complete
                </span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden mt-3">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                  style={{ width: `${((currentIdx + 1) / questions.length) * 100}%` }}
                />
              </div>
            </CardHeader>

            <CardContent className="space-y-6">
              {submitError && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-300 text-xs p-3 rounded-lg flex items-center space-x-2">
                  <ShieldAlert className="h-4 w-4 shrink-0" />
                  <span>{submitError}</span>
                </div>
              )}

              <div className="space-y-4">
                <h3 className="text-lg font-bold text-slate-100 leading-snug">{currentQuestion}</h3>
                <textarea
                  value={currentAnswer}
                  onChange={(e) => setAnswers({ ...answers, [currentQuestion]: e.target.value })}
                  rows={4}
                  placeholder="Provide your honest assessment..."
                  className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 px-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition resize-none"
                />
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-slate-800/50">
                <Button variant="secondary" onClick={handlePrev} disabled={currentIdx === 0} className="flex items-center space-x-2 text-xs font-semibold px-4">
                  <ChevronLeft className="h-4 w-4" />
                  <span>Previous</span>
                </Button>
                <Button onClick={handleNext} disabled={!currentAnswer.trim()} className="flex items-center space-x-2 text-xs font-semibold px-5">
                  <span>{currentIdx + 1 === questions.length ? 'Evaluate Readiness' : 'Next'}</span>
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
