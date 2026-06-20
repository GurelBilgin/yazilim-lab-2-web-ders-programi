from __future__ import annotations

from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for

from .excel_exporter import export_schedule
from .models import Classroom, Course, Instructor
from .repository import MemoryRepository
from .scheduler import build_department_schedule


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = PACKAGE_ROOT / "data" / "ornek_veriler.json"
DOWNLOAD_DIR = PACKAGE_ROOT / "downloads"


def create_app(repository: MemoryRepository | None = None) -> Flask:
    app = Flask(__name__)
    app.secret_key = "dev-secret-key"

    repo = repository or MemoryRepository.from_json(DEFAULT_DATA)
    DOWNLOAD_DIR.mkdir(exist_ok=True)

    @app.route("/")
    def index():
        return render_template("index.html", courses=repo.courses, departments=repo.departments)

    @app.route("/dersler")
    def courses():
        return render_template("courses.html", courses=repo.courses)

    @app.route("/ders-ekle", methods=["GET", "POST"])
    def add_course():
        if request.method == "POST":
            try:
                course = Course(
                    code=request.form["code"].strip(),
                    name=request.form["name"].strip(),
                    weekly_hours=int(request.form["weekly_hours"]),
                    department=request.form["department"].strip(),
                    semester=int(request.form["semester"]),
                    instructor=request.form.get("instructor", "").strip(),
                    classroom=request.form.get("classroom", "").strip(),
                    course_type=request.form.get("course_type", "Zorunlu").strip(),
                )
                repo.add_course(course)
                flash(f"{course.code} kodlu ders kaydedildi.", "success")
                return redirect(url_for("courses"))
            except Exception as exc:
                flash(f"Ders eklenemedi: {exc}", "danger")

        return render_template(
            "course_form.html",
            departments=repo.departments + ["Ortak"],
            instructors=repo.instructors,
            classrooms=repo.classrooms,
        )

    @app.route("/ders-sil/<code>", methods=["POST"])
    def delete_course(code: str):
        repo.delete_course(code)
        flash(f"{code} kodlu ders silindi.", "success")
        return redirect(url_for("courses"))

    @app.route("/derslikler", methods=["GET", "POST"])
    def rooms():
        if request.method == "POST":
            repo.add_classroom(
                Classroom(
                    room_id=request.form["room_id"].strip(),
                    capacity=int(request.form.get("capacity", 0) or 0),
                    status=request.form.get("status", "NORMAL").strip(),
                )
            )
            flash("Derslik kaydedildi.", "success")
            return redirect(url_for("rooms"))
        return render_template("rooms.html", classrooms=repo.classrooms)

    @app.route("/ogretim-uyeleri", methods=["GET", "POST"])
    def instructors():
        if request.method == "POST":
            next_id = max([item.id for item in repo.instructors] + [0]) + 1
            repo.add_instructor(
                Instructor(
                    id=next_id,
                    name=request.form["name"].strip(),
                    role=request.form.get("role", "Öğretim Üyesi").strip(),
                )
            )
            flash("Öğretim üyesi kaydedildi.", "success")
            return redirect(url_for("instructors"))
        return render_template("instructors.html", instructors=repo.instructors)

    @app.route("/program/<department>")
    def schedule(department: str):
        try:
            entries = build_department_schedule(repo.courses, department)
            file_name = "output_yazilim.xlsx" if department.startswith("Yazılım") else "output_bilgisayar.xlsx"
            export_schedule(entries, department, DOWNLOAD_DIR / file_name)
        except Exception as exc:
            flash(f"Program oluşturulamadı: {exc}", "danger")
            entries = []
            file_name = ""

        return render_template("schedule.html", department=department, entries=entries, file_name=file_name)

    @app.route("/download/<filename>")
    def download(filename: str):
        return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

    return app


def main() -> None:
    app = create_app()
    app.run(debug=True)


if __name__ == "__main__":
    main()
