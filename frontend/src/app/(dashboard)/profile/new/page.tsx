'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Target, User, Compass, Clock, Award, ShieldAlert } from 'lucide-react';
import { authService } from '../../../../services/auth.service';
import { Button } from '../../../../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../../components/ui/card';

const profileSchema = z.object({
  fullName: z.string().min(2, 'Name must be at least 2 characters'),
  role: z.string().min(1, 'Please select a role'),
  workStyle: z.string().min(1, 'Please select a work style'),
  weeklyHours: z.number().min(1, 'Must allocate at least 1 hour/week').max(168, 'Cannot exceed 168 hours/week'),
  biggestChallenge: z.string().optional(),
});

type ProfileFields = z.infer<typeof profileSchema>;

export default function ProfileNewPage() {
  const router = useRouter();
  const [apiError, setApiError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ProfileFields>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      weeklyHours: 10,
    },
  });

  const selectedRole = watch('role');
  const selectedStyle = watch('workStyle');

  const onSubmit = async (data: ProfileFields) => {
    setIsLoading(true);
    setApiError(null);
    try {
      await authService.updateProfile({
        full_name: data.fullName,
        role: data.role,
        work_style: data.workStyle,
        weekly_hours_available: data.weeklyHours,
        biggest_challenge: data.biggestChallenge,
      });
      router.push('/dashboard');
    } catch (err: any) {
      setApiError(err.message || 'Failed to save profile. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-955/20 via-[#0b0f19] to-[#0b0f19]">
      <div className="w-full max-w-lg">
        
        {/* Branding Logo */}
        <div className="flex items-center justify-center space-x-3 mb-8">
          <div className="h-11 w-11 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Target className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">OnboardX</h1>
            <p className="text-[10px] text-indigo-400 font-semibold uppercase tracking-widest">AI Goal Operating System</p>
          </div>
        </div>

        <Card className="border border-slate-700/50 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-full filter blur-[60px] opacity-20 pointer-events-none" />
          
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-extrabold gradient-text">Configure Onboarding</CardTitle>
            <CardDescription className="text-slate-400 mt-2">
              Tell us about your execution styles so we can normalise strategy roadmaps.
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
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
                  <input
                    type="text"
                    {...register('fullName')}
                    placeholder="John Doe"
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 pl-11 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                  />
                </div>
                {errors.fullName && (
                  <p className="text-[11px] text-red-400 mt-1 pl-1">{errors.fullName.message}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                    Your Role
                  </label>
                  <select
                    {...register('role')}
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 px-4 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 transition cursor-pointer"
                  >
                    <option value="" className="bg-slate-950">Select Role</option>
                    <option value="Student" className="bg-slate-950">Student</option>
                    <option value="Professional" className="bg-slate-950">Professional</option>
                    <option value="Developer" className="bg-slate-950">Developer / Creator</option>
                    <option value="Researcher" className="bg-slate-950">Researcher</option>
                  </select>
                  {errors.role && (
                    <p className="text-[11px] text-red-400 mt-1 pl-1">{errors.role.message}</p>
                  )}
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                    Work Style
                  </label>
                  <select
                    {...register('workStyle')}
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 px-4 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 transition cursor-pointer"
                  >
                    <option value="" className="bg-slate-950">Select Style</option>
                    <option value="Pomodoro" className="bg-slate-950">Pomodoro Sprints</option>
                    <option value="Deep Work" className="bg-slate-950">Deep Work Blocks</option>
                    <option value="Time Blocking" className="bg-slate-950">Time Blocking</option>
                    <option value="Flexible" className="bg-slate-950">Flexible Buffer</option>
                  </select>
                  {errors.workStyle && (
                    <p className="text-[11px] text-red-400 mt-1 pl-1">{errors.workStyle.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Weekly Available Hours
                </label>
                <div className="relative">
                  <Clock className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
                  <input
                    type="number"
                    {...register('weeklyHours', { valueAsNumber: true })}
                    placeholder="10"
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 pl-11 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                  />
                </div>
                {errors.weeklyHours && (
                  <p className="text-[11px] text-red-400 mt-1 pl-1">{errors.weeklyHours.message}</p>
                )}
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Biggest Consistency Challenge
                </label>
                <div className="relative">
                  <Compass className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
                  <input
                    type="text"
                    {...register('biggestChallenge')}
                    placeholder="e.g. Procrastination, complex tasks, fatigue"
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 pl-11 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                  />
                </div>
              </div>

              <Button
                type="submit"
                isLoading={isLoading}
                className="w-full py-3.5 mt-4 text-sm font-semibold"
              >
                Save Profile & Start Dashboard
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
