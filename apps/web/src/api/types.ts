export type Role = "admin" | "manager" | "employee";
export type Category = "office" | "hybrid" | "field" | "service";
export type AttendanceStatus =
  | "present"
  | "absent"
  | "leave"
  | "holiday"
  | "half_day";
export type SessionType = "office" | "wfh" | "field";
export type LeaveType = "EL" | "ML" | "FL" | "DL" | "DL2" | "UL";

export interface LoginResponse {
  access_token: string;
  token_type: string;
  employee_id: string;
  full_name: string;
  role: Role;
}

export interface PublicEmployee {
  id: string;
  full_name: string;
}

export interface PayComponent {
  name: string;
  amount: number;
}

export interface Employee {
  id: string;
  full_name: string;
  email: string | null;
  department: string;
  category: Category;
  designation: string;
  role: Role;
  monthly_salary: number;
  hourly_rate: number | null;
  fixed_components: PayComponent[];
  deductions: PayComponent[];
  wfh_limit: number;
  free_punch: boolean;
  active: boolean;
}

export interface PunchResult {
  allowed: boolean;
  session_type: SessionType;
  is_wfh: boolean;
  is_field_duty: boolean;
  distance_m: number | null;
  reason: string;
}

export interface AttendanceSession {
  id: number;
  punch_in: string;
  punch_out: string | null;
  lat: number | null;
  lng: number | null;
  type: SessionType;
}

export interface AttendanceDay {
  id: number;
  employee_id: string;
  date: string;
  status: AttendanceStatus;
  leave_type: LeaveType | null;
  total_hours: number;
  paid_hours: number;
  is_wfh: boolean;
  is_field_duty: boolean;
  is_late: boolean;
  manual_override: boolean;
  sessions: AttendanceSession[];
}

export interface LeaveRequest {
  id: number;
  employee_id: string;
  date_from: string;
  date_to: string;
  leave_type: LeaveType;
  reason: string;
  status: string;
  reviewed_by: string | null;
  review_date: string | null;
  comment: string;
  created_at: string;
}

export interface LeaveBalance {
  leave_type: LeaveType;
  balance: number;
}

export interface Payslip {
  month: string;
  employee_id: string;
  gross: number;
  deductions_total: number;
  net: number;
  breakdown: Record<string, unknown>;
}

export interface PayrollSummaryRow {
  employee_id: string;
  full_name: string;
  department: string;
  present_days: number;
  late_marks: number;
  worked_hours: number;
  gross: number;
  deductions_total: number;
  net: number;
}

export interface EmployeeRef {
  employee_id: string;
  full_name: string;
  detail: string;
}

export interface DashboardSummary {
  date: string;
  present: EmployeeRef[];
  absent: EmployeeRef[];
  late: EmployeeRef[];
  on_leave: EmployeeRef[];
  currently_in: EmployeeRef[];
}

export interface AppSettings {
  office_lat: number | null;
  office_lng: number | null;
  allowed_radius_m: number;
  late_cutoff: string;
  free_late_marks: number;
  working_hours_per_day: number;
  working_days_per_month: number;
  holidays: string[];
}
