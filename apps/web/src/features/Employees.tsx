import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import type { Category, Employee, Role } from "../api/types";
import { useToast } from "../components/Toast";
import { Modal, Spinner } from "../components/ui";
import { fmtMoney } from "../lib/format";

const CATEGORIES: Category[] = ["office", "hybrid", "field", "service"];
const ROLES: Role[] = ["employee", "manager", "admin"];

const BLANK = {
  id: "",
  full_name: "",
  email: "",
  department: "",
  category: "office" as Category,
  designation: "",
  role: "employee" as Role,
  monthly_salary: 0,
  wfh_limit: 0,
  free_punch: false,
  pin: "",
};

export function Employees() {
  const { notify } = useToast();
  const [rows, setRows] = useState<Employee[] | null>(null);
  const [adding, setAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<Employee> | null>(null);
  const [form, setForm] = useState({ ...BLANK });

  async function load() {
    setRows(await api.get<Employee[]>("/employees"));
  }
  useEffect(() => {
    load();
  }, []);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post("/employees", { ...form, fixed_components: [], deductions: [] });
      notify("Employee added", "success");
      setAdding(false);
      setForm({ ...BLANK });
      await load();
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Failed", "error");
    }
  }

  async function deactivate(id: string) {
    await api.del(`/employees/${id}`);
    notify("Employee deactivated", "info");
    await load();
  }

  function startEdit(emp: Employee) {
    setEditingId(emp.id);
    setEditForm({
      full_name: emp.full_name,
      email: emp.email ?? "",
      department: emp.department,
      category: emp.category,
      designation: emp.designation,
      role: emp.role,
      monthly_salary: emp.monthly_salary,
      wfh_limit: emp.wfh_limit,
      free_punch: emp.free_punch,
      active: emp.active,
    });
  }

  async function saveEdit(e: React.FormEvent) {
    e.preventDefault();
    if (!editingId || !editForm) return;
    try {
      await api.patch(`/employees/${editingId}`, editForm);
      notify("Employee updated", "success");
      setEditingId(null);
      setEditForm(null);
      await load();
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Update failed", "error");
    }
  }

  if (!rows) return <Spinner label="Loading employees…" />;

  return (
    <>
      <div className="row">
        <h2 style={{ margin: 0 }}>Employees</h2>
        <div className="spacer" />
        <button className="accent" onClick={() => setAdding(true)}>
          + Add Employee
        </button>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Dept</th>
              <th>Category</th>
              <th>Role</th>
              <th>Salary</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((e) => (
              <tr key={e.id} style={{ opacity: e.active ? 1 : 0.5 }}>
                <td>{e.id}</td>
                <td>{e.full_name}</td>
                <td>{e.department}</td>
                <td>{e.category}</td>
                <td>{e.role}</td>
                <td>{fmtMoney(e.monthly_salary)}</td>
                <td>{e.active ? "Active" : "Inactive"}</td>
                <td>
                  <div className="row" style={{ gap: 8, justifyContent: "flex-end" }}>
                    <button className="ghost" onClick={() => startEdit(e)}>
                      Edit
                    </button>
                    {e.active && (
                      <button className="ghost" onClick={() => deactivate(e.id)}>
                        Deactivate
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {adding && (
        <Modal title="Add Employee" onClose={() => setAdding(false)}>
          <form onSubmit={create}>
            <label>Employee ID</label>
            <input value={form.id} onChange={(e) => setForm({ ...form, id: e.target.value })} required />
            <label>Full name</label>
            <input
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              required
            />
            <label>Email</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
            <label>Department</label>
            <input
              value={form.department}
              onChange={(e) => setForm({ ...form, department: e.target.value })}
              required
            />
            <label>Category</label>
            <select
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value as Category })}
            >
              {CATEGORIES.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
            <label>Role</label>
            <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value as Role })}>
              {ROLES.map((r) => (
                <option key={r}>{r}</option>
              ))}
            </select>
            <label>Monthly salary</label>
            <input
              type="number"
              value={form.monthly_salary}
              onChange={(e) => setForm({ ...form, monthly_salary: Number(e.target.value) })}
            />
            <label>WFH limit (per month)</label>
            <input
              type="number"
              value={form.wfh_limit}
              onChange={(e) => setForm({ ...form, wfh_limit: Number(e.target.value) })}
            />
            <label>
              <input
                type="checkbox"
                checked={form.free_punch}
                onChange={(e) => setForm({ ...form, free_punch: e.target.checked })}
                style={{ width: "auto", minHeight: 0, marginRight: 8 }}
              />
              Free punch (bypass GPS)
            </label>
            <label>Initial PIN</label>
            <input
              value={form.pin}
              onChange={(e) => setForm({ ...form, pin: e.target.value })}
              minLength={4}
              maxLength={8}
              required
            />
            <button className="accent" type="submit" style={{ width: "100%", marginTop: 14 }}>
              Create
            </button>
          </form>
        </Modal>
      )}

      {editingId && editForm && (
        <Modal title="Edit Employee" onClose={() => { setEditingId(null); setEditForm(null); }}>
          <form onSubmit={saveEdit}>
            <label>Full name</label>
            <input
              value={editForm.full_name ?? ""}
              onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
              required
            />
            <label>Email</label>
            <input
              type="email"
              value={editForm.email ?? ""}
              onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
            />
            <label>Department</label>
            <input
              value={editForm.department ?? ""}
              onChange={(e) => setEditForm({ ...editForm, department: e.target.value })}
              required
            />
            <label>Category</label>
            <select
              value={editForm.category ?? "office"}
              onChange={(e) => setEditForm({ ...editForm, category: e.target.value as Category })}
            >
              {CATEGORIES.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
            <label>Designation</label>
            <input
              value={editForm.designation ?? ""}
              onChange={(e) => setEditForm({ ...editForm, designation: e.target.value })}
            />
            <label>Role</label>
            <select
              value={editForm.role ?? "employee"}
              onChange={(e) => setEditForm({ ...editForm, role: e.target.value as Role })}
            >
              {ROLES.map((r) => (
                <option key={r}>{r}</option>
              ))}
            </select>
            <label>Monthly salary</label>
            <input
              type="number"
              value={editForm.monthly_salary ?? 0}
              onChange={(e) => setEditForm({ ...editForm, monthly_salary: Number(e.target.value) })}
            />
            <label>WFH limit (per month)</label>
            <input
              type="number"
              value={editForm.wfh_limit ?? 0}
              onChange={(e) => setEditForm({ ...editForm, wfh_limit: Number(e.target.value) })}
            />
            <label>
              <input
                type="checkbox"
                checked={Boolean(editForm.free_punch)}
                onChange={(e) => setEditForm({ ...editForm, free_punch: e.target.checked })}
                style={{ width: "auto", minHeight: 0, marginRight: 8 }}
              />
              Free punch (bypass GPS)
            </label>
            <button className="accent" type="submit" style={{ width: "100%", marginTop: 14 }}>
              Save changes
            </button>
          </form>
        </Modal>
      )}
    </>
  );
}
