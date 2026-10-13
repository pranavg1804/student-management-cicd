from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify
)

from app import db
from app.models import Student

bp = Blueprint("main", __name__)


def validate(data):
    """Clean and validate student input. Returns (clean_data, errors)."""
    errors = []
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    course = (data.get("course") or "").strip()
    try:
        year = int(data.get("year"))
    except (TypeError, ValueError):
        year = None

    if not name:
        errors.append("Name is required.")
    if "@" not in email or "." not in email.split("@")[-1]:
        errors.append("A valid email is required.")
    if not course:
        errors.append("Course is required.")
    if year is None or not 1 <= year <= 6:
        errors.append("Year must be a number between 1 and 6.")

    return {"name": name, "email": email, "course": course, "year": year}, errors


# ---------- Health check ----------
@bp.route("/health")
def health():
    return jsonify(status="healthy"), 200


# ---------- Web UI ----------
@bp.route("/")
def index():
    q = request.args.get("q", "").strip()
    query = Student.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Student.name.ilike(like),
                Student.email.ilike(like),
                Student.course.ilike(like),
            )
        )
    students = query.order_by(Student.id.desc()).all()
    return render_template("index.html", students=students, q=q)


@bp.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        data, errors = validate(request.form)
        if Student.query.filter_by(email=data["email"]).first():
            errors.append("A student with this email already exists.")
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("form.html", student=data, title="Add Student"), 400
        db.session.add(Student(**data))
        db.session.commit()
        flash("Student added successfully.", "success")
        return redirect(url_for("main.index"))
    return render_template("form.html", student={}, title="Add Student")


@bp.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    student = db.get_or_404(Student, student_id)
    if request.method == "POST":
        data, errors = validate(request.form)
        duplicate = Student.query.filter(
            Student.email == data["email"], Student.id != student_id
        ).first()
        if duplicate:
            errors.append("Another student already uses this email.")
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("form.html", student=data, title="Edit Student"), 400
        for key, value in data.items():
            setattr(student, key, value)
        db.session.commit()
        flash("Student updated successfully.", "success")
        return redirect(url_for("main.index"))
    return render_template("form.html", student=student, title="Edit Student")


@bp.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    student = db.get_or_404(Student, student_id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted.", "success")
    return redirect(url_for("main.index"))


# ---------- REST API ----------
@bp.route("/api/students", methods=["GET"])
def api_list():
    students = Student.query.order_by(Student.id).all()
    return jsonify([s.to_dict() for s in students])


@bp.route("/api/students", methods=["POST"])
def api_create():
    data, errors = validate(request.get_json(silent=True) or {})
    if Student.query.filter_by(email=data["email"]).first():
        errors.append("A student with this email already exists.")
    if errors:
        return jsonify(errors=errors), 400
    student = Student(**data)
    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201


@bp.route("/api/students/<int:student_id>", methods=["GET"])
def api_get(student_id):
    student = db.get_or_404(Student, student_id)
    return jsonify(student.to_dict())


@bp.route("/api/students/<int:student_id>", methods=["PUT"])
def api_update(student_id):
    student = db.get_or_404(Student, student_id)
    data, errors = validate(request.get_json(silent=True) or {})
    duplicate = Student.query.filter(
        Student.email == data["email"], Student.id != student_id
    ).first()
    if duplicate:
        errors.append("Another student already uses this email.")
    if errors:
        return jsonify(errors=errors), 400
    for key, value in data.items():
        setattr(student, key, value)
    db.session.commit()
    return jsonify(student.to_dict())


@bp.route("/api/students/<int:student_id>", methods=["DELETE"])
def api_delete(student_id):
    student = db.get_or_404(Student, student_id)
    db.session.delete(student)
    db.session.commit()
    return jsonify(message="Student deleted"), 200