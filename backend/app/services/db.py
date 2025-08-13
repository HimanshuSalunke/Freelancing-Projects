from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import json


@dataclass
class Employee:
    emp_id: int
    full_name: str
    designation: str
    department: str
    joining_date: str
    employee_code: str
    email: str


class EmployeeDB:
    def __init__(self) -> None:
        path = Path(__file__).resolve().parent.parent / "data" / "employees.json"
        with open(path, "r", encoding="utf-8") as f:
            rows = json.load(f)
        self.id_to_emp: dict[int, Employee] = {
            int(r["emp_id"]): Employee(**r) for r in rows
        }

    def get_employee(self, emp_id: int) -> Employee | None:
        return self.id_to_emp.get(emp_id)


