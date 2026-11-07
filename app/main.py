from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Internship Backend API",
    description="Backend application built with FastAPI",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def root():
    return {"message": "Welcome to Internship Backend API"}




class Student(BaseModel):
    name: str
    email: str
    age: int


@app.post("/students")
def create_student(student: Student):
    return {
        "message": "Student created successfully",
        "student": student
    }