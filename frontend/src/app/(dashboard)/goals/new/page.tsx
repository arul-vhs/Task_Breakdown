'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Target, ArrowLeft, ShieldAlert } from 'lucide-react';
import { goalService } from '../../../../services/goal.service';
import { useUIStore } from '../../../../store/ui.store';
import { Button } from '../../../../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../../components/ui/card';

const goalSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters').max(100, 'Title cannot exceed 100 characters'),
  description: z.string().optional(),
});

type GoalFields = z.infer<typeof goalSchema>;

export default function CreateGoalPage() {
  const router = useRouter();
  const setSelectedGoalId = useUIStore((s) => s.setSelectedGoalId);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<GoalFields>({
    resolver: zodResolver(goalSchema),
  });

  const onSubmit = async (data: GoalFields) => {
    setIsLoading(true);
    setApiError(null);
    try {
      // Step 1: Create the goal record
      const response = await goalService.createGoal({
        title: data.title,
        description: data.description || '',
      });

      setSelectedGoalId(response.id);

      // Step 2: Navigate to intake — intake page will call analyze
      router.push(`/goals/${response.id}/intake`);
    } catch (err: any) {
      setApiError(err.response?.data?.detail || err.message || 'Failed to create goal. Please try again.');
      setIsLoading(false);
    }
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
          <span>Back</span>
        </button>
        <div className="flex items-center space-x-2 border-l border-slate-700/50 pl-4">
          <Target className="h-5 w-5 text-indigo-500" />
          <span className="text-sm font-bold">New Goal</span>
        </div>
      </header>

      {/* Main Form Box */}
      <main className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-lg">
          <Card className="border border-slate-700/50 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-full filter blur-[60px] opacity-20 pointer-events-none" />

            <CardHeader className="text-center">
              <CardTitle className="text-2xl font-extrabold gradient-text">Start A Goal</CardTitle>
              <CardDescription className="text-slate-400 mt-2">
                Define your objective. The AI will generate personalized intake questions and strategies.
              </CardDescription>
            </CardHeader>

            <CardContent>
              {apiError && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-300 text-xs p-3 rounded-lg mb-6 flex items-center space-x-2">
                  <ShieldAlert className="h-4 w-4 shrink-0" />
                  <span>{apiError}</span>
                </div>
              )}

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Goal Objective
                  </label>
                  <input
                    type="text"
                    {...register('title')}
                    placeholder="e.g. Build an AI-driven trading bot, Pass GCP Architect exam"
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 px-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                  />
                  {errors.title && (
                    <p className="text-[11px] text-red-400 mt-1 pl-1">{errors.title.message}</p>
                  )}
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Brief Context / Description
                  </label>
                  <textarea
                    {...register('description')}
                    rows={4}
                    placeholder="Describe what success looks like, any hard constraints, or relevant prior experience."
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 px-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition resize-none"
                  />
                </div>

                <Button
                  type="submit"
                  isLoading={isLoading}
                  className="w-full py-3.5 mt-4 text-sm font-semibold"
                >
                  Create Goal & Run Discovery
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
