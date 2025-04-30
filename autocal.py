import requests
import re
import os

def clean_title(title):
    """Clean the event title by removing unwanted parts."""
    # Example: Remove course codes and other unwanted text
    # replace 
    cleaned_title = re.sub(r'Implementering af programmeringssprog', r'IPS', title) 
    cleaned_title = re.sub(r'Databases and Information Systems', r'DIS', cleaned_title)
    cleaned_title = re.sub(r'Algoritmer og Datastrukturer', r'AD', cleaned_title)
    # remove everythng until the first ;
    cleaned_title = re.sub(r'^[^;]*;', '', cleaned_title)
    # replace with either lecutre or exerise
    cleaned_title = re.sub(r'Forelæsning/lecture', r'Lecture', cleaned_title)
    cleaned_title = re.sub(r'Teoretiske øvelser/theoretical exercises', r'Exercise', cleaned_title)
    cleaned_title = cleaned_title.strip()
    return cleaned_title

def download_ical(url, filename):
    """Download the iCal file from the URL."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded iCal file: {filename}")
    else:
        print("Failed to download iCal file.")
        return None
    return filename

def process_ical_lectures_and_exercises(input_file, output_file):
    """Process the iCal file to clean event titles for lectures and exercises."""
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        in_event = False
        for line in infile:
            if line.startswith("BEGIN:VEVENT"):
                in_event = True
            elif line.startswith("END:VEVENT"):
                in_event = False

            elif in_event and line.startswith("DESCRIPTION:"):
                original_description = line[12:].strip()
                cleaned_description = re.sub(r'Aktivitet.*?\\n', '', original_description)
                cleaned_description = re.sub(r'Beskrivelse.*?\\n', '', cleaned_description)
                cleaned_description = re.sub(r'Undervisningstype.*?\\n', '', cleaned_description)
                cleaned_description = re.sub(r'Underviser / Staff', 'Teacher', cleaned_description)
                cleaned_description = re.sub(r'Lokale / Room', 'Room', cleaned_description)
                cleaned_description = re.sub(r'Hold / Student Set', 'Group', cleaned_description)
                line = f"DESCRIPTION:{cleaned_description}\n"

            elif line.startswith("LOCATION:"):
                original_location = line[9:].strip()
                cleaned_location = re.sub(r'^[^-]*- ', '', original_location)
                line = f"LOCATION:{cleaned_location}\n"

            if in_event and line.startswith("SUMMARY:"):
                original_title = line[8:].strip()
                cleaned_title = clean_title(original_title)
                line = f"SUMMARY:{cleaned_title}\n"

            outfile.write(line)

def process_ical_assignments(input_file, output_file):
    """Process the iCal file to clean and shorten event titles for assignments."""
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        in_event = False
        buffer = ""
        for line in infile:
            if line.startswith("SUMMARY"):
                in_event = True
                buffer = line[:-1]
                continue
            if in_event:
                in_event = False
                if line[0] == " ":
                    buffer += line[1:]
                # shortened title is
                buffer = buffer[8:].strip()
                shortened_title = re.split(r"\[", buffer)
                
                #remove all character until ; using regex and remove ]
                shortened_title[1] = re.sub(r'^[^;]*;', '', shortened_title[1])
                shortened_title[1] = re.sub(r'\]', '', shortened_title[1])
            
                shortened_title[1] = re.sub(r'Implementering af programmeringssprog', r'IPS', shortened_title[1])
                shortened_title[1] = re.sub(r'Databases and Information Systems', r'DIS', shortened_title[1])
                shortened_title[1] = re.sub(r'Algoritmer og Datastrukturer', r'AD', shortened_title[1])

                shortened_title = shortened_title[1] + " - " + shortened_title[0]

                line = f"SUMMARY:{shortened_title}\n"

            outfile.write(line)
                           
            

# Usage
ical_url = "https://personligtskema.ku.dk/ical.asp?objectclass=student&id=bgd215"
assignments_url = "https://absalon.instructure.com/feeds/calendars/user_xsBGWlGBZ7dnHadz84HVlc0jxoz3oUgGo7klFwJG.ics"

downloaded_ical_lectures = download_ical(ical_url, "latest_calendar_lectures.ics")
if downloaded_ical_lectures:
    process_ical_lectures_and_exercises(downloaded_ical_lectures, "cleaned_calendar_lectures.ics")
    print("Processed iCal file for lectures and exercises saved as cleaned_calendar_lectures.ics")

downloaded_ical_assignments = download_ical(assignments_url, "latest_calendar_assignments.ics")
if downloaded_ical_assignments:
    process_ical_assignments(downloaded_ical_assignments, "cleaned_calendar_assignments.ics")
    print("Processed iCal file for assignments saved as cleaned_calendar_assignments.ics")

# Remove downloaded calendar files on exit
try:
    if downloaded_ical_lectures and os.path.exists(downloaded_ical_lectures):
        os.remove(downloaded_ical_lectures)
    if downloaded_ical_assignments and os.path.exists(downloaded_ical_assignments):
        os.remove(downloaded_ical_assignments)
    print("Temporary downloaded calendar files removed.")
except Exception as e:
    print(f"Error removing temporary files: {e}")
