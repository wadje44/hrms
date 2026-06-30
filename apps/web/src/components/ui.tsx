import type { ReactNode } from "react";
import type { AttendanceStatus } from "../api/types";

export function Spinner({ label }: { label?: string }) {
  return (
    <div className="row" style={{ padding: 24, justifyContent: "center" }}>
      <div
        style={{
          width: 24,
          height: 24,
          border: "3px solid var(--border)",
          borderTopColor: "var(--navy)",
          borderRadius: "50%",
          animation: "spin 0.8s linear infinite",
        }}
      />
      {label && <span className="muted">{label}</span>}
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

export function Empty({ message }: { message: string }) {
  return (
    <div className="card" style={{ textAlign: "center", color: "var(--muted)" }}>
      {message}
    </div>
  );
}

export function Modal({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(20,30,60,0.45)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 16,
        zIndex: 900,
      }}
    >
      <div
        className="card"
        onClick={(e) => e.stopPropagation()}
        style={{ width: "100%", maxWidth: 480, maxHeight: "90vh", overflow: "auto" }}
      >
        <div className="row">
          <h3 style={{ margin: 0 }}>{title}</h3>
          <div className="spacer" />
          <button className="ghost" onClick={onClose}>
            ✕
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

const STATUS_LABEL: Record<AttendanceStatus, string> = {
  present: "Present",
  absent: "Absent",
  leave: "Leave",
  holiday: "Holiday",
  half_day: "Half-Day",
};

export function StatusBadge({ status, wfh }: { status: AttendanceStatus; wfh?: boolean }) {
  if (status === "present" && wfh) return <span className="badge wfh">WFH</span>;
  return <span className={`badge ${status}`}>{STATUS_LABEL[status]}</span>;
}
