import axios from "axios";
import { create } from "zustand";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

type UserRole = 'owner' | 'worker' | 'vet'

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  role: UserRole | null;
  setTokens: (access: string, refresh: string) => void;
  clear: () => void;
};

function decodeJwtPayload(token: string): any | null {
  try {
    const base64Url = token.split(".")[1]
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/")
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    )
    return JSON.parse(jsonPayload)
  } catch {
    return null
  }
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  refreshToken: null,
  role: null,
  setTokens: (access: string, refresh: string) => {
    const payload = decodeJwtPayload(access)
    const role: UserRole | null = payload?.role ?? null
    set({ accessToken: access, refreshToken: refresh, role })
  },
  clear: () => set({ accessToken: null, refreshToken: null, role: null }),
}));

export const api = axios.create({ baseURL: API_BASE + "/v1" });

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let subscribers: ((token: string) => void)[] = [];

function onRefreshed(token: string) {
  subscribers.forEach((cb) => cb(token));
  subscribers = [];
}

api.interceptors.response.use(
  (resp) => resp,
  async (error) => {
    const { response, config } = error;
    if (response?.status === 401 && !config.__isRetryRequest) {
      const store = useAuthStore.getState();
      const refresh = store.refreshToken;
      if (!refresh) {
        store.clear();
        return Promise.reject(error);
      }
      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribers.push((token) => {
            config.headers.Authorization = `Bearer ${token}`;
            config.__isRetryRequest = true;
            resolve(api(config));
          });
        });
      }
      isRefreshing = true;
      try {
        const resp = await axios.post(`${API_BASE}/v1/auth/refresh`, { token: refresh });
        const { access_token, refresh_token } = resp.data;
        useAuthStore.getState().setTokens(access_token, refresh_token);
        isRefreshing = false;
        onRefreshed(access_token);
        config.headers.Authorization = `Bearer ${access_token}`;
        config.__isRetryRequest = true;
        return api(config);
      } catch (e) {
        useAuthStore.getState().clear();
        isRefreshing = false;
        return Promise.reject(e);
      }
    }
    return Promise.reject(error);
  }
);

export function useRole(): UserRole | null {
  return useAuthStore((s) => s.role)
}

export function hasAnyRole(...roles: UserRole[]): boolean {
  const current = useAuthStore.getState().role
  return current ? roles.includes(current) : false
}

