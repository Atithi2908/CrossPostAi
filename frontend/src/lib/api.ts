const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("token");
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  // Safely join URL and endpoint avoiding double slashes
  const baseUrl = API_URL.replace(/\/+$/, "");
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const fetchUrl = `${baseUrl}${cleanEndpoint}`;

  const response = await fetch(fetchUrl, {
    ...options,
    headers,
  });

  // Handle unauthorized by clearing token
  if (response.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/login";
  }

  const isJson = response.headers.get("content-type")?.includes("application/json");
  const data = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    throw new ApiError(
      response.status,
      data?.detail || typeof data === "string" ? data : "An error occurred"
    );
  }

  return data as T;
}

export const api = {
  get: <T>(endpoint: string) => request<T>(endpoint),
  post: <T>(endpoint: string, body?: any) => request<T>(endpoint, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  }),
};
