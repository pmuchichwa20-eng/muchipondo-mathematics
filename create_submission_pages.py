from pathlib import Path

pages = {
"student_assignments.html": r'''<!DOCTYPE html>
<html><head><title>My Assignments | MuchiPondo</title>
<style>
body{font-family:Arial;background:#f4f7fb;margin:0;color:#243247}
header{background:#1f4e79;color:white;padding:20px;text-align:center}
main{max-width:900px;margin:30px auto;padding:20px}
.card{background:white;padding:20px;margin:15px 0;border-radius:9px}
a{color:#1f4e79} .button{display:inline-block;background:#1f4e79;color:white;padding:10px 15px;text-decoration:none;border-radius:5px}
</style></head><body>
<header><h1>MuchiPondo Mathematics</h1><h2>My Assignments</h2></header>
<main><p><a href="/dashboard">Student Dashboard</a> | <a href="/logout">Log Out</a></p>
{% for a in assignments %}
<div class="card"><h3>{{ a['title'] }}</h3>
<p>Topic: {{ a['topic_name'] or 'General Mathematics' }}</p>
<p>Teacher: {{ a['teacher_name'] or 'Teacher' }}</p>
<p>Deadline: {{ a['due_date'] or 'No deadline' }}</p>
<p>Status: {{ a['submission_status'] or 'Not submitted' }}</p>
<a class="button" href="/student/assignments/{{ a['id'] }}">Open Assignment</a>
</div>
{% else %}<p>No published assignments are available.</p>{% endfor %}
</main></body></html>''',

"student_assignment_detail.html": r'''<!DOCTYPE html>
<html><head><title>Submit Work | MuchiPondo</title>
<style>
body{font-family:Arial;background:#f4f7fb;margin:0;color:#243247}
header{background:#1f4e79;color:white;padding:20px;text-align:center}
main{max-width:800px;margin:30px auto;padding:20px}
.card{background:white;padding:25px;border-radius:9px}
textarea{width:100%;min-height:160px;padding:10px;box-sizing:border-box}
button{background:#1f4e79;color:white;padding:12px 20px;border:0;border-radius:5px}
.message{background:#e8f4ea;padding:12px;margin:15px 0}
</style></head><body>
<header><h1>MuchiPondo Mathematics</h1><h2>Assignment Submission</h2></header>
<main><p><a href="/student/assignments">Back to Assignments</a></p>
<div class="card"><h2>{{ assignment['title'] }}</h2>
<p>Topic: {{ assignment['topic_name'] or 'General Mathematics' }}</p>
<p>Teacher: {{ assignment['teacher_name'] or 'Teacher' }}</p>
<p>Instructions: {{ assignment['instructions'] }}</p>
<p>Deadline: {{ assignment['due_date'] or 'No deadline' }}</p>
{% if message %}<div class="message">{{ message }}</div>{% endif %}
{% if submission %}
<p><strong>Current status:</strong> {{ submission['status'] }}</p>
{% if submission['marks'] is not none %}<p>Marks: {{ submission['marks'] }}</p>{% endif %}
{% if submission['teacher_feedback'] %}<p>Teacher's comments: {{ submission['teacher_feedback'] }}</p>{% endif %}
{% endif %}
<form method="POST" enctype="multipart/form-data">
<label><strong>Type your answers:</strong></label><br><br>
<textarea name="answer_text" placeholder="Write your Mathematics answers here...">{{ submission['answer_text'] or '' if submission else '' }}</textarea><br><br>
<label>Or upload handwritten work (PDF, JPG or PNG):</label><br><br>
<input type="file" name="work_file" accept=".pdf,.jpg,.jpeg,.png"><br><br>
<button type="submit">Submit My Work</button>
</form></div></main></body></html>''',

"teacher_submissions.html": r'''<!DOCTYPE html>
<html><head><title>Student Submissions | MuchiPondo</title>
<style>
body{font-family:Arial;background:#f4f7fb;margin:0;color:#243247}
header{background:#1f4e79;color:white;padding:20px;text-align:center}
main{max-width:1000px;margin:30px auto;padding:20px}
.card{background:white;padding:20px;margin:15px 0;border-radius:9px}
textarea,input{width:100%;padding:10px;box-sizing:border-box;margin:6px 0}
button{background:#1f4e79;color:white;padding:10px 18px;border:0;border-radius:5px}
a{color:#1f4e79}
</style></head><body>
<header><h1>MuchiPondo Mathematics</h1><h2>Student Submissions</h2></header>
<main><p><a href="/teacher/assignments/list">Back to Assignments</a></p>
<h2>{{ assignment['title'] }}</h2>
{% for sub in submissions %}
<div class="card"><h3>{{ sub['student_name'] }}</h3>
<p>Email: {{ sub['student_email'] }}</p>
<p>Submitted: {{ sub['submitted_at'] }}</p>
<p>Status: {{ sub['status'] }}</p>
<p><strong>Student's answers:</strong><br>{{ sub['answer_text'] or 'No typed answer.' }}</p>
{% if sub['file_path'] %}
<p><a href="/teacher/submissions/{{ sub['id'] }}/file">Download student's attached work</a></p>
{% endif %}
<p>Previous marks: {{ sub['marks'] if sub['marks'] is not none else 'Not marked' }}</p>
<p>Previous comments: {{ sub['teacher_feedback'] or 'None' }}</p>
<form method="POST" action="/teacher/submissions/{{ sub['id'] }}/review">
<label>Marks:</label><input type="number" name="marks" min="0" step="0.5" value="{{ sub['marks'] if sub['marks'] is not none else '' }}">
<label>Comments for student:</label><textarea name="teacher_feedback" rows="4">{{ sub['teacher_feedback'] or '' }}</textarea>
<button type="submit">Save Review</button>
</form></div>
{% else %}<p>No students have submitted work yet.</p>{% endfor %}
</main></body></html>'''
}

folder = Path("templates")
folder.mkdir(exist_ok=True)

for name, content in pages.items():
    (folder / name).write_text(content, encoding="utf-8")
    print("Created:", name)

print("All three submission pages created.")