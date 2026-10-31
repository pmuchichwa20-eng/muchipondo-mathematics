from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import uuid
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "educare.db"))

app.secret_key = os.environ.get("SECRET_KEY", "local-development-only-change-before-deployment")


# ==========================================
# GET TOPICS
# ==========================================

def get_topics():

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM topics")

    topics = cursor.fetchall()

    connection.close()

    return topics


# ==========================================
# GET QUESTIONS
# ==========================================

def get_questions(topic_id=None):

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    if topic_id:

        cursor.execute("""
            SELECT questions.*, topics.name AS topic_name
            FROM questions
            JOIN topics
            ON questions.topic_id = topics.id
            WHERE questions.topic_id = ?
        """, (topic_id,))

    else:

        cursor.execute("""
            SELECT questions.*, topics.name AS topic_name
            FROM questions
            JOIN topics
            ON questions.topic_id = topics.id
        """)

    questions = cursor.fetchall()

    connection.close()

    return questions


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    topics = get_topics()

    return render_template(
        "index.html",
        topics=topics
    )


# ==========================================
# TOPICS PAGE
# ==========================================

@app.route("/topics")
def topics():

    if "student_id" not in session:

        return redirect("/login")

    topics = get_topics()

    return render_template(
        "topics.html",
        topics=topics
    )


# ==========================================
# REGISTER
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    message = None

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        connection = sqlite3.connect(DATABASE_PATH)

        cursor = connection.cursor()

        try:

            cursor.execute("""
                INSERT INTO students (name, email, password)
                VALUES (?, ?, ?)
            """, (name, email, hashed_password))

            connection.commit()
            connection.close()

            return redirect("/login")

        except sqlite3.IntegrityError:

            connection.close()

            message = "This email is already registered."

    return render_template(
        "register.html",
        message=message
    )


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    message = None

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE email = ?",
            (email,)
        )

        student = cursor.fetchone()

        connection.close()

        if student and check_password_hash(
            student["password"],
            password
        ):

            session["student_id"] = student["id"]
            session["student_name"] = student["name"]

            return redirect("/dashboard")

        else:

            message = "Incorrect email or password."

    return render_template(
        "login.html",
        message=message
    )


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():
    if "student_id" not in session:
        return redirect("/login")

    con = sqlite3.connect(DATABASE_PATH)
    reviewed_count = con.execute(
        "SELECT COUNT(*) FROM assignment_submissions WHERE student_id = ? AND status = ?",
        (session["student_id"], "Reviewed")
    ).fetchone()[0]
    con.close()

    return render_template(
        "dashboard.html",
        reviewed_count=reviewed_count
    )


# ==========================================
# STUDENT TEACHER FEEDBACK
# ==========================================

@app.route("/student/feedback")
def student_feedback():
    if "student_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("""
        SELECT tf.message, tf.created_at, t.name AS teacher_name
        FROM teacher_feedback AS tf
        LEFT JOIN teachers AS t ON t.id = tf.teacher_id
        WHERE tf.student_id = ?
        ORDER BY tf.created_at DESC
    """, (session["student_id"],))
    feedback_list = cursor.fetchall()
    connection.close()
    return render_template("student_feedback.html", feedback_list=feedback_list)


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ==========================================
# RESULTS
# ==========================================

@app.route("/results")
def results():

    if "student_id" not in session:

        return redirect("/login")

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM results
        WHERE student_id = ?
        ORDER BY date_taken DESC
    """, (session["student_id"],))

    results = cursor.fetchall()

    connection.close()

    return render_template(
        "results.html",
        results=results
    )

# ==========================================
# STUDENT PROGRESS
# ==========================================

@app.route("/progress")
def progress():

    if "student_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Get overall progress statistics
    cursor.execute("""
        SELECT
            COUNT(*) AS total_attempts,
            COALESCE(AVG(percentage), 0) AS average_percentage,
            COALESCE(MAX(percentage), 0) AS best_percentage
        FROM results
        WHERE student_id = ?
    """, (session["student_id"],))

    summary = cursor.fetchone()

    # Get the five most recent quiz results
    cursor.execute("""
        SELECT score, total_marks, percentage, date_taken
        FROM results
        WHERE student_id = ?
        ORDER BY date_taken DESC
        LIMIT 5
    """, (session["student_id"],))

    recent_results = cursor.fetchall()

    connection.close()

    return render_template(
        "progress.html",
        summary=summary,
        recent_results=recent_results
    )


# ==========================================
# QUESTIONS / QUIZ
# ==========================================

