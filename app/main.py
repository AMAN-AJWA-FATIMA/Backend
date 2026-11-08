from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr

app = FastAPI(
    title="Backend API",
    description="A practical REST API built with FastAPI",
    version="1.0.0",
)


# Request model
class Student(BaseModel):
    name: str
    email: EmailStr
    age: int
    department: str


# Response model
class StudentResponse(Student):
    student_id: int


# Sample in-memory data
students = {
    1: {
        "student_id": 1,
        "name": "Aman",
        "email": "aman@example.com",
        "age": 20,
        "department": "CS",
    },
    2: {
        "student_id": 2,
        "name": "Bisma",
        "email": "bisma@example.com",
        "age": 21,
        "department": "AI",
    },
}


# Dependency
def get_pagination(
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return {"limit": limit}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def root():
    return {"message": "Welcome to Backend API"}


# POST: Request body and response model
@app.post("/students", response_model=StudentResponse)
def create_student(student: Student):
    student_id = max(students.keys(), default=0) + 1

    new_student = {
        "student_id": student_id,
        **student.model_dump(),
    }

    students[student_id] = new_student

    return new_student


# GET: Path parameter
@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    if student_id not in students:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    return students[student_id]


# GET: Query parameter and dependency
@app.get("/students", response_model=list[StudentResponse])
def list_students(
    department: str | None = None,
    pagination: dict = Depends(get_pagination),
):
    results = list(students.values())

    if department:
        results = [
            student
            for student in results
            if student["department"].lower() == department.lower()
        ]

    return results[: pagination["limit"]]
