"""create initial schema

Revision ID: 20260406_0001
Revises:
Create Date: 2026-04-06 22:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260406_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.create_table(
        "faculties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
    )

    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
    )

    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("faculty_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"]),
        sa.UniqueConstraint(
            "last_name",
            "first_name",
            "faculty_id",
            name="uq_students_full_name_faculty",
        ),
    )

    op.create_table(
        "student_grades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"]),
        sa.UniqueConstraint("student_id", "subject_id", name="uq_student_subject"),
        sa.CheckConstraint("grade >= 0 AND grade <= 100", name="ck_grade_range"),
    )



def downgrade() -> None:
    op.drop_table("student_grades")
    op.drop_table("students")
    op.drop_table("subjects")
    op.drop_table("faculties")
