import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import type { WfhRequest } from "../api/types";
import { useToast } from "../components/Toast";
import { Empty, Spinner } from "../components/ui";
import { fmtDate } from "../lib/format";

export function WFH() {
  const { notify } = useToast();
  const [pending, setPending] = useState<WfhRequest[] | null>(null);

  async function load() {
    setPending(await api.get<WfhRequest[]>("/wfh/pending"));
  }

  useEffect(() => {
    load();
  }, []);

  async function review(id: number, approve: boolean) {
    try {
      await api.post(`/wfh/${id}/review`, { approve, comment: "" });
      notify(approve ? "WFH approved" : "WFH rejected", "success");
      await load();
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Action failed", "error");
    }
  }

  if (!pending) return <Spinner label="Loading WFH requests…" />;

  return (
    <>
      <h2 style={{ margin: 0 }}>Pending WFH Requests</h2>
      {pending.length === 0 ? (
        <Empty message="No pending WFH requests." />
      ) : (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>Employee</th>
                <th>From</th>
                <th>To</th>
                <th>Reason</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {pending.map((r) => (
                <tr key={r.id}>
                  <td>{r.employee_id}</td>
                  <td>{fmtDate(r.date_from)}</td>
                  <td>{fmtDate(r.date_to)}</td>
                  <td>{r.reason || "—"}</td>
                  <td>
                    <div className="row">
                      <button className="accent" onClick={() => review(r.id, true)}>
                        Approve
                      </button>
                      <button className="ghost" onClick={() => review(r.id, false)}>
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
