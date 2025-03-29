import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.core.models import User, StudentClass  # Correct path

class Command(BaseCommand):
    help = "Load student data from Excel into the database"

    def handle(self, *args, **kwargs):
        file_path = "DATA.xlsx"  # Update this with the actual path
        df = pd.read_excel(file_path)
        df.fillna("", inplace=True)  # Replace NaN with empty strings

        for _, row in df.iterrows():
            student_class, _ = StudentClass.objects.get_or_create(name=row["Level"])

            # Convert first name to uppercase for the password
            default_password = row["First Name"].upper()

            user, created = User.objects.get_or_create(
                username=row["Student ID"],
                defaults={
                    "first_name": row["First Name"],
                    "last_name": row["Last Name"],
                    "gender": row["Gender"].lower(),
                    "student_class": student_class,
                    "password": make_password(default_password),  # Hash password
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f"Added {row['First Name']} {row['Last Name']} with default password: {default_password}"
                ))
            else:
                self.stdout.write(self.style.WARNING(f"User {row['Student ID']} already exists"))

