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
