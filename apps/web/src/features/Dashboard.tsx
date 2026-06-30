import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { DashboardSummary, EmployeeRef } from "../api/types";
import { Modal, Spinner } from "../components/ui";

interface Drill {
  title: string;
  rows: EmployeeRef[];
}

export function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [drill, setDrill] = useState<Drill | null>(null);

  useEffect(() => {
    api.get<DashboardSummary>("/dashboard/today").then(setData);
  }, []);

  if (!data) return <Spinner label="Loading dashboard…" />;

  const cards: { label: string; rows: EmployeeRef[] }[] = [
    { label: "Present Today", rows: data.present },
    { label: "Absent Today", rows: data.absent },
    { label: "Late Today", rows: data.late },
    { label: "On Leave Today", rows: data.on_leave },
    { label: "Currently Punched In", rows: data.currently_in },
  ];

  return (
    <>
      <h2 style={{ margin: 0 }}>Dashboard — {data.date}</h2>
      <div className="stat-grid">
        {cards.map((c) => (
          <div
            key={c.label}
            className="card stat-card"
            role="button"
            tabIndex={0}
            onClick={() => setDrill({ title: c.label, rows: c.rows })}
            onKeyDown={(e) => e.key === "Enter" && setDrill({ title: c.label, rows: c.rows })}
          >
            <div className="num">{c.rows.length}</div>
            <div className="label">{c.label}</div>
          </div>
        ))}
      </div>

      {drill && (
        <Modal title={drill.title} onClose={() => setDrill(null)}>
          {drill.rows.length === 0 ? (
            <p className="muted">No employees.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Detail</th>
                </tr>
              </thead>
              <tbody>
                {drill.rows.map((r) => (
                  <tr key={r.employee_id}>
                    <td>{r.employee_id}</td>
                    <td>{r.full_name}</td>
                    <td>{r.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Modal>
      )}
    </>
  );
}
