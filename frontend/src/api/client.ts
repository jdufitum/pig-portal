import axios from "axios";
import { create } from "zustand";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  setTokens: (access: string, refresh: string) => void;
  clear: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  refreshToken: null,
  setTokens: (access: string, refresh: string) => set({ accessToken: access, refreshToken: refresh }),
  clear: () => set({ accessToken: null, refreshToken: null }),
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
        const resp = await axios.post(`${API_BASE}/auth/refresh`, { token: refresh });
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

