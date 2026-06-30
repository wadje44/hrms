import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "../../api/client";
import type { AttendanceDay, PunchResult } from "../../api/types";
import { useToast } from "../../components/Toast";
import { Spinner } from "../../components/ui";
import { getPosition } from "../../lib/geolocation";
import { elapsed, fmtTime } from "../../lib/format";

type GpsState = "idle" | "searching" | "locked" | "denied";

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

export function Punch() {
  const { notify } = useToast();
  const [day, setDay] = useState<AttendanceDay | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [gps, setGps] = useState<GpsState>("idle");
  const [now, setNow] = useState(Date.now());

  const load = useCallback(async () => {
    const d = today();
    const rows = await api.get<AttendanceDay[]>(`/attendance/me?date_from=${d}&date_to=${d}`);
    setDay(rows[0] ?? null);
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // Live timer tick while a session is open.
  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, []);

  const openSession = day?.sessions.find((s) => !s.punch_out) ?? null;

  async function punchIn() {
    setBusy(true);
    setGps("searching");
    const pos = await getPosition();
    setGps(pos.available ? "locked" : "denied");
    try {
      const res = await api.post<PunchResult>("/attendance/punch-in", {
        lat: pos.lat,
        lng: pos.lng,
        gps_available: pos.available,
      });
      if (res.allowed) {
        notify(`Punched in (${res.session_type})`, "success");
        await load();
      } else {
        notify(res.reason || "Punch blocked", "error");
      }
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Punch failed", "error");
    } finally {
      setBusy(false);
    }
  }

  async function punchOut() {
    setBusy(true);
    try {
      await api.post<AttendanceDay>("/attendance/punch-out");
      notify("Punched out", "success");
      await load();
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Punch-out failed", "error");
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <Spinner label="Loading…" />;

  return (
    <>
      <div className="card" style={{ textAlign: "center" }}>
        <p className="muted" style={{ margin: 0 }}>
          {new Date(now).toLocaleString([], {
            weekday: "long",
            day: "2-digit",
            month: "short",
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>

        {openSession ? (
          <>
            <h1 style={{ fontVariantNumeric: "tabular-nums", margin: "12px 0" }}>
              {elapsed(openSession.punch_in, now)}
            </h1>
            <p className="muted">Active session since {fmtTime(openSession.punch_in)}</p>
            <button className="accent" onClick={punchOut} disabled={busy} style={{ minWidth: 200 }}>
              Punch Out
            </button>
          </>
        ) : (
          <>
            <h2 style={{ margin: "12px 0" }}>
              {day && day.total_hours > 0
                ? `${day.total_hours}h logged today`
                : "Not punched in yet"}
            </h2>
            <button onClick={punchIn} disabled={busy} style={{ minWidth: 200 }}>
              {busy ? "Locating…" : "Punch In"}
            </button>
          </>
        )}

        <p className="muted" style={{ marginBottom: 0, marginTop: 14 }}>
          GPS:{" "}
          {gps === "locked"
            ? "🟢 locked"
            : gps === "searching"
              ? "🟡 searching…"
              : gps === "denied"
                ? "🔴 unavailable"
                : "—"}
        </p>
      </div>

      {day && day.sessions.length > 0 && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Today's sessions</h3>
          <table>
            <thead>
              <tr>
                <th>In</th>
                <th>Out</th>
                <th>Type</th>
              </tr>
            </thead>
            <tbody>
              {day.sessions.map((s) => (
                <tr key={s.id}>
                  <td>{fmtTime(s.punch_in)}</td>
                  <td>{fmtTime(s.punch_out)}</td>
                  <td>{s.type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
