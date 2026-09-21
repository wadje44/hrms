import { useEffect, useState } from "react";
import { api, ApiError } from "../../api/client";
import type { WfhRequest } from "../../api/types";
import { useToast } from "../../components/Toast";
import { Empty, Spinner } from "../../components/ui";
import { fmtDate } from "../../lib/format";

export function MyWFH() {
  const { notify } = useToast();
  const [requests, setRequests] = useState<WfhRequest[] | null>(null);
  const [form, setForm] = useState({ date_from: "", date_to: "", reason: "" });

  async function load() {
    setRequests(await api.get<WfhRequest[]>("/wfh/me"));
  }

  useEffect(() => {
    load();
  }, []);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post("/wfh", form);
      notify("WFH request submitted", "success");
      setForm({ date_from: "", date_to: "", reason: "" });
      await load();
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Request failed", "error");
    }
  }

  if (!requests) return <Spinner label="Loading WFH…" />;

  return (
    <>
      <h2 style={{ margin: 0 }}>My WFH</h2>

      <form className="card" onSubmit={submit} style={{ maxWidth: 460 }}>
        <h3 style={{ marginTop: 0 }}>Request WFH</h3>
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
        <label>Reason</label>
        <textarea
          value={form.reason}
          onChange={(e) => setForm({ ...form, reason: e.target.value })}
          rows={3}
        />
        <button className="accent" type="submit" style={{ marginTop: 14 }}>
          Submit Request
        </button>
      </form>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>History</h3>
        {requests.length === 0 ? (
          <Empty message="No WFH requests yet." />
        ) : (
          <table>
            <thead>
              <tr>
                <th>From</th>
                <th>To</th>
                <th>Status</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((r) => (
                <tr key={r.id}>
                  <td>{fmtDate(r.date_from)}</td>
                  <td>{fmtDate(r.date_to)}</td>
                  <td>{r.status}</td>
                  <td>{r.reason || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
