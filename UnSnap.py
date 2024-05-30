import csv
from datetime import datetime
import hashlib
import os
import argparse
import pytz

def parse_timestamp(timestamp_str):
    if timestamp_str is None:
        return None
    try:
        return datetime.strptime(timestamp_str, '%a %b %d %H:%M:%S %Z %Y').replace(tzinfo=pytz.UTC)
    except ValueError:
        return None

def find_actual_header(file):
    while True:
        line = file.readline().strip()
        if line.startswith('id,from,to,body,href,media_id,saved,timestamp'):
            return line.split(',')
        if not line:
            raise ValueError("Actual header not found in the CSV file.")
'''
def extract_media_id(string):
    parts = string.split('~')
    media_id = parts[-1] if len(parts) > 1 else string
    
    return media_id
'''
def extract_media_id(string):
    if string is None:
        return ''
    parts = string.split('~')
    media_id = parts[-1] if len(parts) > 1 else string
    return media_id

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate a forensically sound report from a CSV file.')
    parser.add_argument('filename', type=str, help='The path to the CSV file')
    parser.add_argument('--from', dest='from_user', type=str, help='Filter by the sender')
    parser.add_argument('--to', dest='to_user', type=str, help='Filter by the recipient')
    parser.add_argument('--output', type=str, default='report.html', help='The path to save the report')
    parser.add_argument('--timezone', type=str, default='UTC', help='Time zone for timestamp display (default: UTC)')
    return parser.parse_args()

def calculate_hashes(filename):
    sha256_hash = hashlib.sha256()
    sha1_hash = hashlib.sha1()

    with open(filename, "rb") as file:
        while chunk := file.read(8192):
            sha256_hash.update(chunk)
            sha1_hash.update(chunk)

    return sha256_hash.hexdigest(), sha1_hash.hexdigest()

def locate_media_files(media_id):
    directory = os.getcwd()
    matching_files = []
    inverted_media_id = '-'.join(reversed(media_id.split('-')))
    
    
    for root, _, files in os.walk(directory):
        
        for file in files:
            if media_id in file or inverted_media_id in file:
                matching_files.append(os.path.join(root, file))
    return matching_files

