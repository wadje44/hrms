import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import type { AppSettings } from "../api/types";
import { useToast } from "../components/Toast";
import { Spinner } from "../components/ui";

interface DeviceConfig {
  device_name: string;
  firebase_project_id: string;
  firebase_api_key: string;
  firebase_app_id: string;
  storage_bucket: string;
  notes: string;
}

const STORAGE_KEY = "hrms_device_config";

export function Settings() {
  const { notify } = useToast();
  const [s, setS] = useState<AppSettings | null>(null);
  const [device, setDevice] = useState<DeviceConfig>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? (JSON.parse(raw) as DeviceConfig) : { device_name: "", firebase_project_id: "", firebase_api_key: "", firebase_app_id: "", storage_bucket: "", notes: "" };
    } catch {
      return { device_name: "", firebase_project_id: "", firebase_api_key: "", firebase_app_id: "", storage_bucket: "", notes: "" };
    }
  });

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

  function saveDeviceConfig(e: React.FormEvent) {
    e.preventDefault();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(device));
    notify("Device setup saved locally", "success");
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

      <form className="card" onSubmit={saveDeviceConfig} style={{ maxWidth: 520, marginTop: 16 }}>
        <h3 style={{ marginTop: 0 }}>Device setup</h3>
        <p className="muted" style={{ marginTop: 0 }}>
          First-time configuration for the attendance device or kiosk.
        </p>
        <label>Device name</label>
        <input value={device.device_name} onChange={(e) => setDevice({ ...device, device_name: e.target.value })} />
        <label>Firebase project ID</label>
        <input value={device.firebase_project_id} onChange={(e) => setDevice({ ...device, firebase_project_id: e.target.value })} />
        <label>Firebase API key</label>
        <input value={device.firebase_api_key} onChange={(e) => setDevice({ ...device, firebase_api_key: e.target.value })} />
        <label>Firebase app ID</label>
        <input value={device.firebase_app_id} onChange={(e) => setDevice({ ...device, firebase_app_id: e.target.value })} />
        <label>Storage bucket</label>
        <input value={device.storage_bucket} onChange={(e) => setDevice({ ...device, storage_bucket: e.target.value })} />
        <label>Notes</label>
        <textarea value={device.notes} onChange={(e) => setDevice({ ...device, notes: e.target.value })} rows={4} />
        <button className="accent" type="submit" style={{ marginTop: 14 }}>
          Save device config
        </button>
      </form>
    </>
  );
}