@app.route("/questions", methods=["GET", "POST"])
def questions():

    if "student_id" not in session:

        return redirect("/login")

    topic_id = request.args.get("topic_id")

    questions = get_questions(topic_id)

    score = None

    total_marks = sum(
        question["marks"]
        for question in questions
    )

    percentage = None

    results = []


    if request.method == "POST":

        score = 0

        for question in questions:

            answer = request.form.get(
                f"question_{question['id']}"
            )

            correct = (
                answer == question["correct_answer"]
            )

            if correct:

                score += question["marks"]

            results.append({

                "question": question["question"],

                "topic": question["topic_name"],

                "your_answer": (
                    answer
                    if answer
                    else "Not answered"
                ),

                "correct_answer": (
                    question["correct_answer"]
                ),

                "explanation": (
                    question["explanation"]
                ),

                "correct": correct

            })


        if total_marks > 0:

            percentage = (
                score / total_marks
            ) * 100

        else:

            percentage = 0


        connection = sqlite3.connect(DATABASE_PATH)

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO results (
                student_id,
                score,
                total_marks,
                percentage
            )
            VALUES (?, ?, ?, ?)
        """, (

            session["student_id"],

            score,

            total_marks,

            percentage

        ))

        connection.commit()

        connection.close()


    return render_template(

        "questions.html",

        questions=questions,

        score=score,

        total_marks=total_marks,

        percentage=percentage,

        results=results

    )


# ==========================================
# TEACHER REGISTRATION
# ==========================================

@app.route("/teacher/register", methods=["GET", "POST"])
def teacher_register():

    message = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            message = "Please complete all fields."
        elif len(password) < 8:
            message = "Your password must contain at least 8 characters."
        else:
            connection = sqlite3.connect(DATABASE_PATH)
            cursor = connection.cursor()
            try:
                hashed_password = generate_password_hash(password)
                cursor.execute("INSERT INTO teachers (name, email, password, is_approved) VALUES (?, ?, ?, 1)", (name, email, hashed_password))
                connection.commit()
                message = "Registration successful. You can now log in."
            except sqlite3.IntegrityError:
                message = "This email address is already registered."
            finally:
                connection.close()

    return render_template("teacher_register.html", message=message)


@app.route("/teacher/login", methods=["GET", "POST"])
def teacher_login():

    message = None

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM teachers WHERE email = ?",
            (email,)
        )

        teacher = cursor.fetchone()
        connection.close()

        if teacher and check_password_hash(
            teacher["password"], password
        ):

            session.pop("student_id", None)
            session.pop("student_name", None)

            session["teacher_id"] = teacher["id"]
            session["teacher_name"] = teacher["name"]

            return redirect("/teacher/dashboard")

        else:
            message = "Incorrect email or password."

    return render_template(
        "teacher_login.html",
        message=message
    )
@app.route("/teacher/dashboard")
def teacher_dashboard():

    if "teacher_id" not in session:
        return redirect("/teacher/login")

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, is_approved FROM teachers WHERE id = ?",
        (session["teacher_id"],)
    )

    teacher = cursor.fetchone()
    connection.close()

    if teacher is None:
        session.pop("teacher_id", None)
        session.pop("teacher_name", None)
        return redirect("/teacher/login")

    session["teacher_name"] = teacher["name"]

    return render_template("teacher_dashboard.html")



# ==========================================
# TEACHER FEEDBACK FOR STUDENTS
# ==========================================

@app.route("/teacher/feedback", methods=["GET", "POST"])
def teacher_feedback():

    if "teacher_id" not in session:
        return redirect("/teacher/login")

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, is_approved FROM teachers WHERE id = ?",
        (session["teacher_id"],)
    )
    teacher = cursor.fetchone()

    if teacher is None:
        connection.close()
        session.pop("teacher_id", None)
        session.pop("teacher_name", None)
        return redirect("/teacher/login")

    session["teacher_name"] = teacher["name"]
    message = ""

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        feedback_text = request.form.get("message", "").strip()

        try:
            student_id = int(student_id)
        except (ValueError, TypeError):
            student_id = 0

        cursor.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,)
        )
        student = cursor.fetchone()

        if not student:
            message = "Please select a valid student."
        elif not feedback_text:
            message = "Please enter your feedback."
        elif len(feedback_text) > 2000:
            message = "Feedback must not exceed 2000 characters."
        else:
            cursor.execute(
                """
                INSERT INTO teacher_feedback
                    (teacher_id, student_id, message)
                VALUES (?, ?, ?)
                """,
                (session["teacher_id"], student_id, feedback_text)
            )
            connection.commit()
            connection.close()
            return redirect(
                "/teacher/feedback?message=Feedback+submitted+successfully"
            )

    cursor.execute(
        "SELECT id, name FROM students ORDER BY name ASC"
    )
    students = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            tf.id,
            tf.message,
            tf.created_at,
            s.name AS student_name
        FROM teacher_feedback AS tf
        JOIN students AS s ON s.id = tf.student_id
        WHERE tf.teacher_id = ?
        ORDER BY tf.created_at DESC, tf.id DESC
        """,
        (session["teacher_id"],)
    )
    feedback_list = cursor.fetchall()

    connection.close()

    return render_template(
        "teacher_feedback.html",
        students=students,
        feedback_list=feedback_list,
        message=message,
        success_message=request.args.get("message", "")
    )