def generate_report(args, metadata, messages):
    
    with open(args.output, 'w', encoding='utf-8') as report_file:
        report_file.write("""
        <html>
        <head>
            <title>SnapChat Return Forensic Report</title>
            <style>
                body { font-family: Arial, sans-serif; }
                .conversations { margin: 20px; }
                .timestamp { color: grey; font-size: 0.9em; }
                .sender-blue { color: blue; }
                .sender-red { color: red; }
                .media-file { color: green; }
            </style>
            <script>
                function updateTimestamps() {
                    var offset = parseFloat(document.getElementById('offset').value) || 0;
                    var isDst = document.getElementById('dst').checked;
                    var totalOffset = offset + (isDst ? 1 : 0);

                    var timestamps = document.getElementsByClassName('timestamp');
                    for (var i = 0; i < timestamps.length; i++) {
                        var originalTimestamp = new Date(timestamps[i].getAttribute('data-original'));
                        var newTimestamp = new Date(originalTimestamp.getTime() + totalOffset * 60 * 60 * 1000);
                        timestamps[i].innerText = newTimestamp.toLocaleString();
                    }

                    document.getElementById('current-offset').innerText = 'UTC Offset: ' + totalOffset + ' hour(s)';
                    document.getElementById('current-dst').innerText = 'Daylight Saving Time: ' + (isDst ? 'Enabled' : 'Disabled');
                }
            </script>
        </head>
        <body>
        """)

        # Write metadata and other information
        report_file.write(f"<h1>SnapChat Return: Forensic Report</h1>")
        report_file.write(f"<p>Examiner: {metadata['examiner']}</p>")
        report_file.write(f"<p>Case Number: {metadata['case_number']}</p>")
        report_file.write(f"<p>Source Directory: {os.getcwd()}</p>")  # Display the source directory
        
        report_file.write(f"<p>File Name: {metadata['filename']}</p>")
        report_file.write(f"<p>SHA-256: {metadata['sha256']}</p>")
        report_file.write(f"<p>SHA-1: {metadata['sha1']}</p>")
        
        # Add timezone and DST adjustment form
        report_file.write("""
        <h2>Adjust Timezone and Daylight Saving Time</h2>
        <form oninput="updateTimestamps()">
            <label for="offset">Timezone Offset (hours):</label>
            <input type="number" id="offset" name="offset" value="0" step="1">
            <label for="dst">Daylight Saving Time:</label>
            <input type="checkbox" id="dst" name="dst">
            <p id="current-offset">Current Offset: 0 hour(s)</p>
            <p id="current-dst">Daylight Saving Time: Disabled</p>
        </form>
        """)

        report_file.write("<h2>Conversations</h2>")
        report_file.write("<div class='conversations'>")

        # Filter and sort messages by timestamp, handling invalid timestamps
        all_messages = sorted(
            [msg for msg in messages if msg['timestamp'] is not None],
            key=lambda x: x['timestamp']
        )

        color_toggle = True  # Start with blue
        last_sender = None  # Track the last sender

        for message in all_messages:
            sender = message['from']
            recipient = message['to']
            original_time = message['timestamp']
            formatted_time = original_time.strftime('%Y-%m-%d %I:%M:%S %p')
            
            if sender != last_sender:
                color_toggle = not color_toggle  # Toggle color when sender changes
                last_sender = sender

            sender_class = 'sender-blue' if color_toggle else 'sender-red'

            report_file.write(f"<p><span class='timestamp' data-original='{original_time.isoformat()}'>{formatted_time}</span><br><span class='{sender_class}'>{sender} </span></p>")

            if message['media_id']:
                media_id = extract_media_id(message['media_id'])
                media_files = locate_media_files(media_id)
                if media_files:
                    for media_file in media_files:
                        file_extension = os.path.splitext(media_file)[1].lower()
                        if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                            report_file.write(f"<p class='media-file'><img src='{media_file}' alt='Media file' style='max-width: 400px;'></p>")
                        elif file_extension in ['.mp4', '.webm', '.ogg']:
                            report_file.write(f"<p class='media-file'><video controls style='max-width: 400px;'><source src='{media_file}' type='video/{file_extension[1:]}'></video></p>")
                        else:
                            report_file.write(f"<p class='media-file'><a href='{media_file}'>{os.path.basename(media_file)}</a></p>")
                        # Add media location to message
                        message['media_location'] = media_files
                else:
                    report_file.write(f"<p class='media-file'>Media file not found for ID: {media_id}</p>")
            else:
                report_file.write(f"<p>{message['body']}<br><span class='{sender_class}'>________________________</p></span>")

        report_file.write("</div>")
        report_file.write("</body></html>")
        print("HTML report generated successfully.")


def main():
    args = parse_arguments()

    metadata = {
        'filename': args.filename,
        'examiner': input("Enter Examiner's Name: "),
        'case_number': input("Enter Case Number: "),
    }

    metadata['sha256'], metadata['sha1'] = calculate_hashes(args.filename)

    with open(args.filename, mode='r', newline='', encoding='utf-8') as file:
        fieldnames = find_actual_header(file)
        if len(fieldnames) != len(set(fieldnames)):
            raise ValueError("CSV file contains duplicate field names")
        file.seek(0)  # Move back to the beginning of the file
        raw_data = csv.DictReader(file, fieldnames=fieldnames)
        
        messages = []
        for row in raw_data:
            if row['id'] == 'id':
                continue  # Skip header row
            timestamp = parse_timestamp(row['timestamp'])
            message = {
                'id': row['id'],
                'from': row['from'],
                'to': row['to'],
                'body': row['body'],
                'href': row['href'],
                'media_id': extract_media_id(row['media_id']),
                'saved': row['saved'],
                'timestamp': timestamp,
            }
            messages.append(message)
    
    filtered_messages = []
    for message in messages:
        if args.from_user and args.to_user:
            if (message['from'] == args.from_user and message['to'] == args.to_user) or \
               (message['from'] == args.to_user and message['to'] == args.from_user):
                filtered_messages.append(message)
        elif args.from_user:
            if message['from'] == args.from_user:
                filtered_messages.append(message)
        elif args.to_user:
            if message['to'] == args.to_user:
                filtered_messages.append(message)
        else:
            filtered_messages.append(message)

    
    generate_report(args, metadata, filtered_messages)

if __name__ == '__main__':
    main()