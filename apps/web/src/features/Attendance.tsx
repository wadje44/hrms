import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { AttendanceDay, Employee } from "../api/types";
import { AttendanceTable } from "./AttendanceTable";
import { Empty, Spinner } from "../components/ui";

function currentMonth(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function monthBounds(month: string): [string, string] {
  const [y, m] = month.split("-").map(Number);
  const last = new Date(y, m, 0).getDate();
  return [`${month}-01`, `${month}-${String(last).padStart(2, "0")}`];
}

export function Attendance() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [empId, setEmpId] = useState("");
  const [month, setMonth] = useState(currentMonth());
  const [rows, setRows] = useState<AttendanceDay[] | null>(null);

  useEffect(() => {
    api.get<Employee[]>("/employees").then((list) => {
      setEmployees(list);
      if (list[0]) setEmpId(list[0].id);
    });
  }, []);

  useEffect(() => {
    if (!empId) return;
    const [from, to] = monthBounds(month);
    setRows(null);
    api.get<AttendanceDay[]>(`/attendance/${empId}?date_from=${from}&date_to=${to}`).then(setRows);
  }, [empId, month]);

  function exportCsv() {
    if (!rows) return;
    const header = ["Date", "Status", "Leave Type", "In", "Out", "Hours", "Late"];
    const lines = rows.map((day) => {
      const first = day.sessions[0];
      const last = day.sessions[day.sessions.length - 1];
      return [day.date, day.status, day.leave_type ?? "", first ? first.punch_in : "", last ? last.punch_out ?? "" : "", String(day.total_hours), day.is_late ? "Yes" : "No"];
    });
    const csv = [header, ...lines]
      .map((line) => line.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","))
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `attendance-${empId}-${month}.csv`;
    a.click();
  }

  return (
    <>
      <div className="row">
        <h2 style={{ margin: 0 }}>Attendance</h2>
        <div className="spacer" />
        <select value={empId} onChange={(e) => setEmpId(e.target.value)} style={{ width: "auto" }}>
          {employees.map((e) => (
            <option key={e.id} value={e.id}>
              {e.full_name} ({e.id})
            </option>
          ))}
        </select>
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          style={{ width: "auto" }}
        />
        <button className="ghost" onClick={exportCsv} disabled={!rows}>Export CSV</button>
      </div>
      {!rows ? (
        <Spinner />
      ) : rows.length === 0 ? (
        <Empty message="No records for this employee/month." />
      ) : (
        <AttendanceTable rows={rows} />
      )}
    </>
  );
}
