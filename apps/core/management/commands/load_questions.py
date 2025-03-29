import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.exam.models import Question, Choice, Subject, StudentClass


class Command(BaseCommand):
    help = "Load questions from an Excel file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the Excel file")

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]  # Read file path from command-line argument

        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File '{file_path}' not found!"))
            return

        # Read the Excel file
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading Excel file: {e}"))
            return

        # Check if required columns exist
        required_columns = ["Subject", "Class Group", "Question", "Choice 1", "Choice 2", "Choice 3", "Choice 4", "Correct Choice"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            self.stdout.write(self.style.ERROR(f"Missing columns in Excel file: {missing_columns}"))
            return

        # Insert data using atomic transaction
        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # Get or create Subject
                    subject, _ = Subject.objects.get_or_create(name=row["Subject"])
                    
                    # Get or create Class Group
                    class_group, _ = StudentClass.objects.get_or_create(name=row["Class Group"])

                    # Create question
                    question = Question.objects.create(
                        subject=subject,
                        class_group=class_group,
                        question=row["Question"]
                    )

                    # Create choices
                    for i in range(1, 5):
                        Choice.objects.create(
                            question=question,
                            body=row[f"Choice {i}"],
                            is_correct=(row["Correct Choice"] == i)
                        )

                    self.stdout.write(self.style.SUCCESS(f"Inserted question {index + 1}: {question.question}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error inserting row {index + 1}: {e}"))

        self.stdout.write(self.style.SUCCESS("Questions loaded successfully!"))

