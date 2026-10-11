import { create } from "zustand";

type SessionState = {
  token: string | null;
  ready: boolean;
  hydrate: () => void;
  setToken: (token: string) => void;
  clear: () => void;
};

const key = "family-task-token";
export const useSession = create<SessionState>((set) => ({
  token: null,
  ready: false,
  hydrate: () => {
    let token: string | null = null;
    try {
      token = sessionStorage.getItem(key);
    } catch {
      /* Storage may be unavailable. */
    }
    set({ token, ready: true });
  },
  setToken: (token) => {
    try {
      sessionStorage.setItem(key, token);
    } catch {
      /* Keep an in-memory session. */
    }
    set({ token, ready: true });
  },
  clear: () => {
    if (typeof window !== "undefined") {
      try {
        sessionStorage.removeItem(key);
      } catch {
        /* Clear memory even without storage. */
      }
    }
    set({ token: null, ready: true });
  },
}));
