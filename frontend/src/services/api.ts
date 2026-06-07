const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface FetchOptions extends RequestInit {
  token?: string | null;
}

async function request<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { token, ...customOptions } = options;
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config: RequestInit = {
    ...customOptions,
    headers: {
      ...headers,
      ...customOptions.headers,
    },
  };

  const response = await fetch(`${BASE_URL}${path}`, config);
  
  if (!response.ok) {
    let errorMsg = 'An error occurred';
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errorMsg;
    } catch {
      // Fallback if not JSON
    }
    throw new Error(errorMsg);
  }

  // 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string, token?: string | null) => 
    request<T>(path, { method: 'GET', token }),
    
  post: <T>(path: string, body: any, token?: string | null) => 
    request<T>(path, { method: 'POST', body: JSON.stringify(body), token }),
    
  postForm: async <T>(path: string, formData: URLSearchParams) => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString()
    });
    
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Login failed');
    }
    
    return response.json() as Promise<T>;
  }
};
