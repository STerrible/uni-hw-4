from pydantic import BaseModel, Field


class StudentBase(BaseModel):
    last_name: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    faculty_name: str = Field(min_length=1, max_length=50)


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    faculty_name: str | None = Field(default=None, min_length=1, max_length=50)


class StudentOut(BaseModel):
    id: int
    last_name: str
    first_name: str
    faculty: str


class GradeCreate(BaseModel):
    subject_name: str = Field(min_length=1, max_length=100)
    grade: int = Field(ge=0, le=100)


class GradeUpdate(BaseModel):
    grade: int = Field(ge=0, le=100)
