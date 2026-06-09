'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Target, ArrowLeft, ShieldAlert, ChevronRight, ChevronLeft, Brain, Sparkles } from 'lucide-react';
import { goalService } from '../../../../../services/goal.service';
import { Button } from '../../../../../components/ui/button';
import { Card, CardHeader, CardContent } from '../../../../../components/ui/card';

type AnalyzeResult = {
  category: string;
  difficulty: string;
  estimated_duration: string;
  required_skills: string[];
  risks: string[];
  questions: string[];
};

export default function IntakePage() {
  const router = useRouter();
  const params = useParams();
  const goalId = params?.goalId as string;

  const [phase, setPhase] = useState<'analyzing' | 'questions' | 'submitting'>('analyzing');
  const [analysisData, setAnalysisData] = useState<AnalyzeResult | null>(null);
  const [analyzeError, setAnalyzeError] = useState<string | null>(null);

  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentIdx, setCurrentIdx] = useState(0);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // On mount: call /analyze to get dynamic questions
  useEffect(() => {
    if (!goalId) return;
    goalService.analyzeGoal(goalId)
      .then((data) => {
        setAnalysisData(data);
        setPhase('questions');
      })
      .catch((err) => {
        setAnalyzeError(
          err.response?.data?.detail ||
          err.message ||
          'Failed to analyze goal. Please try again.'
        );
      });
  }, [goalId]);

  const questions = analysisData?.questions || [];
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
      await goalService.submitContextAnswers(goalId, formattedAnswers);
      router.push(`/goals/${goalId}/strategy`);
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || err.message || 'Failed to submit answers.');
      setPhase('questions');
    }
  };

  // ── Analyzing state ──────────────────────────────────────────────────
  if (phase === 'analyzing') {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-5 max-w-sm">
          <div className="relative w-20 h-20 mx-auto">
            <div className="absolute inset-0 rounded-full border-2 border-indigo-500/30 animate-ping" />
            <div className="absolute inset-3 rounded-full border-2 border-purple-500/60 animate-pulse" />
            <div className="absolute inset-0 flex items-center justify-center">
              <Brain className="h-8 w-8 text-indigo-400 animate-bounce" />
            </div>
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-bold text-slate-100">Analyzing Your Goal</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              The AI is generating personalized intake questions based on your goal context...
              <br />
              <span className="text-indigo-400 font-medium">This may take up to 60 seconds.</span>
            </p>
          </div>
          {analyzeError && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-300 text-xs p-3 rounded-lg flex items-center space-x-2">
              <ShieldAlert className="h-4 w-4 shrink-0" />
              <span>{analyzeError}</span>
            </div>
          )}
          {!analyzeError && (
            <div className="flex items-center justify-center space-x-1.5">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-bounce"
                  style={{ animationDelay: `${i * 150}ms` }}
                />
              ))}
            </div>
          )}
          {analyzeError && (
            <Button onClick={() => { setAnalyzeError(null); setPhase('analyzing'); window.location.reload(); }} className="text-sm">
              Retry Analysis
            </Button>
          )}
        </div>
      </div>
    );
  }

  // ── Submitting state ─────────────────────────────────────────────────
  if (phase === 'submitting') {
    return (
      <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex items-center justify-center">
        <div className="text-center space-y-4">
          <svg className="animate-spin h-8 w-8 text-indigo-500 mx-auto" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-sm text-slate-400 font-medium">Saving your answers...</p>
        </div>
      </div>
    );
  }

  // ── Questions wizard ─────────────────────────────────────────────────
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
          <span className="text-sm font-bold">Goal Discovery — Intake Questions</span>
        </div>
        {analysisData && (
          <div className="ml-auto flex items-center space-x-2">
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              {analysisData.category}
            </span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
              {analysisData.difficulty}
            </span>
          </div>
        )}
      </header>

      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-lg">
          <Card className="border border-slate-700/50 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-full filter blur-[60px] opacity-20 pointer-events-none" />

            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Sparkles className="h-4 w-4 text-indigo-400" />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                    Intake Question {currentIdx + 1} of {questions.length}
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
                <h3 className="text-lg font-bold text-slate-100 leading-snug">
                  {currentQuestion}
                </h3>
                <textarea
                  value={currentAnswer}
                  onChange={(e) => setAnswers({ ...answers, [currentQuestion]: e.target.value })}
                  rows={4}
                  placeholder="Provide context or answer details..."
                  className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 px-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition resize-none"
                />
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-slate-800/50">
                <Button
                  variant="secondary"
                  onClick={handlePrev}
                  disabled={currentIdx === 0}
                  className="flex items-center space-x-2 text-xs font-semibold px-4"
                >
                  <ChevronLeft className="h-4 w-4" />
                  <span>Previous</span>
                </Button>

                <Button
                  onClick={handleNext}
                  disabled={!currentAnswer.trim()}
                  className="flex items-center space-x-2 text-xs font-semibold px-5"
                >
                  <span>{currentIdx + 1 === questions.length ? 'Submit Answers' : 'Next'}</span>
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
