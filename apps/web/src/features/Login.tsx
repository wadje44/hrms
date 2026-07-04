import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../api/client";
import type { PublicEmployee } from "../api/types";
import { useAuth } from "../auth/AuthContext";

export function Login() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const [employees, setEmployees] = useState<PublicEmployee[]>([]);
  const [employeeId, setEmployeeId] = useState("");
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

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
      </form>
    </div>
  );
}
