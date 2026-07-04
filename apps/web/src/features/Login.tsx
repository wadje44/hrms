import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../api/client";
import type { PublicEmployee } from "../api/types";
import { useAuth } from "../auth/AuthContext";

const DEMO_ACCOUNTS = [
  { id: "EMP008", label: "Neelam (Admin)", pin: "1234" },
  { id: "EMP006", label: "Tushar (Manager)", pin: "0000" },
  { id: "EMP007", label: "Ganesh (Manager)", pin: "0000" },
  { id: "EMP001", label: "Aarti (Employee)", pin: "0000" },
  { id: "EMP004", label: "Kunal (Employee)", pin: "0000" },
];

export function Login() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const [employees, setEmployees] = useState<PublicEmployee[]>([]);
  const [employeeId, setEmployeeId] = useState("");
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showDemo, setShowDemo] = useState(false);

  useEffect(() => {
    if (user) navigate("/");
  }, [user, navigate]);

  useEffect(() => {
    api
      .get<PublicEmployee[]>("/auth/employees")
      .then(setEmployees)
      .catch(() => setError("Could not reach the server."));
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(employeeId, pin);
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 16,
        background: "var(--navy)",
      }}
    >
      <form className="card" onSubmit={submit} style={{ width: "100%", maxWidth: 360 }}>
        <h2 style={{ marginTop: 0 }}>
          Prabha <span style={{ color: "var(--orange)" }}>HRMS</span>
        </h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Select your name and enter your 4-digit PIN.
        </p>

        <label htmlFor="emp">Employee</label>
        <select
          id="emp"
          value={employeeId}
          onChange={(e) => setEmployeeId(e.target.value)}
          required
        >
          <option value="" disabled>
            Select your name…
          </option>
          {employees.map((e) => (
            <option key={e.id} value={e.id}>
              {e.full_name} ({e.id})
            </option>
          ))}
        </select>

        <label htmlFor="pin">PIN</label>
        <input
          id="pin"
          type="password"
          inputMode="numeric"
          autoComplete="off"
          maxLength={8}
          value={pin}
          onChange={(e) => setPin(e.target.value)}
          required
        />

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <button className="accent" type="submit" disabled={busy} style={{ width: "100%", marginTop: 14 }}>
          {busy ? "Signing in…" : "Sign in"}
        </button>

        <button
          type="button"
          onClick={() => setShowDemo((v) => !v)}
          style={{
            width: "100%",
            marginTop: 10,
            background: "none",
            border: "1px solid var(--border)",
            borderRadius: 6,
            padding: "6px 0",
            cursor: "pointer",
            color: "var(--muted)",
            fontSize: 13,
          }}
        >
          {showDemo ? "Hide" : "Show"} demo accounts
        </button>

        {showDemo && (
          <div style={{ marginTop: 10 }}>
            {DEMO_ACCOUNTS.map((acc) => (
              <button
                key={acc.id}
                type="button"
                onClick={() => {
                  setEmployeeId(acc.id);
                  setPin(acc.pin);
                }}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  width: "100%",
                  padding: "6px 10px",
                  marginBottom: 4,
                  background: employeeId === acc.id ? "var(--orange)" : "var(--surface)",
                  color: employeeId === acc.id ? "#fff" : "inherit",
                  border: "1px solid var(--border)",
                  borderRadius: 6,
                  cursor: "pointer",
                  fontSize: 13,
                  textAlign: "left",
                }}
              >
                <span>{acc.label}</span>
                <span style={{ fontFamily: "monospace", opacity: 0.7 }}>
                  {acc.id} · PIN {acc.pin}
                </span>
              </button>
            ))}
          </div>
        )}
      </form>
    </div>
  );
}
