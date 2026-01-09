# Import modules needed for this program
import csv
from datetime import datetime

# Name of the input CSV file with metadata
INPUT_FILE = "metadata.csv"

# Name of the output CSV file for the results
OUTPUT_FILE = "report.csv"

# List of metadata fields that must not be empty
REQUIRED_FIELDS = ["filename", "title", "creator", "date", "license", "format"]

# List of licenses that are allowed
ALLOWED_LICENSES = ["CC0-1.0", "CC-BY-4.0", "MIT", "GPL-3.0"]


# Read the CSV file and return all rows as a list
def load_rows(path):
    # Open the CSV file in read mode
    with open(path, mode="r", encoding="utf-8", newline="") as f:
        # Read each row as a dictionary (column name → value)
        reader = csv.DictReader(f)
        return list(reader)


# Check if required fields are missing
def check_required_fields(row):
    issues = []

# Loop over all required fields
    for field in REQUIRED_FIELDS:
        value = (row.get(field) or "").strip()
        
        # If the field is empty, add an issue
        if value == "":
            issues.append(f"Missing {field}")

    return issues

# Check if the date has the format YYYY-MM-DD
def check_date(row):
    issues = []

    date_value = (row.get("date") or "").strip()
    if date_value == "":
        return issues  # missing dates are handled elsewhere

    try:
        # Try to read the date using the expected format
        datetime.strptime(date_value, "%Y-%m-%d")
    except ValueError:
        # If this fails, the date format is invalid
        issues.append("Invalid date format (expected YYYY-MM-DD)")

    return issues

# Check if the license value is allowed
def check_license(row):
    issues = []

    license_value = (row.get("license") or "").strip()
    if license_value == "":
        return issues  # missing license handled elsewhere

    if license_value not in ALLOWED_LICENSES:
        issues.append(f"License not allowed: {license_value}")

    return issues

# Check if the filename follows a simple naming convention
def check_filename(row):
    issues = []

    filename = (row.get("filename") or "").strip()
    if filename == "":
        return issues  # missing filename handled elsewhere

    # Check that the filename has an extension
    if "." not in filename:
        issues.append("Filename has no file extension")
        return issues

    # Split filename into name and extension
    name_part, extension = filename.rsplit(".", 1)

    # Split the name into parts using underscores
    parts = name_part.split("_")

    # Expect at least date, project, description, and version
    if len(parts) < 4:
        issues.append("Filename does not follow expected structure")
        return issues

    date_part = parts[0]
    version_part = parts[-1]

    # Check date part (YYYYMMDD)
    if len(date_part) != 8 or not date_part.isdigit():
        issues.append("Filename date must be YYYYMMDD")

    # Check version part (v01, v02, ...)
    if not version_part.startswith("v") or not version_part[1:].isdigit():
        issues.append("Filename version must look like v01")

    return issues

# Write a report CSV file with an additional column called "issues"
def write_report(rows, all_issues, path):
    # Use original column names plus a new "issues" column
    fieldnames = list(rows[0].keys()) + ["issues"]

    with open(path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Write each row together with its issues
        for row, issues in zip(rows, all_issues):
            out_row = dict(row)
            out_row["issues"] = "; ".join(issues)
            writer.writerow(out_row)

# Main function that controls the program
def main():
    # Load metadata from the input CSV file
    rows = load_rows(INPUT_FILE)
    print(f"Loaded {len(rows)} rows.")
    
    all_issues = []

    # Check each row and collect its issues
    for i, row in enumerate(rows, start=1):
        issues = check_required_fields(row)
        issues += check_date(row)
        issues += check_license(row)
        issues += check_filename(row)
        all_issues.append(issues)

# Write the results to the output CSV file
    write_report(rows, all_issues, OUTPUT_FILE)
    
# Print a short summary to the console
    rows_with_issues = sum(1 for issues in all_issues if issues)
    print(f"Wrote {OUTPUT_FILE}. {rows_with_issues}/{len(rows)} rows have issues.")



# Start the program here
if __name__ == "__main__":
    main()


