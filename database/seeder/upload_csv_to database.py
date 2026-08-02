import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("SUPABASE_URL"))
print(os.getenv("SUPABASE_KEY")[:20])
# LOAD ENV

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# CONFIG

BATCH_SIZE = 500

TABLE_FILES = [
    ("accounts", "accounts.csv"),
    ("users", "users.csv"),
    ("subscriptions", "subscriptions.csv"),
    ("invoices", "invoices.csv"),
    ("invoice_line_items", "invoice_line_items.csv"),
    ("tickets", "tickets.csv"),
]

# HELPERS

def clean_dataframe(df):
    """
    Convert NaN to None so Supabase accepts values.
    """

    df = df.where(pd.notnull(df), None)

    return df


def upload_table(table_name, csv_file):

    print(f"\nUploading {table_name}...")

    df = pd.read_csv(csv_file)

    df = clean_dataframe(df)

    records = df.to_dict(orient="records")

    total_records = len(records)

    print(f"Found {total_records} rows")

    for i in range(0, total_records, BATCH_SIZE):

        batch = records[i:i + BATCH_SIZE]

        try:

            supabase.table(table_name).insert(batch).execute()

            print(
                f"{table_name}: "
                f"{min(i+BATCH_SIZE,total_records)}/{total_records}"
            )

        except Exception as e:

            print(
                f"\nERROR inserting batch into {table_name}"
            )

            print(e)

            raise

    print(f"{table_name} upload complete")


# MAIN

if __name__ == "__main__":

    print("\nStarting Upload\n")

    for table_name, csv_file in TABLE_FILES:

        upload_table(
            table_name,
            csv_file
        )

    print("\nAll data uploaded successfully\n")