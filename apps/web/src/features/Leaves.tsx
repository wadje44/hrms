import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import type { LeaveRequest } from "../api/types";
import { useToast } from "../components/Toast";
import { Empty, Spinner } from "../components/ui";
import { fmtDate } from "../lib/format";

export function Leaves() {
  const { notify } = useToast();
  const [pending, setPending] = useState<LeaveRequest[] | null>(null);

  async function load() {
    setPending(await api.get<LeaveRequest[]>("/leaves/pending"));
  }
  useEffect(() => {
    load();
  }, []);

  async function review(id: number, approve: boolean) {
    try {
      await api.post(`/leaves/${id}/review`, { approve, comment: "" });
      notify(approve ? "Leave approved" : "Leave rejected", "success");
      await load();
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Action failed", "error");
    }
  }

  if (!pending) return <Spinner label="Loading leave requests…" />;

  return (
    <>
      <h2 style={{ margin: 0 }}>Pending Leave Requests</h2>
      {pending.length === 0 ? (
        <Empty message="No pending leave requests." />
      ) : (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>Employee</th>
                <th>Type</th>
                <th>From</th>
                <th>To</th>
                <th>Reason</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {pending.map((l) => (
                <tr key={l.id}>
                  <td>{l.employee_id}</td>
                  <td>
                    <span className="badge leave">{l.leave_type}</span>
                  </td>
                  <td>{fmtDate(l.date_from)}</td>
                  <td>{fmtDate(l.date_to)}</td>
                  <td>{l.reason}</td>
                  <td>
                    <div className="row">
                      <button className="accent" onClick={() => review(l.id, true)}>
                        Approve
                      </button>
                      <button className="ghost" onClick={() => review(l.id, false)}>
                        Reject
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
