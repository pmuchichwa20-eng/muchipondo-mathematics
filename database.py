import sqlite3

connection = sqlite3.connect("educare.db")

cursor = connection.cursor()


# ==========================================
# STUDENTS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")


# ==========================================
# RESULTS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    total_marks INTEGER NOT NULL,
    percentage REAL NOT NULL,
    date_taken TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id)
)
""")


# ==========================================
# REMOVE OLD TOPICS AND QUESTIONS
# ==========================================

cursor.execute("DROP TABLE IF EXISTS questions")

cursor.execute("DROP TABLE IF EXISTS topics")


# ==========================================
# CREATE TOPICS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
)
""")


# ==========================================
# CREATE QUESTIONS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    difficulty TEXT,
    marks INTEGER,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
)
""")


# ==========================================
# ADD MATHEMATICS TOPICS
# ==========================================

topics = [

    (
        "Number",
        "Numbers, calculations, fractions, decimals and percentages"
    ),

    (
        "Algebra",
        "Expressions, equations, inequalities and sequences"
    ),

    (
        "Geometry",
        "Angles, shapes, lines and geometric properties"
    ),

    (
        "Mensuration",
        "Perimeter, area, surface area and volume"
    ),

    (
        "Trigonometry",
        "Sine, cosine, tangent and applications"
    ),

    (
        "Statistics",
        "Data, averages, graphs and data analysis"
    ),

    (
        "Probability",
        "Chance, events and probability calculations"
    ),

    (
        "Graphs",
        "Coordinates, linear graphs and graphical interpretation"
    ),

    (
        "Financial Mathematics",
        "Money, interest, profit, loss and financial calculations"
    )
]


cursor.executemany("""
INSERT INTO topics (name, description)
VALUES (?, ?)
""", topics)


# ==========================================
# GET TOPIC IDs
# ==========================================

cursor.execute(
    "SELECT id FROM topics WHERE name = ?",
    ("Number",)
)

number_id = cursor.fetchone()[0]


cursor.execute(
    "SELECT id FROM topics WHERE name = ?",
    ("Algebra",)
)

algebra_id = cursor.fetchone()[0]


cursor.execute(
    "SELECT id FROM topics WHERE name = ?",
    ("Geometry",)
)

geometry_id = cursor.fetchone()[0]


cursor.execute(
    "SELECT id FROM topics WHERE name = ?",
    ("Mensuration",)
)

mensuration_id = cursor.fetchone()[0]


# ==========================================
# ADD QUESTIONS
# ==========================================

questions = [

    # NUMBER

    (
        number_id,
        "What is 25% of 200?",
        "25",
        "40",
        "50",
        "75",
        "C",
        "25% of 200 = (25/100) × 200 = 50.",
        "Easy",
        1
    ),

    (
        number_id,
        "Calculate 3/4 + 1/4.",
        "1/2",
        "1",
        "2",
        "3/4",
        "B",
        "3/4 + 1/4 = 4/4 = 1.",
        "Easy",
        1
    ),

    (
        number_id,
        "Convert 0.75 into a percentage.",
        "7.5%",
        "25%",
        "75%",
        "750%",
        "C",
        "0.75 × 100 = 75%.",
        "Easy",
        1
    ),

    (
        number_id,
        "What is the HCF of 12 and 18?",
        "2",
        "3",
        "6",
        "9",
        "C",
        "The highest common factor of 12 and 18 is 6.",
        "Medium",
        1
    ),


    # ALGEBRA

    (
        algebra_id,
        "Solve 3x + 5 = 20.",
        "3",
        "5",
        "7",
        "10",
        "B",
        "Subtract 5: 3x = 15. Divide by 3: x = 5.",
        "Easy",
        1
    ),

    (
        algebra_id,
        "Solve 2x - 6 = 10.",
        "2",
        "4",
        "8",
        "16",
        "C",
        "Add 6: 2x = 16. Divide by 2: x = 8.",
        "Easy",
        1
    ),

    (
        algebra_id,
        "Simplify 4x + 3x.",
        "7",
        "7x",
        "12x",
        "x",
        "B",
        "4x + 3x = 7x.",
        "Easy",
        1
    ),

    (
        algebra_id,
        "If x = 4, calculate 2x + 3.",
        "7",
        "8",
        "11",
        "14",
        "C",
        "2(4) + 3 = 11.",
        "Easy",
        1
    ),


    # GEOMETRY

    (
        geometry_id,
        "What is the sum of angles in a triangle?",
        "90°",
        "180°",
        "270°",
        "360°",
        "B",
        "The interior angles of a triangle add up to 180°.",
        "Easy",
        1
    ),

    (
        geometry_id,
        "A straight line contains an angle of how many degrees?",
        "90°",
        "180°",
        "270°",
        "360°",
        "B",
        "A straight angle is 180°.",
        "Easy",
        1
    ),

    (
        geometry_id,
        "What type of triangle has three equal sides?",
        "Scalene triangle",
        "Isosceles triangle",
        "Equilateral triangle",
        "Right-angled triangle",
        "C",
        "An equilateral triangle has three equal sides.",
        "Easy",
        1
    ),

    (
        geometry_id,
        "A right angle is equal to:",
        "45°",
        "90°",
        "180°",
        "360°",
        "B",
        "A right angle measures 90°.",
        "Easy",
        1
    ),


    # MENSURATION

    (
        mensuration_id,
        "What is the area of a rectangle with length 8 cm and width 5 cm?",
        "13 cm²",
        "26 cm²",
        "40 cm²",
        "80 cm²",
        "C",
        "Area = length × width = 8 × 5 = 40 cm².",
        "Easy",
        1
    ),

    (
        mensuration_id,
        "What is the perimeter of a square with side 6 cm?",
        "12 cm",
        "18 cm",
        "24 cm",
        "36 cm",
        "C",
        "Perimeter = 4 × 6 = 24 cm.",
        "Easy",
        1
    ),

    (
        mensuration_id,
        "What is the area of a triangle with base 10 cm and height 6 cm?",
        "30 cm²",
        "60 cm²",
        "16 cm²",
        "36 cm²",
        "A",
        "Area = 1/2 × 10 × 6 = 30 cm².",
        "Medium",
        1
    ),

    (
        mensuration_id,
        "What is the volume of a cuboid measuring 4 cm × 3 cm × 2 cm?",
        "9 cm³",
        "12 cm³",
        "24 cm³",
        "48 cm³",
        "C",
        "Volume = 4 × 3 × 2 = 24 cm³.",
        "Easy",
        1
    )
]


cursor.executemany("""
INSERT INTO questions (
    topic_id,
    question,
    option_a,
    option_b,
    option_c,
    option_d,
    correct_answer,
    explanation,
    difficulty,
    marks
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", questions)


# ==========================================
# SAVE DATABASE
# ==========================================

connection.commit()

connection.close()


print("==========================================")
print("EDUCARE DATABASE RESET SUCCESSFULLY")
print("==========================================")
print("Student accounts preserved.")
print("Quiz results preserved.")
print("Duplicate topics removed.")
print("Duplicate questions removed.")
print("9 Mathematics topics created.")
print("16 Mathematics questions created.")
print("==========================================")