"""Seed the database with sample employees, settings, and leave balances.

Run: python -m app.seed   (idempotent — skips if employees already exist)

Admin: EMP008 / PIN 1234  (doc §4)
"""

from app.core.constants import BALANCE_LEAVE_TYPES, Category, Role
from app.core.security import hash_pin
from app.db.session import SessionLocal
from app.models.employee import Employee
from app.models.leave import LeaveBalance
from app.services.settings_service import get_settings

DEFAULT_PIN = "0000"

# (id, name, dept, category, designation, role, monthly_salary, wfh_limit, free_punch)
# Approved roster sourced from the live reference implementation.
EMPLOYEES = [
    ("EMP001", "Aditya Lashkare", "Office", Category.OFFICE, "Operations Executive", Role.EMPLOYEE, 42000, 0, False),
    ("EMP002", "Shubham Amale", "Office", Category.OFFICE, "Sales Executive", Role.EMPLOYEE, 40000, 0, False),
    ("EMP003", "Vinod Gawali", "Office", Category.OFFICE, "Sales Executive", Role.EMPLOYEE, 39000, 0, False),
    ("EMP004", "Altamash Shaikh", "Office", Category.OFFICE, "Sales Executive", Role.EMPLOYEE, 40000, 0, False),
    ("EMP005", "Manish Pardeshi", "Office", Category.OFFICE, "Sales Executive", Role.EMPLOYEE, 41000, 0, False),
    ("EMP006", "Tushar Yadav", "Office", Category.OFFICE, "Sales Manager", Role.MANAGER, 72000, 0, False),
    ("EMP007", "Ganesh Mahale", "Warehouse", Category.FIELD, "Warehouse Manager", Role.MANAGER, 72000, 0, False),
    ("EMP008", "Neelam Nikam", "Office", Category.OFFICE, "Accounts Manager", Role.ADMIN, 120000, 0, False),
    ("EMP009", "Devika Gaikwad", "Office", Category.OFFICE, "Sales Executive", Role.EMPLOYEE, 38000, 0, False),
    ("EMP010", "Ummehani Patanwala", "Office", Category.OFFICE, "Accounts Executive", Role.EMPLOYEE, 42000, 0, False),
    ("EMP011", "Eshwari Aher", "Office", Category.OFFICE, "Accounts Executive", Role.EMPLOYEE, 41000, 0, False),
    ("EMP012", "Simran Asija", "Office", Category.OFFICE, "Accounts Executive", Role.EMPLOYEE, 41000, 0, False),
    ("EMP013", "Raj Fadwale", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 35000, 0, False),
    ("EMP014", "Ajay Kachare", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 35000, 0, False),
    ("EMP015", "Sandeep Gulve", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 35000, 0, False),
    ("EMP016", "Sanjay K. Jain", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 35000, 0, False),
    ("EMP017", "Mahesh Bachhav", "Service", Category.SERVICE, "Service Technician", Role.EMPLOYEE, 36000, 0, False),
    ("EMP018", "Asif Khan", "Office", Category.OFFICE, "Sales Executive", Role.EMPLOYEE, 39000, 0, False),
    ("EMP019", "Satish Patil", "Service", Category.SERVICE, "Service Technician", Role.EMPLOYEE, 36000, 0, False),
    ("EMP020", "Sonu Wagh", "Service", Category.SERVICE, "Service Technician", Role.EMPLOYEE, 36000, 0, False),
    ("EMP021", "Zahid Patel", "Office", Category.OFFICE, "Sales Executive", Role.EMPLOYEE, 39000, 0, False),
    ("EMP022", "Akhil Aloysius", "Office", Category.OFFICE, "Sales Executive", Role.EMPLOYEE, 39000, 0, False),
    ("EMP023", "Ajay Shinde", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 34000, 0, False),
    ("EMP024", "Ramesh Mistry", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 34000, 0, False),
    ("EMP025", "Prasad Jadhav", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 34000, 0, False),
    ("EMP026", "Neha Gond", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 34000, 0, False),
    ("EMP027", "Sunita Jadhav", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 34000, 0, False),
    ("EMP028", "Nasrin Sayyad", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 34000, 0, False),
    ("EMP029", "Swapnil Nimbekar", "Service", Category.SERVICE, "Service Technician", Role.EMPLOYEE, 36000, 0, False),
    ("EMP030", "Deepak Nimbekar", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 36000, 0, True),
    ("EMP031", "Chhaya Sonawane", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 34000, 0, False),
    ("EMP032", "Nagesh Rao", "Office", Category.OFFICE, "Sales Executive", Role.EMPLOYEE, 39000, 0, False),
    ("EMP033", "Sagnik Paul", "Office", Category.OFFICE, "Sales Executive", Role.EMPLOYEE, 38000, 0, False),
    ("EMP034", "Varsha Sarode", "Warehouse", Category.FIELD, "Warehouse Associate", Role.EMPLOYEE, 34000, 0, False),
]

DEFAULT_BALANCES = {"EL": 18, "ML": 12, "FL": 8, "DL": 6, "DL2": 4}


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(Employee).count() > 0:
            print("Employees already present — skipping seed.")
            return

        for eid, name, dept, cat, desig, role, salary, wfh, free in EMPLOYEES:
            pin = "1234" if eid == "EMP008" else DEFAULT_PIN
            emp = Employee(
                id=eid,
                full_name=name,
                email=f"{eid.lower()}@prabha.example",
                department=dept,
                category=cat,
                designation=desig,
                role=role,
                monthly_salary=salary,
                wfh_limit=wfh,
                free_punch=free,
                fixed_components=[{"name": "HRA", "amount": round(salary * 0.1, 2)}],
                deductions=[{"name": "PF", "amount": round(salary * 0.04, 2)}],
                pin_hash=hash_pin(pin),
            )
            db.add(emp)
            for lt in BALANCE_LEAVE_TYPES:
                db.add(LeaveBalance(employee_id=eid, leave_type=lt, balance=DEFAULT_BALANCES[lt]))

        # Office location (example: Mumbai) and default radius.
        s = get_settings(db)
        s.office_lat = 19.0760
        s.office_lng = 72.8777
        db.commit()
        print(f"Seeded {len(EMPLOYEES)} employees. Admin: EMP008 / PIN 1234")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
