import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { AttendanceDay, Employee, YtdEarningsRow } from "../api/types";
import { Empty, Spinner } from "../components/ui";
import { fmtMoney } from "../lib/format";

interface MonthlyReportSummary {
  month: string;
  present: number;
  absent: number;
  late: number;
  leave: number;
  wfh: number;
  avg_hours: number;
}

interface EmployeeStatusRow {
  employee_id: string;
  full_name: string;
  statuses: Array<AttendanceDay | null>;
}

function currentMonth(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function monthBounds(month: string): [string, string] {
  const [year, mon] = month.split("-").map(Number);
  const last = new Date(year, mon, 0).getDate();
  return [`${month}-01`, `${month}-${String(last).padStart(2, "0")}`];
}

function statusLabel(day: AttendanceDay | null): string {
  if (!day) return "—";
  if (day.status === "present") return day.is_wfh ? "WFH" : "P";
  if (day.status === "leave") return day.leave_type ?? "L";
  if (day.status === "absent") return "A";
  if (day.status === "holiday") return "H";
  if (day.status === "half_day") return "HD";
  return "P";
}

export function Reports() {
  const [month, setMonth] = useState(currentMonth());
  const [data, setData] = useState<MonthlyReportSummary | null>(null);
  const [ytd, setYtd] = useState<YtdEarningsRow[] | null>(null);
  const [rows, setRows] = useState<EmployeeStatusRow[] | null>(null);
  const [days, setDays] = useState<string[]>([]);

  useEffect(() => {
    const [from, to] = monthBounds(month);
    const last = new Date(from).getDate();
    const dateList: string[] = [];
    for (let i = 1; i <= last; i += 1) {
      dateList.push(`${month}-${String(i).padStart(2, "0")}`);
    }
    setDays(dateList);

    const load = async () => {
      const [summary, employees, ytdRows] = await Promise.all([
        api.get<MonthlyReportSummary>(`/reports/monthly/${month}`),
        api.get<Employee[]>("/employees"),
        api.get<YtdEarningsRow[]>("/reports/ytd-earnings/aggregate"),
      ]);
      setData(summary);
      setYtd(ytdRows);

      const attendanceLists = await Promise.all(
        employees.map((emp) =>
          api.get<AttendanceDay[]>(`/attendance/${emp.id}?date_from=${from}&date_to=${to}`),
        ),
      );

      const byEmployee = new Map<string, Map<string, AttendanceDay>>();
      employees.forEach((emp, idx) => {
        const map = new Map<string, AttendanceDay>();
        attendanceLists[idx].forEach((day) => map.set(day.date, day));
        byEmployee.set(emp.id, map);
      });

      const employeeRows = employees.map((emp) => ({
        employee_id: emp.id,
        full_name: emp.full_name,
        statuses: dateList.map((d) => byEmployee.get(emp.id)?.get(d) ?? null),
      }));
      setRows(employeeRows);
    };

    load().catch(() => {
      setData(null);
      setYtd(null);
      setRows(null);
    });
  }, [month]);

  function exportCsv() {
    if (!rows || days.length === 0) return;
    const header = ["Employee ID", "Name", ...days];
    const lines = rows.map((row) => [row.employee_id, row.full_name, ...row.statuses.map((d) => statusLabel(d))]);
    const csv = [header, ...lines].map((line) => line.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `attendance-${month}.csv`;
    a.click();
  }

  const ytdTotal = (ytd ?? []).reduce((sum, row) => sum + row.ytd_earnings, 0);

  return (
    <>
      <div className="row">
        <h2 style={{ margin: 0 }}>Reports</h2>
        <div className="spacer" />
        <button className="ghost" onClick={exportCsv} disabled={!rows}>Export CSV</button>
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          style={{ width: "auto" }}
        />
      </div>

      {!data ? (
        <Spinner label="Loading report…" />
      ) : (
        <>
          {data.present === 0 && data.absent === 0 && data.late === 0 && data.leave === 0 && data.wfh === 0 ? (
            <Empty message="No attendance data for this month yet." />
          ) : (
            <div className="stat-grid">
              <div className="card stat-card"><div className="num">{data.present}</div><div className="label">Present</div></div>
              <div className="card stat-card"><div className="num">{data.absent}</div><div className="label">Absent</div></div>
              <div className="card stat-card"><div className="num">{data.late}</div><div className="label">Late marks</div></div>
              <div className="card stat-card"><div className="num">{data.leave}</div><div className="label">Leave</div></div>
              <div className="card stat-card"><div className="num">{data.wfh}</div><div className="label">WFH</div></div>
              <div className="card stat-card"><div className="num">{data.avg_hours.toFixed(2)}</div><div className="label">Avg hrs</div></div>
              <div className="card stat-card"><div className="num">{fmtMoney(ytdTotal)}</div><div className="label">YTD earnings</div></div>
            </div>
          )}

          {ytd && ytd.length > 0 && (
            <div className="card" style={{ marginTop: 18 }}>
              <h3 style={{ marginTop: 0 }}>Year-to-date earnings</h3>
              <table>
                <thead>
                  <tr>
                    <th>Employee</th>
                    <th>YTD earnings</th>
                  </tr>
                </thead>
                <tbody>
                  {ytd.map((row) => (
                    <tr key={row.employee_id}>
                      <td>{row.full_name}</td>
                      <td>{fmtMoney(row.ytd_earnings)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {rows && rows.length > 0 && (
            <div className="card" style={{ overflowX: "auto", marginTop: 18 }}>
              <table>
                <thead>
                  <tr>
                    <th>Employee</th>
                    {days.map((d) => (
                      <th key={d} style={{ minWidth: 28, textAlign: "center" }}>{d.slice(8, 10)}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={row.employee_id}>
                      <td>{row.full_name}</td>
                      {row.statuses.map((day, idx) => (
                        <td key={`${row.employee_id}-${days[idx]}`} style={{ textAlign: "center" }}>
                          {statusLabel(day)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </>
  );
}
