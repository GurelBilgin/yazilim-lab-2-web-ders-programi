from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Classroom:
    room_id: str
    capacity: int = 0
    status: str = "NORMAL"


@dataclass(slots=True)
class Instructor:
    id: int
    name: str
    role: str = "Öğretim Üyesi"


@dataclass(slots=True)
class Course:
    code: str
    name: str
    weekly_hours: int
    department: str
    semester: int
    instructor: str = ""
    classroom: str = ""
    course_type: str = "Zorunlu"

    @property
    def class_column(self) -> int:
        mapping = {2: 1, 4: 2, 6: 3, 8: 4}
        return mapping.get(self.semester, 1)


@dataclass(frozen=True, slots=True)
class TimeSlot:
    day: str
    hour: str
    index: int


@dataclass(slots=True)
class ScheduleEntry:
    course: Course
    day: str
    hour: str
    slot_index: int
    class_column: int

    @property
    def instructor_display(self) -> str:
        name = (self.course.instructor or "").strip()
        if name.casefold() == "yönetici".casefold():
            return ""
        return name

    @property
    def cell_text(self) -> str:
        lines = [f"{self.course.code} - {self.course.name}"]
        if self.instructor_display:
            lines.append(f"Öğretim Üyesi: {self.instructor_display}")
        if self.course.classroom:
            lines.append(f"Derslik: {self.course.classroom}")
        return "\n".join(lines)
