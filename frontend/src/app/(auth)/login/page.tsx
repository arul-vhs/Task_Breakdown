'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Target, Mail, Lock, ShieldAlert } from 'lucide-react';
import { useAuthStore } from '../../../store/auth.store';
import { authService } from '../../../services/auth.service';
import { Button } from '../../../components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../../components/ui/card';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginFields = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const setToken = useAuthStore((s) => s.setToken);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFields>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFields) => {
    setIsLoading(true);
    setApiError(null);
    try {
      const response = await authService.login(data.email, data.password);
      setToken(response.access_token, data.email);
      router.push('/dashboard');
    } catch (err: any) {
      setApiError(err.message || 'Login failed. Please verify your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-955/20 via-[#0b0f19] to-[#0b0f19]">
      <div className="w-full max-w-md">
        
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
            <CardTitle className="text-2xl font-extrabold gradient-text">Welcome Back</CardTitle>
            <CardDescription className="text-slate-400 mt-2">
              Sign in to manage your active roadmap and execute daily blocks.
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
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
                  <input
                    type="email"
                    {...register('email')}
                    placeholder="you@example.com"
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 pl-11 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                  />
                </div>
                {errors.email && (
                  <p className="text-[11px] text-red-400 mt-1 pl-1">{errors.email.message}</p>
                )}
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-3.5 h-4 w-4 text-slate-500" />
                  <input
                    type="password"
                    {...register('password')}
                    placeholder="••••••••"
                    className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3.5 pl-11 pr-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                  />
                </div>
                {errors.password && (
                  <p className="text-[11px] text-red-400 mt-1 pl-1">{errors.password.message}</p>
                )}
              </div>

              <Button
                type="submit"
                isLoading={isLoading}
                className="w-full py-3.5 mt-2 text-sm font-semibold"
              >
                Sign In
              </Button>
            </form>

            <div className="text-center mt-6">
              <span className="text-xs text-slate-400">Don't have an account? </span>
              <Link
                href="/signup"
                className="text-xs text-indigo-400 hover:text-indigo-300 font-medium transition"
              >
                Sign Up
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
