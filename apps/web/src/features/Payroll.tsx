import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import type { PayrollSummaryRow } from "../api/types";
import { useToast } from "../components/Toast";
import { Empty, Spinner } from "../components/ui";
import { currentMonth, fmtMoney } from "../lib/format";

export function Payroll() {
  const { notify } = useToast();
  const [month, setMonth] = useState(currentMonth());
  const [rows, setRows] = useState<PayrollSummaryRow[] | null>(null);
  const [busy, setBusy] = useState(false);

  async function load(m: string) {
    setRows(null);
    setRows(await api.get<PayrollSummaryRow[]>(`/payroll/summary/${m}`));
  }
  useEffect(() => {
    load(month);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function run() {
    setBusy(true);
    try {
      await api.post(`/payroll/run/${month}`);
      notify(`Payroll run for ${month}`, "success");
      await load(month);
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Run failed", "error");
    } finally {
      setBusy(false);
    }
  }

  function exportCsv() {
    if (!rows) return;
    const header = "ID,Name,Dept,Present,Late,Hours,Gross,Deductions,Net";
    const lines = rows.map(
      (r) =>
        `${r.employee_id},${r.full_name},${r.department},${r.present_days},${r.late_marks},${r.worked_hours},${r.gross},${r.deductions_total},${r.net}`,
    );
    const blob = new Blob([[header, ...lines].join("\n")], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `payroll-${month}.csv`;
    a.click();
  }

  const totals = (rows ?? []).reduce(
    (acc, r) => ({
      gross: acc.gross + r.gross,
      ded: acc.ded + r.deductions_total,
      net: acc.net + r.net,
    }),
    { gross: 0, ded: 0, net: 0 },
  );

  return (
    <>
      <div className="row">
        <h2 style={{ margin: 0 }}>Payroll</h2>
        <div className="spacer" />
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          style={{ width: "auto" }}
        />
        <button onClick={() => load(month)} className="ghost">
          View
        </button>
        <button onClick={run} disabled={busy} className="accent">
          {busy ? "Running…" : "Run Payroll"}
        </button>
        <button onClick={exportCsv} className="ghost">
          Export CSV
        </button>
      </div>

      {!rows ? (
        <Spinner label="Loading…" />
      ) : rows.length === 0 ? (
        <Empty message="No payroll for this month yet. Click Run Payroll." />
      ) : (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Dept</th>
                <th>Present</th>
                <th>Late</th>
                <th>Hours</th>
                <th>Gross</th>
                <th>Deductions</th>
                <th>Net</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.employee_id}>
                  <td>{r.employee_id}</td>
                  <td>{r.full_name}</td>
                  <td>{r.department}</td>
                  <td>{r.present_days}</td>
                  <td>{r.late_marks}</td>
                  <td>{r.worked_hours}</td>
                  <td>{fmtMoney(r.gross)}</td>
                  <td>{fmtMoney(r.deductions_total)}</td>
                  <td>
                    <strong>{fmtMoney(r.net)}</strong>
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan={6}>
                  <strong>Totals</strong>
                </td>
                <td>{fmtMoney(totals.gross)}</td>
                <td>{fmtMoney(totals.ded)}</td>
                <td>
                  <strong>{fmtMoney(totals.net)}</strong>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </>
  );
}
