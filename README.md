SnapChat Return Forensic Report Generator

This Python script generates a forensically sound HTML report from a CSV file containing SnapChat return data.
The report includes metadata such as examiner details, hash values for integrity verification, and a user-friendly
interface for adjusting timezone and daylight saving time settings.
*Work in progress.  

Features

Forensic Metadata:
Includes examiner name, case number, source directory, and file hashes (SHA-256 and SHA-1) for integrity verification.
Media Handling:
Automatically locates and displays media files (images and videos) associated with messages.
Timezone and DST Adjustment:
User-friendly form to adjust timestamps according to different timezones and daylight saving time.
Message Filtering:
Option to filter messages by sender and recipient.
Forensic Soundness:
Ensures data integrity and accurate reporting.

Ensure you have installed pytz
pip install pytz

Usage

Prepare your CSV file:

*preformatted chat.csv received from SnapChat.

Ensure your CSV file contains the following columns: 

   id,from,to,body,href,media_id,saved,timestamp



Run the script:

python unsnap.py [options]

Options:
filename: The path to the CSV file (required).
--from: Filter by the sender (optional).
--to: Filter by the recipient (optional).
--output: The path to save the report (current python script working directory is the default: report.html).
Example:
python report_generator.py data.csv --from alice --to bob --output report.html 

Input Metadata:
When prompted, enter the examiner's name and case number.

Sample Workflow
Clone the repository:

python unsnap.py sample_data.csv

Enter Metadata:
Enter Examiner's Name: John Doe
Enter Case Number: 123456
Open the Report:
Open the generated report.html in your browser to view the forensic report.

Functions
parse_timestamp(timestamp_str): Parses a timestamp string into a datetime object.
find_actual_header(file): Finds the actual header row in the CSV file.
extract_media_id(string): Extracts the media ID from a string.
parse_arguments(): Parses command-line arguments.
calculate_hashes(filename): Calculates SHA-256 and SHA-1 hashes of the CSV file.
locate_media_files(media_id): Locates media files based on the media ID.
generate_report(args, metadata, messages): Generates the HTML report.
main(): Main function to run the script.

Error Handling
Ensures the CSV file contains the correct header.
Handles invalid timestamps.
Checks for duplicate field names in the CSV file.
Contributing
Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

License
This project is licensed under the MIT License.
