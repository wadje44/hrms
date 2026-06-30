import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import type { AppSettings } from "../api/types";
import { useToast } from "../components/Toast";
import { Spinner } from "../components/ui";

export function Settings() {
  const { notify } = useToast();
  const [s, setS] = useState<AppSettings | null>(null);

  useEffect(() => {
    api.get<AppSettings>("/settings").then(setS);
  }, []);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!s) return;
    try {
      const updated = await api.patch<AppSettings>("/settings", s);
      setS(updated);
      notify("Settings saved", "success");
    } catch (err) {
      notify(err instanceof ApiError ? err.message : "Save failed", "error");
    }
  }

  if (!s) return <Spinner label="Loading settings…" />;

  return (
    <>
      <h2 style={{ margin: 0 }}>Settings</h2>
      <form className="card" onSubmit={save} style={{ maxWidth: 460 }}>
        <label>Office latitude</label>
        <input
          type="number"
          step="any"
          value={s.office_lat ?? ""}
          onChange={(e) => setS({ ...s, office_lat: e.target.value === "" ? null : Number(e.target.value) })}
        />
        <label>Office longitude</label>
        <input
          type="number"
          step="any"
          value={s.office_lng ?? ""}
          onChange={(e) => setS({ ...s, office_lng: e.target.value === "" ? null : Number(e.target.value) })}
        />
        <label>Allowed radius (metres)</label>
        <input
          type="number"
          value={s.allowed_radius_m}
          onChange={(e) => setS({ ...s, allowed_radius_m: Number(e.target.value) })}
        />
        <label>Late cutoff (HH:MM)</label>
        <input value={s.late_cutoff} onChange={(e) => setS({ ...s, late_cutoff: e.target.value })} />
        <label>Free late marks per month</label>
        <input
          type="number"
          value={s.free_late_marks}
          onChange={(e) => setS({ ...s, free_late_marks: Number(e.target.value) })}
        />
        <label>Working hours per day</label>
        <input
          type="number"
          step="any"
          value={s.working_hours_per_day}
          onChange={(e) => setS({ ...s, working_hours_per_day: Number(e.target.value) })}
        />
        <label>Working days per month</label>
        <input
          type="number"
          value={s.working_days_per_month}
          onChange={(e) => setS({ ...s, working_days_per_month: Number(e.target.value) })}
        />
        <button className="accent" type="submit" style={{ marginTop: 14 }}>
          Save
        </button>
      </form>
    </>
  );
}
