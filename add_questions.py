
import sqlite3

DATABASE = "educare.db"

new_questions = [
    # NUMBER (topic_id 1)
    (1, "What is 15% of 200?", "20", "25", "30", "35", "C",
     "15% of 200 = 0.15 × 200 = 30.", "Easy", 1),
    (1, "Evaluate (-3)² + 4.", "5", "9", "13", "-5", "C",
     "(-3)² = 9, and 9 + 4 = 13.", "Easy", 1),

    # ALGEBRA (topic_id 2)
    (2, "Simplify 3x + 5x - 2x.", "6x", "10x", "8x", "6x²", "A",
     "Combine like terms: (3 + 5 - 2)x = 6x.", "Easy", 1),
    (2, "Solve 2x + 7 = 19.", "5", "6", "12", "13", "B",
     "Subtract 7 to get 2x = 12, then divide by 2. Thus x = 6.", "Easy", 1),

    # GEOMETRY (topic_id 3)
    (3, "Two angles in a triangle are 50° and 60°. Find the third angle.", "60°", "70°", "80°", "90°", "B",
     "Angles in a triangle sum to 180°. The third angle is 180° - 50° - 60° = 70°.", "Easy", 1),
    (3, "An angle on a straight line is 125°. Find the adjacent angle.", "45°", "55°", "65°", "125°", "B",
     "Angles on a straight line sum to 180°. So 180° - 125° = 55°.", "Easy", 1),

    # MENSURATION (topic_id 4)
    (4, "Find the area of a rectangle of length 8 cm and width 5 cm.", "13 cm²", "26 cm²", "40 cm²", "80 cm²", "C",
     "Area = length × width = 8 × 5 = 40 cm².", "Easy", 1),
    (4, "Find the perimeter of a square with side 7 cm.", "14 cm", "21 cm", "28 cm", "49 cm", "C",
     "Perimeter of a square = 4 × side = 4 × 7 = 28 cm.", "Easy", 1),

    # TRIGONOMETRY (topic_id 5)
    (5, "In a right triangle, opposite = 3 and hypotenuse = 5. What is sin θ?", "3/5", "4/5", "5/3", "3/4", "A",
     "sin θ = opposite ÷ hypotenuse = 3/5.", "Easy", 1),
    (5, "If tan θ = 1 and θ is an acute angle, find θ.", "30°", "45°", "60°", "90°", "B",
     "For an acute angle, tan 45° = 1.", "Easy", 1),

    # STATISTICS (topic_id 6)
    (6, "Find the mean of 2, 4, 6 and 8.", "4", "5", "6", "20", "B",
     "Mean = (2 + 4 + 6 + 8) ÷ 4 = 20 ÷ 4 = 5.", "Easy", 1),
    (6, "Find the median of 3, 9, 5, 7 and 1.", "3", "5", "7", "9", "B",
     "Arrange the numbers: 1, 3, 5, 7, 9. The middle value is 5.", "Easy", 1),

    # PROBABILITY (topic_id 7)
    (7, "A fair six-sided die is rolled. What is the probability of getting a 4?", "1/2", "1/3", "1/6", "1/4", "C",
     "There is one outcome of 4 among six equally likely outcomes, so the probability is 1/6.", "Easy", 1),
    (7, "A bag contains 3 red and 2 blue balls. What is the probability of choosing a blue ball at random?", "2/5", "3/5", "1/2", "2/3", "A",
     "There are 2 blue balls out of 5 balls altogether. Probability = 2/5.", "Easy", 1),

    # GRAPHS (topic_id 8)
    (8, "For the equation y = 2x + 1, find y when x = 3.", "5", "6", "7", "8", "C",
     "Substitute x = 3: y = 2(3) + 1 = 7.", "Easy", 1),
    (8, "Which is the gradient of the line y = 4x - 2?", "−2", "2", "4", "−4", "C",
     "In y = mx + c, the gradient is the coefficient m of x. Here m = 4.", "Easy", 1),

    # FINANCIAL MATHEMATICS (topic_id 9)
    (9, "Calculate the simple interest on $500 at 10% per year for 2 years.", "$50", "$100", "$150", "$200", "B",
     "Simple interest = principal × rate × time = 500 × 0.10 × 2 = $100.", "Easy", 1),
    (9, "An item costs $80 and is discounted by 25%. What is the sale price?", "$20", "$55", "$60", "$75", "C",
     "Discount = 25% of $80 = $20. Sale price = $80 - $20 = $60.", "Easy", 1),
]


def add_questions():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    added = 0
    skipped = 0

    try:
        for item in new_questions:
            topic_id, question_text = item[0], item[1]

            existing = cursor.execute(
                """
                SELECT id FROM questions
                WHERE topic_id = ? AND question = ?
                """,
                (topic_id, question_text)
            ).fetchone()

            if existing:
                skipped += 1
                continue

            cursor.execute(
                """
                INSERT INTO questions (
                    topic_id, question,
                    option_a, option_b, option_c, option_d,
                    correct_answer, explanation, difficulty, marks
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                item
            )
            added += 1

        connection.commit()
        print(f"Questions added: {added}")
        print(f"Questions skipped because they already exist: {skipped}")

        total = cursor.execute(
            "SELECT COUNT(*) FROM questions"
        ).fetchone()[0]

        print(f"Total questions in database: {total}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    add_questions()