# ==========================================
# TEACHER FEEDBACK FOR STUDENTS
# ==========================================


# ==========================================
# STUDENT PERFORMANCE FOR TEACHERS
# ==========================================

@app.route("/teacher/performance")
def teacher_performance():

    if "teacher_id" not in session:
        return redirect("/teacher/login")

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, is_approved FROM teachers WHERE id = ?",
        (session["teacher_id"],)
    )

    teacher = cursor.fetchone()

    if teacher is None:
        connection.close()
        session.pop("teacher_id", None)
        session.pop("teacher_name", None)
        return redirect("/teacher/login")

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM results")
    total_attempts = cursor.fetchone()[0]

    cursor.execute(
        "SELECT AVG(percentage) FROM results"
    )
    average = cursor.fetchone()[0]
    average_percentage = average if average is not None else 0

    cursor.execute(
        """
        SELECT
            s.id AS student_id,
            s.name,
            s.email,
            r.id AS result_id,
            r.score,
            r.total_marks,
            r.percentage,
            r.date_taken
        FROM students AS s
        LEFT JOIN results AS r
            ON s.id = r.student_id
        ORDER BY s.name ASC, r.date_taken DESC
        """
    )

    results = cursor.fetchall()
    connection.close()

    session["teacher_name"] = teacher["name"]

    return render_template(
        "student_performance.html",
        results=results,
        total_students=total_students,
        total_attempts=total_attempts,
        average_percentage=average_percentage
    )



# ==========================================
# RUN APPLICATION
# ==========================================

# ==========================================
# TEACHER REVISION ASSIGNMENTS
# ==========================================

