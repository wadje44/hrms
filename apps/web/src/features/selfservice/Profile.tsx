import { useEffect, useState } from "react";
import { api, ApiError } from "../../api/client";
import type { Employee } from "../../api/types";
import { useToast } from "../../components/Toast";
import { Spinner } from "../../components/ui";

export function Profile() {
  const { notify } = useToast();
  const [me, setMe] = useState<Employee | null>(null);
  const [pins, setPins] = useState({ current_pin: "", new_pin: "" });

  useEffect(() => {
    api.get<Employee>("/employees/me").then(setMe);
  }, []);

  async function changePin(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post("/auth/change-pin", pins);
      notify("PIN changed", "success");
      setPins({ current_pin: "", new_pin: "" });
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Failed", "error");
    }
  }

  if (!me) return <Spinner />;

  return (
    <>
      <h2 style={{ margin: 0 }}>Profile</h2>
      <div className="card" style={{ maxWidth: 460 }}>
        <table>
          <tbody>
            <tr>
              <td>ID</td>
              <td>{me.id}</td>
            </tr>
            <tr>
              <td>Name</td>
              <td>{me.full_name}</td>
            </tr>
            <tr>
              <td>Email</td>
              <td>{me.email ?? "—"}</td>
            </tr>
            <tr>
              <td>Department</td>
              <td>{me.department}</td>
            </tr>
            <tr>
              <td>Category</td>
              <td>{me.category}</td>
            </tr>
            <tr>
              <td>Designation</td>
              <td>{me.designation}</td>
            </tr>
            <tr>
              <td>Role</td>
              <td>{me.role}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <form className="card" onSubmit={changePin} style={{ maxWidth: 460 }}>
        <h3 style={{ marginTop: 0 }}>Change PIN</h3>
        <label>Current PIN</label>
        <input
          type="password"
          value={pins.current_pin}
          onChange={(e) => setPins({ ...pins, current_pin: e.target.value })}
          minLength={4}
          maxLength={8}
          required
        />
        <label>New PIN</label>
        <input
          type="password"
          value={pins.new_pin}
          onChange={(e) => setPins({ ...pins, new_pin: e.target.value })}
          minLength={4}
          maxLength={8}
          required
        />
        <button className="accent" type="submit" style={{ marginTop: 14 }}>
          Update PIN
        </button>
      </form>
    </>
  );
}
