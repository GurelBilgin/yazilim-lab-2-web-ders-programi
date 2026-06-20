from __future__ import annotations

import json
from pathlib import Path

from .models import Classroom, Course, Instructor


class MemoryRepository:
    """Web arayüzü için basit bellek içi veri deposu."""

    def __init__(
        self,
        departments: list[str],
        classrooms: list[Classroom],
        instructors: list[Instructor],
        courses: list[Course],
    ) -> None:
        self.departments = departments
        self.classrooms = classrooms
        self.instructors = instructors
        self.courses = courses

    @classmethod
    def from_json(cls, path: str | Path) -> "MemoryRepository":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            departments=list(data.get("departments", [])),
            classrooms=[Classroom(**item) for item in data.get("classrooms", [])],
            instructors=[Instructor(**item) for item in data.get("instructors", [])],
            courses=[Course(**item) for item in data.get("courses", [])],
        )

    def add_course(self, course: Course) -> None:
        self.courses = [existing for existing in self.courses if existing.code != course.code]
        self.courses.append(course)

    def delete_course(self, code: str) -> None:
        self.courses = [course for course in self.courses if course.code != code]

    def add_classroom(self, classroom: Classroom) -> None:
        self.classrooms = [room for room in self.classrooms if room.room_id != classroom.room_id]
        self.classrooms.append(classroom)

    def add_instructor(self, instructor: Instructor) -> None:
        self.instructors = [item for item in self.instructors if item.id != instructor.id]
        self.instructors.append(instructor)
