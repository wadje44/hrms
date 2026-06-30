import { useEffect, useState } from "react";
import { api } from "../../api/client";
import type { AttendanceDay } from "../../api/types";
import { AttendanceTable } from "../AttendanceTable";
import { Empty, Spinner } from "../../components/ui";

function monthBounds(month: string): [string, string] {
  const [y, m] = month.split("-").map(Number);
  const last = new Date(y, m, 0).getDate();
  return [`${month}-01`, `${month}-${String(last).padStart(2, "0")}`];
}

function currentMonth(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

export function MyAttendance() {
  const [month, setMonth] = useState(currentMonth());
  const [rows, setRows] = useState<AttendanceDay[] | null>(null);

  useEffect(() => {
    const [from, to] = monthBounds(month);
    setRows(null);
    api.get<AttendanceDay[]>(`/attendance/me?date_from=${from}&date_to=${to}`).then(setRows);
  }, [month]);

  return (
    <>
      <div className="row">
        <h2 style={{ margin: 0 }}>My Attendance</h2>
        <div className="spacer" />
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          style={{ width: "auto" }}
        />
      </div>
      {!rows ? <Spinner /> : rows.length === 0 ? <Empty message="No records this month." /> : <AttendanceTable rows={rows} />}
    </>
  );
}
