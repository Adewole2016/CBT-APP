import pandas as pd
from django.core.management.base import BaseCommand
from apps.exam.models import Answer  # Import your model

class Command(BaseCommand):
    help = "Export student exam results to Excel"

    def handle(self, *args, **kwargs):
        # Fetch all exam results
        results = Answer.objects.select_related("exam", "user", "exam__class_group")

        # Prepare data for export
        data = []
        for result in results:
            data.append({
                "Username": result.user.username,
                "Full Name": result.user.get_full_name(),
                "Class": result.exam.class_group.name,  # Fetch student class
                "Subject": result.exam.subject.name,
                "Score": result.score,
                "Total Questions": result.total_questions,
                "Percentage": result.percent(),
            })

        # Convert to Pandas DataFrame
        df = pd.DataFrame(data)

        # Save to Excel file
        file_path = "exam_results.xlsx"
        df.to_excel(file_path, index=False, engine="openpyxl")

        self.stdout.write(self.style.SUCCESS(f"Data exported successfully to {file_path}"))

