from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .models import Course, ScheduleEntry, TimeSlot


DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
HOURS = [
    "09:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
    "12:00-13:00",
    "13:00-14:00",
    "14:00-15:00",
    "15:00-16:00",
    "16:00-17:00",
]


def normalize_instructor(name: str) -> str:
    value = (name or "").strip()
    if value.casefold() == "yönetici".casefold():
        return ""
    return value


def build_slots(days: Iterable[str] = DAYS, hours: Iterable[str] = HOURS) -> list[TimeSlot]:
    slots: list[TimeSlot] = []
    index = 0
    for day in days:
        for hour in hours:
            slots.append(TimeSlot(day=day, hour=hour, index=index))
            index += 1
    return slots


def split_patterns(hours: int) -> list[list[int]]:
    """Ders saatini bloklara ayırmak için tercih sırasını döndürür."""
    if hours <= 0:
        return []

    patterns: list[list[int]] = [[hours]]

    if hours == 2:
        patterns.extend([[1, 1]])
    elif hours == 3:
        patterns.extend([[2, 1], [1, 2], [1, 1, 1]])
    elif hours == 4:
        patterns.extend([[2, 2], [3, 1], [1, 3], [2, 1, 1], [1, 1, 2]])
    elif hours > 4:
        first = [2] * (hours // 2)
        if hours % 2:
            first.append(1)
        patterns.append(first)

    unique: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()
    for pattern in patterns:
        key = tuple(pattern)
        if key not in seen:
            unique.append(pattern)
            seen.add(key)
    return unique


class ScheduleBuilder:
    """Çakışma kontrolü yapan kural tabanlı ders programı oluşturucu.

    Yerleştirme yalnızca ilk boş saati seçmez. Dersleri mümkün olduğunca blok hâlinde
    tutar ve günlere dengeli dağıtmaya çalışır. Böylece tüm derslerin Pazartesi gününe
    yığılması engellenir.
    """

    def __init__(self, days: Iterable[str] = DAYS, hours: Iterable[str] = HOURS):
        self.days = list(days)
        self.hours = list(hours)
        self.slots = build_slots(self.days, self.hours)
        self._teacher_busy: set[tuple[str, int]] = set()
        self._room_busy: set[tuple[str, int]] = set()
        self._class_busy: set[tuple[str, int, int]] = set()
        self._day_load: dict[str, int] = {day: 0 for day in self.days}
        self._class_day_load: dict[tuple[str, int, str], int] = {}
        self._teacher_day_load: dict[tuple[str, str], int] = {}
        self._room_day_load: dict[tuple[str, str], int] = {}

    def build_for_department(self, courses: Iterable[Course], department: str) -> list[ScheduleEntry]:
        relevant = [
            course
            for course in courses
            if course.department == department or course.department == "Ortak"
        ]
        relevant.sort(key=lambda c: (-c.weekly_hours, c.semester, c.code))

        entries: list[ScheduleEntry] = []
        for course in relevant:
            entries.extend(self._place_course(course, department))

        entries.sort(key=lambda e: (e.slot_index, e.class_column, e.course.code))
        return entries

    def _place_course(self, course: Course, department: str) -> list[ScheduleEntry]:
        for pattern in split_patterns(course.weekly_hours):
            snapshot = self._snapshot()
            entries: list[ScheduleEntry] = []
            success = True

            for block_length in pattern:
                block = self._find_best_block(course, department, block_length)
                if block is None:
                    success = False
                    break
                entries.extend(self._reserve_block(course, department, block))

            if success:
                return entries

            self._restore(snapshot)

        raise ValueError(f"{course.code} - {course.name} dersi için uygun zaman aralığı bulunamadı.")

    def _find_best_block(self, course: Course, department: str, length: int) -> list[TimeSlot] | None:
        candidates: list[list[TimeSlot]] = []
        for day in self.days:
            day_slots = [slot for slot in self.slots if slot.day == day]
            for start in range(0, len(day_slots) - length + 1):
                block = day_slots[start:start + length]
                if self._can_use_block(course, department, block):
                    candidates.append(block)

        if not candidates:
            return None

        return min(candidates, key=lambda block: self._block_score(course, department, block))

    def _block_score(self, course: Course, department: str, block: list[TimeSlot]) -> tuple[int, int, int, int, int, int]:
        """Aday blokları puanlar; düşük puan daha uygundur.

        Öncelik sırası:
        1. Aynı sınıfın dersleri aynı güne yığılmasın.
        2. Aynı öğretim üyesi aynı güne gereksiz yığılmasın.
        3. Aynı derslik aynı güne gereksiz yığılmasın.
        4. Genel ders yükü günlere dengeli dağılsın.
        5. Eşitlikte daha erken gün ve daha erken saat seçilsin.
        """
        day = block[0].day
        teacher = normalize_instructor(course.instructor)
        classroom = course.classroom
        class_no = course.class_column
        start_in_day = self.hours.index(block[0].hour)
        day_index = self.days.index(day)

        class_day_load = self._class_day_load.get((department, class_no, day), 0)
        teacher_day_load = self._teacher_day_load.get((teacher, day), 0) if teacher else 0
        room_day_load = self._room_day_load.get((classroom, day), 0) if classroom else 0
        day_load = self._day_load.get(day, 0)

        return (
            class_day_load,
            teacher_day_load,
            room_day_load,
            day_load,
            day_index,
            start_in_day,
        )

    def _can_use_block(self, course: Course, department: str, block: list[TimeSlot]) -> bool:
        teacher = normalize_instructor(course.instructor)
        classroom = course.classroom
        class_key = course.class_column

        for slot in block:
            if teacher and (teacher, slot.index) in self._teacher_busy:
                return False
            if classroom and (classroom, slot.index) in self._room_busy:
                return False
            if (department, class_key, slot.index) in self._class_busy:
                return False
        return True

    def _reserve_block(self, course: Course, department: str, block: list[TimeSlot]) -> list[ScheduleEntry]:
        teacher = normalize_instructor(course.instructor)
        classroom = course.classroom
        class_key = course.class_column
        display_course = replace(course, instructor=teacher)

        entries: list[ScheduleEntry] = []
        day = block[0].day

        self._day_load[day] = self._day_load.get(day, 0) + len(block)
        self._class_day_load[(department, class_key, day)] = (
            self._class_day_load.get((department, class_key, day), 0) + len(block)
        )
        if teacher:
            self._teacher_day_load[(teacher, day)] = self._teacher_day_load.get((teacher, day), 0) + len(block)
        if classroom:
            self._room_day_load[(classroom, day)] = self._room_day_load.get((classroom, day), 0) + len(block)

        for slot in block:
            if teacher:
                self._teacher_busy.add((teacher, slot.index))
            if classroom:
                self._room_busy.add((classroom, slot.index))
            self._class_busy.add((department, class_key, slot.index))

            entries.append(
                ScheduleEntry(
                    course=display_course,
                    day=slot.day,
                    hour=slot.hour,
                    slot_index=slot.index,
                    class_column=class_key,
                )
            )
        return entries

    def _snapshot(self):
        return (
            set(self._teacher_busy),
            set(self._room_busy),
            set(self._class_busy),
            dict(self._day_load),
            dict(self._class_day_load),
            dict(self._teacher_day_load),
            dict(self._room_day_load),
        )

    def _restore(self, snapshot) -> None:
        (
            self._teacher_busy,
            self._room_busy,
            self._class_busy,
            self._day_load,
            self._class_day_load,
            self._teacher_day_load,
            self._room_day_load,
        ) = snapshot


def build_department_schedule(courses: Iterable[Course], department: str) -> list[ScheduleEntry]:
    return ScheduleBuilder().build_for_department(courses, department)
