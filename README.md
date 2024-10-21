# Final Wangler

Gradescope allows lecturers to download fine-grained evaluations data. For each problem/question in the exam/assessment, it generates a file where each row represents a student, and each column represent a rubric item, which is set to True when a given rubric item was applied to a given student.

The final_wrangle.py script takes as input this information as generates a single dataframe where each row represent a student and has a column called "report" that lists all the rubric items applied to that student broken up question by question. 

For a demonstration on how to use the scrip, please refer to the demo.ipynb notebook.