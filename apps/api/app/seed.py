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
EMPLOYEES = [
    (
        "EMP001",
        "Aarti Sharma",
        "Office",
        Category.OFFICE,
        "Accountant",
        Role.EMPLOYEE,
        45000,
        0,
        False,
    ),
    (
        "EMP002",
        "Rohit Verma",
        "Office",
        Category.OFFICE,
        "HR Executive",
        Role.EMPLOYEE,
        42000,
        0,
        False,
    ),
    (
        "EMP003",
        "Sneha Patil",
        "Office",
        Category.OFFICE,
        "Admin Assistant",
        Role.EMPLOYEE,
        38000,
        0,
        False,
    ),
    (
        "EMP004",
        "Kunal Joshi",
        "Hybrid",
        Category.HYBRID,
        "Software Engineer",
        Role.EMPLOYEE,
        65000,
        8,
        False,
    ),
    ("EMP005", "Priya Nair", "Hybrid", Category.HYBRID, "Designer", Role.EMPLOYEE, 60000, 8, False),
    (
        "EMP006",
        "Tushar Kale",
        "Office",
        Category.OFFICE,
        "Team Manager",
        Role.MANAGER,
        80000,
        0,
        False,
    ),
    (
        "EMP007",
        "Ganesh Mahale",
        "Warehouse",
        Category.FIELD,
        "Warehouse Manager",
        Role.MANAGER,
        75000,
        0,
        False,
    ),
    (
        "EMP008",
        "Neelam (Sapphire)",
        "Office",
        Category.OFFICE,
        "Admin / Owner",
        Role.ADMIN,
        120000,
        0,
        False,
    ),
    (
        "EMP009",
        "Deepak Nimbekar",
        "Service",
        Category.SERVICE,
        "Field Service",
        Role.EMPLOYEE,
        40000,
        0,
        True,
    ),
    (
        "EMP010",
        "Manoj Gupta",
        "Warehouse",
        Category.FIELD,
        "Warehouse Staff",
        Role.EMPLOYEE,
        32000,
        0,
        False,
    ),
    (
        "EMP011",
        "Sunita Rao",
        "Service",
        Category.SERVICE,
        "Service Engineer",
        Role.EMPLOYEE,
        36000,
        0,
        False,
    ),
    (
        "EMP012",
        "Vikram Singh",
        "Warehouse",
        Category.FIELD,
        "Logistics",
        Role.EMPLOYEE,
        34000,
        0,
        False,
    ),
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
