import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api, clearToken, getToken, setToken } from "../api/client";
import type { LoginResponse, Role } from "../api/types";

interface AuthState {
  employeeId: string;
  fullName: string;
  role: Role;
}

interface AuthContextValue {
  user: AuthState | null;
  loading: boolean;
  login: (employeeId: string, pin: string) => Promise<void>;
  logout: () => void;
}

const STORAGE = "hrms_user";
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthState | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE);
    if (raw && getToken()) setUser(JSON.parse(raw));
    setLoading(false);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      async login(employeeId, pin) {
        const res = await api.post<LoginResponse>("/auth/login", {
          employee_id: employeeId,
          pin,
        });
        setToken(res.access_token);
        const state: AuthState = {
          employeeId: res.employee_id,
          fullName: res.full_name,
          role: res.role,
        };
        localStorage.setItem(STORAGE, JSON.stringify(state));
        setUser(state);
      },
      logout() {
        clearToken();
        localStorage.removeItem(STORAGE);
        setUser(null);
      },
    }),
    [user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
