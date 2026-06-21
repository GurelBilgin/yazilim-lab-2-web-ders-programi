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

    def test_dersler_tek_gune_yigilmaz(self):
        courses = [
            Course("MAT125", "Lineer Cebir", 3, "Ortak", 2, "Dr. A", "D201"),
            Course("YZM219", "Gereksinim Analizi", 3, "Yazılım Mühendisliği", 4, "Dr. B", "D301"),
            Course("SEC301", "Alan Seçmeli", 2, "Yazılım Mühendisliği", 6, "Yönetici", "S018"),
        ]
        entries = build_department_schedule(courses, "Yazılım Mühendisliği")
        self.assertGreater(len({entry.day for entry in entries}), 1)

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


class ScheduleGridTests(unittest.TestCase):
    def test_web_grid_satirlari_tum_gun_saatleri_icerir(self):
        from web_ders_programi.app import build_grid_rows
        from web_ders_programi.scheduler import DAYS, HOURS

        entries = build_department_schedule(
            [Course("MAT125", "Lineer Cebir", 3, "Ortak", 2, "Dr. A", "D301")],
            "Bilgisayar Mühendisliği",
        )
        grid_rows = build_grid_rows(entries)

        self.assertEqual(len(grid_rows), len(DAYS) * len(HOURS))
        self.assertEqual(grid_rows[0]["day_display"], "Pazartesi")
        self.assertEqual(grid_rows[1]["day_display"], "")
        self.assertIsNotNone(grid_rows[0]["cells"][1])


if __name__ == "__main__":
    unittest.main()
