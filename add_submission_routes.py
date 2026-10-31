from pathlib import Path

p = Path("app.py")
s = p.read_text(encoding="utf-8")

if "def student_assignments():" in s:
    print("Submission routes already exist. No changes made.")
    raise SystemExit

routes = r'''

# STUDENT ASSIGNMENTS AND SUBMISSIONS

@app.route("/student/assignments")
def student_assignments():
    if "student_id" not in session:
        return redirect("/login")

    con = sqlite3.connect("educare.db")
    con.row_factory = sqlite3.Row

    assignments = con.execute("""
        SELECT a.*, t.name AS topic_name, te.name AS teacher_name,
        sub.status AS submission_status
        FROM assignments a
        LEFT JOIN topics t ON t.id = a.topic_id
        LEFT JOIN teachers te ON te.id = a.teacher_id
        LEFT JOIN assignment_submissions sub
        ON sub.assignment_id = a.id AND sub.student_id = ?
        WHERE a.is_published = 1
        ORDER BY a.created_at DESC
    """, (session["student_id"],)).fetchall()

    con.close()
    return render_template("student_assignments.html",
                           assignments=assignments)


@app.route("/student/assignments/<int:assignment_id>", methods=["GET", "POST"])
def student_assignment_detail(assignment_id):
    if "student_id" not in session:
        return redirect("/login")

    con = sqlite3.connect("educare.db")
    con.row_factory = sqlite3.Row

    assignment = con.execute("""
        SELECT a.*, t.name AS topic_name, te.name AS teacher_name
        FROM assignments a
        LEFT JOIN topics t ON t.id = a.topic_id
        LEFT JOIN teachers te ON te.id = a.teacher_id
        WHERE a.id = ? AND a.is_published = 1
    """, (assignment_id,)).fetchone()

    if not assignment:
        con.close()
        return "Assignment not found.", 404

    message = ""

    if request.method == "POST":
        answer = request.form.get("answer_text", "").strip()
        uploaded = request.files.get("work_file")
        filename = None
        filepath = None

        if uploaded and uploaded.filename:
            original = secure_filename(uploaded.filename)
            ext = os.path.splitext(original)[1].lower()

            if ext not in [".pdf", ".jpg", ".jpeg", ".png"]:
                message = "Only PDF, JPG and PNG files are allowed."
            else:
                folder = Path("static/uploads/assignment_submissions")
                folder.mkdir(parents=True, exist_ok=True)

                filename = uuid.uuid4().hex + ext
                uploaded.save(str(folder / filename))
                filepath = "uploads/assignment_submissions/" + filename

        if not message and not answer and not filepath:
            message = "Enter your answer or attach your work."

        if not message:
            con.execute("""
                INSERT INTO assignment_submissions
                (assignment_id, student_id, answer_text,
                 original_filename, file_path, status)
                VALUES (?, ?, ?, ?, ?, 'Submitted')
                ON CONFLICT(assignment_id, student_id)
                DO UPDATE SET
                    answer_text = excluded.answer_text,
                    original_filename = COALESCE(
                        excluded.original_filename,
                        assignment_submissions.original_filename),
                    file_path = COALESCE(
                        excluded.file_path,
                        assignment_submissions.file_path),
                    submitted_at = CURRENT_TIMESTAMP,
                    status = 'Submitted',
                    marks = NULL,
                    teacher_feedback = NULL,
                    reviewed_at = NULL
            """, (assignment_id, session["student_id"],
                  answer, filename, filepath))

            con.commit()
            message = "Your work has been submitted successfully."

    submission = con.execute("""
        SELECT * FROM assignment_submissions
        WHERE assignment_id = ? AND student_id = ?
    """, (assignment_id, session["student_id"])).fetchone()

    con.close()

    return render_template(
        "student_assignment_detail.html",
        assignment=assignment,
        submission=submission,
        message=message
    )


@app.route("/teacher/assignments/<int:assignment_id>/submissions")
def teacher_assignment_submissions(assignment_id):
    if "teacher_id" not in session:
        return redirect("/teacher/login")

    con = sqlite3.connect("educare.db")
    con.row_factory = sqlite3.Row

    assignment = con.execute("""
        SELECT * FROM assignments
        WHERE id = ? AND teacher_id = ?
    """, (assignment_id, session["teacher_id"])).fetchone()

    if not assignment:
        con.close()
        return "Assignment not found.", 404

    submissions = con.execute("""
        SELECT sub.*, st.name AS student_name,
        st.email AS student_email
        FROM assignment_submissions sub
        JOIN students st ON st.id = sub.student_id
        WHERE sub.assignment_id = ?
        ORDER BY sub.submitted_at DESC
    """, (assignment_id,)).fetchall()

    con.close()

    return render_template(
        "teacher_submissions.html",
        assignment=assignment,
        submissions=submissions
    )


@app.route("/teacher/submissions/<int:submission_id>/review", methods=["POST"])
def review_student_submission(submission_id):
    if "teacher_id" not in session:
        return redirect("/teacher/login")

    marks = request.form.get("marks", "").strip()
    feedback = request.form.get("teacher_feedback", "").strip()

    try:
        marks_value = float(marks) if marks else None
        if marks_value is not None and marks_value < 0:
            raise ValueError
    except ValueError:
        return "Enter valid non-negative marks.", 400

    con = sqlite3.connect("educare.db")

    row = con.execute("""
        SELECT sub.assignment_id
        FROM assignment_submissions sub
        JOIN assignments a ON a.id = sub.assignment_id
        WHERE sub.id = ? AND a.teacher_id = ?
    """, (submission_id, session["teacher_id"])).fetchone()

    if not row:
        con.close()
        return "Submission not found.", 404

    con.execute("""
        UPDATE assignment_submissions
        SET marks = ?, teacher_feedback = ?,
            status = 'Reviewed', reviewed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (marks_value, feedback, submission_id))

    con.commit()
    con.close()

    return redirect(url_for(
        "teacher_assignment_submissions",
        assignment_id=row[0]
    ))


@app.route("/teacher/submissions/<int:submission_id>/file")
def download_student_submission(submission_id):
    if "teacher_id" not in session:
        return redirect("/teacher/login")

    con = sqlite3.connect("educare.db")

    row = con.execute("""
        SELECT sub.file_path, sub.original_filename
        FROM assignment_submissions sub
        JOIN assignments a ON a.id = sub.assignment_id
        WHERE sub.id = ? AND a.teacher_id = ?
    """, (submission_id, session["teacher_id"])).fetchone()

    con.close()

    if not row or not row[0]:
        return "File not found.", 404

    return send_from_directory(
        "static",
        row[0],
        as_attachment=True,
        download_name=row[1] or "student_work"
    )

'''

marker = 'if __name__ == "__main__":'
if marker not in s:
    raise SystemExit("Could not find application startup section.")

s = s.replace(marker, routes + "\n" + marker, 1)
p.write_text(s, encoding="utf-8")

print("All student submission and teacher review routes added.")