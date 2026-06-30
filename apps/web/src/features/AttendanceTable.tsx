import type { AttendanceDay } from "../api/types";
import { StatusBadge } from "../components/ui";
import { fmtDate, fmtTime } from "../lib/format";

export function AttendanceTable({ rows }: { rows: AttendanceDay[] }) {
  return (
    <div className="card">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Status</th>
            <th>In</th>
            <th>Out</th>
            <th>Hours</th>
            <th>Late</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((d) => {
            const first = d.sessions[0];
            const last = d.sessions[d.sessions.length - 1];
            return (
              <tr key={d.id}>
                <td>{fmtDate(d.date)}</td>
                <td>
                  <StatusBadge status={d.status} wfh={d.is_wfh} />
                  {d.leave_type && <span className="muted"> {d.leave_type}</span>}
                </td>
                <td>{first ? fmtTime(first.punch_in) : "—"}</td>
                <td>{last ? fmtTime(last.punch_out) : "—"}</td>
                <td>{d.total_hours}</td>
                <td>{d.is_late ? <span className="badge late">Late</span> : "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
