import { useEffect, useState } from "react";
import { api, ApiError } from "../../api/client";
import type { Payslip } from "../../api/types";
import { Empty, Spinner } from "../../components/ui";
import { currentMonth, fmtMoney } from "../../lib/format";

function num(v: unknown): number {
  return typeof v === "number" ? v : 0;
}

export function MyPayslip() {
  const [month, setMonth] = useState(currentMonth());
  const [slip, setSlip] = useState<Payslip | null>(null);
  const [loading, setLoading] = useState(true);
  const [missing, setMissing] = useState(false);

  useEffect(() => {
    setLoading(true);
    setMissing(false);
    api
      .get<Payslip>(`/payroll/payslip/me/${month}`)
      .then((s) => {
        setSlip(s);
        setLoading(false);
      })
      .catch((err) => {
        setLoading(false);
        if (err instanceof ApiError && err.status === 404) setMissing(true);
      });
  }, [month]);

  const b = slip?.breakdown ?? {};

  return (
    <>
      <div className="row">
        <h2 style={{ margin: 0 }}>My Payslip</h2>
        <div className="spacer" />
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          style={{ width: "auto" }}
        />
        <button className="ghost" onClick={() => window.print()}>
          Print / PDF
        </button>
      </div>

      {loading ? (
        <Spinner />
      ) : missing || !slip ? (
        <Empty message="No payslip available for this month." />
      ) : (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>
            {String(b.full_name ?? "")} — {month}
          </h3>
          <p className="muted">
            {String(b.designation ?? "")} · {String(b.department ?? "")}
          </p>
          <table>
            <tbody>
              <tr>
                <td>Working days</td>
                <td>{num(b.working_days_in_month)}</td>
              </tr>
              <tr>
                <td>Days present</td>
                <td>{num(b.present_days)}</td>
              </tr>
              <tr>
                <td>Absent days</td>
                <td>{num(b.absent_days)}</td>
              </tr>
              <tr>
                <td>Paid leave days</td>
                <td>{num(b.paid_leave_days)}</td>
              </tr>
              <tr>
                <td>Unpaid leave days</td>
                <td>{num(b.ul_days)}</td>
              </tr>
              <tr>
                <td>Late marks (deduction hrs)</td>
                <td>
                  {num(b.late_marks)} ({num(b.late_mark_deduction_hours)}h)
                </td>
              </tr>
              <tr>
                <td>Paid hours</td>
                <td>{num(b.paid_hours)}</td>
              </tr>
              <tr>
                <td>Hourly rate</td>
                <td>{fmtMoney(num(b.hourly_rate))}</td>
              </tr>
              <tr>
                <td>Gross</td>
                <td>{fmtMoney(num(b.gross))}</td>
              </tr>
              <tr>
                <td>Fixed components</td>
                <td>{fmtMoney(num(b.fixed_components_total))}</td>
              </tr>
              <tr>
                <td>Deductions</td>
                <td>− {fmtMoney(num(b.deductions_total))}</td>
              </tr>
              <tr>
                <td>
                  <strong>Net pay</strong>
                </td>
                <td>
                  <strong>{fmtMoney(num(b.net))}</strong>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
