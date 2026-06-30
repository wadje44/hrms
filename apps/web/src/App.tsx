import { Navigate, Route, Routes } from "react-router-dom";
import { RequireAuth } from "./auth/RequireAuth";
import { Layout } from "./components/Layout";
import { Attendance } from "./features/Attendance";
import { Dashboard } from "./features/Dashboard";
import { Employees } from "./features/Employees";
import { Leaves } from "./features/Leaves";
import { Login } from "./features/Login";
import { Payroll } from "./features/Payroll";
import { Settings } from "./features/Settings";
import { MyAttendance } from "./features/selfservice/MyAttendance";
import { MyLeaves } from "./features/selfservice/MyLeaves";
import { MyPayslip } from "./features/selfservice/MyPayslip";
import { Profile } from "./features/selfservice/Profile";
import { Punch } from "./features/selfservice/Punch";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        {/* Admin / manager */}
        <Route
          index
          element={
            <RequireAuth roles={["admin", "manager"]}>
              <Dashboard />
            </RequireAuth>
          }
        />
        <Route
          path="employees"
          element={
            <RequireAuth roles={["admin"]}>
              <Employees />
            </RequireAuth>
          }
        />
        <Route
          path="attendance"
          element={
            <RequireAuth roles={["admin", "manager"]}>
              <Attendance />
            </RequireAuth>
          }
        />
        <Route
          path="leaves"
          element={
            <RequireAuth roles={["admin", "manager"]}>
              <Leaves />
            </RequireAuth>
          }
        />
        <Route
          path="payroll"
          element={
            <RequireAuth roles={["admin"]}>
              <Payroll />
            </RequireAuth>
          }
        />
        <Route
          path="settings"
          element={
            <RequireAuth roles={["admin"]}>
              <Settings />
            </RequireAuth>
          }
        />

        {/* Self-service (all roles) */}
        <Route path="me" element={<Punch />} />
        <Route path="my-attendance" element={<MyAttendance />} />
        <Route path="my-leaves" element={<MyLeaves />} />
        <Route path="my-payslip" element={<MyPayslip />} />
        <Route path="profile" element={<Profile />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
