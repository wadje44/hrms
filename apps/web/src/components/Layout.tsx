import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import type { Role } from "../api/types";

interface NavItem {
  to: string;
  label: string;
  roles: Role[];
}

const NAV: NavItem[] = [
  { to: "/", label: "Dashboard", roles: ["admin", "manager"] },
  { to: "/employees", label: "Employees", roles: ["admin"] },
  { to: "/attendance", label: "Attendance", roles: ["admin", "manager"] },
  { to: "/leaves", label: "Leaves", roles: ["admin", "manager"] },
  { to: "/payroll", label: "Payroll", roles: ["admin"] },
  { to: "/settings", label: "Settings", roles: ["admin"] },
  { to: "/me", label: "Punch / Home", roles: ["admin", "manager", "employee"] },
  { to: "/my-attendance", label: "My Attendance", roles: ["admin", "manager", "employee"] },
  { to: "/my-leaves", label: "My Leaves", roles: ["admin", "manager", "employee"] },
  { to: "/my-payslip", label: "My Payslip", roles: ["admin", "manager", "employee"] },
  { to: "/profile", label: "Profile", roles: ["admin", "manager", "employee"] },
];

export function Layout() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  if (!user) return null;
  const items = NAV.filter((n) => n.roles.includes(user.role));

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <aside
        style={{
          width: 230,
          background: "var(--navy)",
          color: "#fff",
          padding: 16,
          position: "fixed",
          top: 0,
          bottom: 0,
          left: open ? 0 : undefined,
          transform: open ? "none" : "translateX(-100%)",
          transition: "transform 0.2s ease",
          zIndex: 800,
        }}
        className="sidebar"
      >
        <h2 style={{ marginTop: 0 }}>
          Prabha <span style={{ color: "var(--orange)" }}>HRMS</span>
        </h2>
        <nav style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {items.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.to === "/"}
              onClick={() => setOpen(false)}
              style={({ isActive }) => ({
                color: "#fff",
                textDecoration: "none",
                padding: "10px 12px",
                borderRadius: 8,
                background: isActive ? "rgba(255,255,255,0.16)" : "transparent",
              })}
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="content" style={{ flex: 1, marginLeft: 230 }}>
        <header
          className="row"
          style={{
            background: "#fff",
            padding: "12px 20px",
            borderBottom: "1px solid var(--border)",
            position: "sticky",
            top: 0,
            zIndex: 700,
          }}
        >
          <button className="ghost hamburger" onClick={() => setOpen((o) => !o)} style={{ display: "none" }}>
            ☰
          </button>
          <strong>{user.fullName}</strong>
          <span className="badge" style={{ background: "var(--orange)" }}>
            {user.role}
          </span>
          <div className="spacer" />
          <button className="ghost" onClick={logout}>
            Logout
          </button>
        </header>
        <main style={{ padding: 20, display: "flex", flexDirection: "column", gap: 16 }}>
          <Outlet />
        </main>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .content { margin-left: 0 !important; }
          .hamburger { display: inline-flex !important; }
        }
        @media (min-width: 769px) {
          .sidebar { transform: none !important; }
        }
      `}</style>
    </div>
  );
}
