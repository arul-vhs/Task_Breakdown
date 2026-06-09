import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value;
  const { pathname } = request.nextUrl;

  const isAuthRoute = pathname.startsWith('/login') || pathname.startsWith('/signup');
  const isProtected = pathname.startsWith('/dashboard') || pathname.startsWith('/goals') || pathname.startsWith('/profile');

  // Verify JWT expiration if present (simple base64 payload decode check)
  let isExpired = false;
  if (token) {
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        if (payload.exp && Date.now() >= payload.exp * 1000) {
          isExpired = true;
        }
      }
    } catch {
      isExpired = true;
    }
  }

  if (isProtected && (!token || isExpired)) {
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    const response = NextResponse.redirect(url);
    response.cookies.delete('access_token');
    return response;
  }

  if (isAuthRoute && token && !isExpired) {
    const url = request.nextUrl.clone();
    url.pathname = '/dashboard';
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  // Run on dashboard, goals, profile, login, signup
  matcher: [
    '/dashboard/:path*', 
    '/goals/:path*', 
    '/profile/:path*',
    '/login', 
    '/signup'
  ],
};
