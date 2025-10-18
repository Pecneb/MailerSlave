"""CSV Reader module for reading email addresses from CSV files."""

import csv
from pathlib import Path
from typing import List, Dict


class CSVReader:
    """Reads email addresses and associated data from CSV files."""

    def __init__(self, csv_path: str):
        """
        Initialize the CSV reader.

        Args:
            csv_path: Path to the CSV file
        """
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

    def read_emails(self) -> List[Dict[str, str]]:
        """
        Read email addresses and associated data from the CSV file.

        Returns:
            List of dictionaries containing email data
        """
        emails_data = []

        with open(self.csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Validate that the CSV has an 'email' column
            if "email" not in reader.fieldnames:
                raise ValueError("CSV file must contain an 'email' column")

            for row in reader:
                if row.get("email"):  # Skip empty email rows
                    emails_data.append(row)

        return emails_data

    def get_email_count(self) -> int:
        """
        Get the total number of emails in the CSV file.

        Returns:
            Number of email addresses
        """
        return len(self.read_emails())