@app.route("/teacher/assignments", methods=["GET", "POST"])
def teacher_assignments():

    if "teacher_id" not in session:
        return redirect("/teacher/login")

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, is_approved FROM teachers WHERE id = ?",
        (session["teacher_id"],)
    )
    teacher = cursor.fetchone()

    if teacher is None:
        connection.close()
        session.pop("teacher_id", None)
        session.pop("teacher_name", None)
        return redirect("/teacher/login")

    message = None
    error = False

    cursor.execute("SELECT id, name FROM topics ORDER BY name ASC")
    topics = cursor.fetchall()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        topic_id = request.form.get("topic_id", "").strip()
        instructions = request.form.get("instructions", "").strip()
        due_date = request.form.get("due_date", "").strip() or None

        if not title or not instructions:
            message = "Please enter an assignment title and instructions."
            error = True

        else:
            if topic_id:
                cursor.execute(
                    "SELECT id FROM topics WHERE id = ?",
                    (topic_id,)
                )
                if cursor.fetchone() is None:
                    message = "Please select a valid Mathematics topic."
                    error = True

            if not error and due_date:
                from datetime import date

                try:
                    deadline = date.fromisoformat(due_date)
                    if deadline < date.today():
                        message = "The deadline cannot be in the past."
                        error = True
                except ValueError:
                    message = "Please enter a valid deadline."
                    error = True

            if not error:
                cursor.execute(
                    """
                    INSERT INTO assignments
                    (teacher_id, title, topic_id, instructions, due_date)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        teacher["id"],
                        title,
                        int(topic_id) if topic_id else None,
                        instructions,
                        due_date
                    )
                )
                connection.commit()
                message = "Revision assignment saved successfully."

    connection.close()
    session["teacher_name"] = teacher["name"]

    return render_template(
        "teacher_assignments.html",
        topics=topics,
        message=message,
        error=error
    )

# ==========================================
# VIEW TEACHER REVISION ASSIGNMENTS
# ==========================================

@app.route("/teacher/assignments/list")
def teacher_assignment_list():

    if "teacher_id" not in session:
        return redirect("/teacher/login")

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, is_approved FROM teachers WHERE id = ?",
        (session["teacher_id"],)
    )
    teacher = cursor.fetchone()

    if teacher is None:
        connection.close()
        session.pop("teacher_id", None)
        session.pop("teacher_name", None)
        return redirect("/teacher/login")

    cursor.execute(
        """
        SELECT
            a.id,
            a.title,
            a.instructions,
            a.due_date,
            a.is_published,
            t.name AS topic_name
        FROM assignments AS a
        LEFT JOIN topics AS t ON a.topic_id = t.id
        WHERE a.teacher_id = ?
        ORDER BY a.created_at DESC, a.id DESC
        """,
        (teacher["id"],)
    )

    assignments = cursor.fetchall()
    connection.close()

    session["teacher_name"] = teacher["name"]

    return render_template(
        "teacher_assignment_list.html",
        assignments=assignments,
        message=request.args.get("message")
    )


# ==========================================
# PUBLISH A TEACHER'S OWN ASSIGNMENT
# ==========================================

@app.route(
    "/teacher/assignments/<int:assignment_id>/publish",
    methods=["POST"]
)
def publish_teacher_assignment():

    if "teacher_id" not in session:
        return redirect("/teacher/login")

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, is_approved FROM teachers WHERE id = ?",
        (session["teacher_id"],)
    )
    teacher = cursor.fetchone()

    if teacher is None:
        connection.close()
        session.pop("teacher_id", None)
        session.pop("teacher_name", None)
        return redirect("/teacher/login")

    cursor.execute(
        """
        UPDATE assignments
        SET is_published = 1
        WHERE id = ? AND teacher_id = ?
        """,
        (assignment_id, teacher["id"])
    )

    updated = cursor.rowcount
    connection.commit()
    connection.close()

    if updated:
        return redirect(
            "/teacher/assignments/list?message=Assignment+published+successfully"
        )

    return redirect(
        "/teacher/assignments/list?message=Assignment+not+found"
    )


# ==========================================
# ADMINISTRATOR LOGIN AND TEACHER APPROVAL
# ==========================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    message = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM admins WHERE email = ?",
            (email,)
        )
        admin = cursor.fetchone()
        connection.close()

        if admin and check_password_hash(
            admin["password_hash"], password
        ):
            session.pop("student_id", None)
            session.pop("student_name", None)
            session.pop("teacher_id", None)
            session.pop("teacher_name", None)

            session["admin_id"] = admin["id"]
            session["admin_email"] = admin["email"]

            return redirect("/admin/dashboard")

        message = "Invalid administrator email or password."

    return render_template(
        "admin_login.html",
        message=message
    )


@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect("/admin/login")

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, email, created_at
        FROM teachers
        WHERE is_approved = 0
        ORDER BY created_at DESC
    """)

    pending_teachers = cursor.fetchall()

    cursor.execute("""
        SELECT id, name, email, created_at
        FROM teachers
        WHERE is_approved = 1
        ORDER BY created_at DESC
    """)

    approved_teachers = cursor.fetchall()
    connection.close()

    return render_template(
        "admin_dashboard.html",
        pending_teachers=pending_teachers,
        approved_teachers=approved_teachers
    )


@app.route(
    "/admin/approve-teacher/<int:teacher_id>",
    methods=["POST"]
)
def admin_approve_teacher(teacher_id):
    if "admin_id" not in session:
        return redirect("/admin/login")

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE teachers
            SET is_approved = 1
            WHERE id = ? AND is_approved = 0
        """, (teacher_id,))

        connection.commit()

        if cursor.rowcount == 1:
            message = "Teacher approved successfully."
        else:
            message = "Teacher not found or already approved."

    finally:
        connection.close()

    return redirect(
        "/admin/dashboard?message=" + message.replace(" ", "+")
    )


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    if "admin_id" not in session:
        return redirect("/admin/login")

    session.pop("admin_id", None)
    session.pop("admin_email", None)

    return redirect("/admin/login")



# STUDENT ASSIGNMENTS AND SUBMISSIONS

@app.route("/student/assignments")
def student_assignments():
    if "student_id" not in session:
        return redirect("/login")

    con = sqlite3.connect(DATABASE_PATH)
    con.row_factory = sqlite3.Row

    assignments = con.execute("""
        SELECT a.*, t.name AS topic_name, te.name AS teacher_name,
        sub.status AS submission_status, sub.marks AS submission_marks, sub.teacher_feedback AS submission_feedback
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

    con = sqlite3.connect(DATABASE_PATH)
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

    con = sqlite3.connect(DATABASE_PATH)
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

    con = sqlite3.connect(DATABASE_PATH)

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

    con = sqlite3.connect(DATABASE_PATH)

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
