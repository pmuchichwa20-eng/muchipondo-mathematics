from pathlib import Path

# Add Assignments link to student dashboard
p = Path("templates/dashboard.html")
s = p.read_text(encoding="utf-8")

if "/student/assignments" not in s:
    link = """
    <div style="background:white;padding:20px;margin:15px 0;border-radius:9px;">
        <h3>My Assignments</h3>
        <p>View assignments from your teachers and submit your Mathematics work.</p>
        <a href="/student/assignments">Open My Assignments</a>
    </div>
    """
    if "</main>" in s:
        s = s.replace("</main>", link + "\n</main>", 1)
    else:
        s = s.replace("</body>", link + "\n</body>", 1)
    p.write_text(s, encoding="utf-8")
    print("Student dashboard updated.")
else:
    print("Student dashboard link already exists.")

# Add View Submissions link to teacher assignment list
p = Path("templates/teacher_assignment_list.html")
s = p.read_text(encoding="utf-8")

anchor = "                        {% if not assignment['is_published'] %}"
link = """                        {% if assignment['is_published'] %}
                            <p><a href="/teacher/assignments/{{ assignment['id'] }}/submissions">View Student Submissions</a></p>
                        {% endif %}

"""

if "View Student Submissions" not in s:
    if anchor not in s:
        raise SystemExit("Could not find the teacher assignment insertion point.")
    s = s.replace(anchor, link + anchor, 1)
    p.write_text(s, encoding="utf-8")
    print("Teacher assignment page updated.")
else:
    print("Teacher submissions link already exists.")

print("Dashboard connections completed.")