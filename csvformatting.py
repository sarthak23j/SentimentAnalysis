import csv

# Input and output file names
input_file = "flipkart_data.csv"  # Change to your actual file name
output_file = "formatted_reviews.csv"

# Read input file and write output file
with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8", newline="") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # Write new header
    writer.writerow(["sl.no", "review"])

    # Skip header of input file (if it has one)
    next(reader, None)

    # Write modified rows
    for index, row in enumerate(reader, start=1):
        writer.writerow([index, row[0]])  # Only keeping the review column

print(f"Formatted CSV saved as {output_file}")
