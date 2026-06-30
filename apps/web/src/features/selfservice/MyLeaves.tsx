import { useEffect, useState } from "react";
import { api, ApiError } from "../../api/client";
import type { LeaveBalance, LeaveRequest, LeaveType } from "../../api/types";
import { useToast } from "../../components/Toast";
import { Empty, Spinner } from "../../components/ui";
import { fmtDate } from "../../lib/format";

const TYPES: LeaveType[] = ["EL", "ML", "FL", "DL", "DL2", "UL"];

export function MyLeaves() {
  const { notify } = useToast();
  const [balances, setBalances] = useState<LeaveBalance[] | null>(null);
  const [history, setHistory] = useState<LeaveRequest[]>([]);
  const [form, setForm] = useState({
    date_from: "",
    date_to: "",
    leave_type: "EL" as LeaveType,
    reason: "",
  });

  async function load() {
    const [b, h] = await Promise.all([
      api.get<LeaveBalance[]>("/leaves/balances/me"),
      api.get<LeaveRequest[]>("/leaves/me"),
    ]);
    setBalances(b);
    setHistory(h);
  }
  useEffect(() => {
    load();
  }, []);

  async function apply(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post("/leaves", form);
      notify("Leave request submitted", "success");
      setForm({ ...form, reason: "" });
      await load();
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Failed", "error");
    }
  }

  if (!balances) return <Spinner label="Loading…" />;

  return (
    <>
      <h2 style={{ margin: 0 }}>My Leaves</h2>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Balances</h3>
        <div className="stat-grid">
          {balances.map((b) => (
            <div key={b.leave_type} className="card">
              <div className="num">{b.balance}</div>
              <div className="label">{b.leave_type}</div>
            </div>
          ))}
        </div>
      </div>

      <form className="card" onSubmit={apply} style={{ maxWidth: 460 }}>
        <h3 style={{ marginTop: 0 }}>Apply for Leave</h3>
        <label>From</label>
        <input
          type="date"
          value={form.date_from}
          onChange={(e) => setForm({ ...form, date_from: e.target.value })}
          required
        />
        <label>To</label>
        <input
          type="date"
          value={form.date_to}
          onChange={(e) => setForm({ ...form, date_to: e.target.value })}
          required
        />
        <label>Type</label>
        <select
          value={form.leave_type}
          onChange={(e) => setForm({ ...form, leave_type: e.target.value as LeaveType })}
        >
          {TYPES.map((t) => (
            <option key={t}>{t}</option>
          ))}
        </select>
        <label>Reason</label>
        <textarea
          value={form.reason}
          onChange={(e) => setForm({ ...form, reason: e.target.value })}
          rows={2}
        />
        <button className="accent" type="submit" style={{ marginTop: 14 }}>
          Submit
        </button>
      </form>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>History</h3>
        {history.length === 0 ? (
          <Empty message="No leave requests yet." />
        ) : (
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>From</th>
                <th>To</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {history.map((l) => (
                <tr key={l.id}>
                  <td>{l.leave_type}</td>
                  <td>{fmtDate(l.date_from)}</td>
                  <td>{fmtDate(l.date_to)}</td>
                  <td>{l.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
