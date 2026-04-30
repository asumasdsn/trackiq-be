from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeResponse, EmployeeCreate, EmployeeUpdate

from app.utils.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[EmployeeResponse])
def list_employees(db: Session = Depends(get_db)):
    """List all employees."""
    return db.query(Employee).all()

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee."""
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    # Audit Log
    log_audit(db, action="MEMBER_ADDED", resource="employees", details={"name": db_employee.name, "role": db_employee.position})
    
    return db_employee

@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: str, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    """Update an employee's details."""
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    update_data = employee.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_employee, key, value)
    
    db.commit()
    db.refresh(db_employee)
    
    # Audit Log
    log_audit(db, action="MEMBER_UPDATED", resource="employees", details={"name": db_employee.name})
    
    return db_employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    """Delete an employee record."""
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    name = db_employee.name
    db.delete(db_employee)
    db.commit()
    
    # Audit Log
    log_audit(db, action="MEMBER_REMOVED", resource="employees", details={"name": name})
    
    return None
