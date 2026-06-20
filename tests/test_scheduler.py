import unittest

from web_ders_programi.models import Course
from web_ders_programi.scheduler import build_department_schedule, normalize_instructor, split_patterns


class SchedulerTests(unittest.TestCase):
    def test_yonetici_bos_gosterilir(self):
        self.assertEqual(normalize_instructor("Yönetici"), "")
        self.assertEqual(normalize_instructor(" yönetici "), "")
        self.assertEqual(normalize_instructor("Dr. A"), "Dr. A")

    def test_uc_saatlik_ders_blok_yerlesir(self):
        courses = [
            Course("MAT125", "Lineer Cebir", 3, "Yazılım Mühendisliği", 2, "Dr. A", "D201")
        ]
        entries = build_department_schedule(courses, "Yazılım Mühendisliği")
        self.assertEqual(len(entries), 3)
        self.assertEqual(len({entry.day for entry in entries}), 1)

    def test_ogretim_uyesi_cakismasi_engellenir(self):
        courses = [
            Course("A", "Ders A", 2, "Yazılım Mühendisliği", 2, "Dr. A", "D201"),
            Course("B", "Ders B", 2, "Yazılım Mühendisliği", 4, "Dr. A", "D301"),
        ]
        entries = build_department_schedule(courses, "Yazılım Mühendisliği")
        seen = set()
        for entry in entries:
            key = (entry.course.instructor, entry.slot_index)
            self.assertNotIn(key, seen)
            seen.add(key)

    def test_split_patterns(self):
        self.assertEqual(split_patterns(3)[0], [3])
        self.assertIn([2, 1], split_patterns(3))


if __name__ == "__main__":
    unittest.main()
