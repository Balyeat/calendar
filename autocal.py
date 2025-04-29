import requests
import re

def clean_title(title):
    """Clean the event title by removing unwanted parts."""
    # Example: Remove course codes and other unwanted text
    # replace 
    cleaned_title = re.sub(r'Implementering af programmeringssprog', r'IPS', title) 
    cleaned_title = re.sub(r'Databases and Information Systems', r'DIS', cleaned_title)
    # remove everythng until the first ;
    cleaned_title = re.sub(r'^[^;]*;', '', cleaned_title)
    # replace with either lecutre or exerise
    cleaned_title = re.sub(r'Forelæsning/lecture', r'Lecture', cleaned_title)
    cleaned_title = re.sub(r'Teoretiske øvelser/theoretical exercises', r'Exercise', cleaned_title)
    cleaned_title = cleaned_title.strip()
    print(f"Origina title: {title}")
    print(f"Cleaned title: {cleaned_title}")
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

def process_ical(input_file, output_file):
    """Process the iCal file to clean event titles."""
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        in_event = False
        # REMOVE aktivitet and beskrivelse from DESCRIPTION
        for line in infile:
            if line.startswith("BEGIN:VEVENT"):
                in_event = True
            elif line.startswith("END:VEVENT"):
                in_event = False

            elif in_event and line.startswith("DESCRIPTION:"):
                # Clean the description
                original_description = line[12:].strip()
                # Example: Remove unwanted text
                # cleaned_description = re.sub(r'Aktivitet[^\n]*\n', '', original_description)
                cleaned_description = re.sub(r'Aktivitet.*?\\n', '', original_description)
                cleaned_description = re.sub(r'Beskrivelse.*?\\n', '', cleaned_description)
                cleaned_description = re.sub(r'Undervisningstype.*?\\n', '', cleaned_description)
                cleaned_description = re.sub(r'Underviser / Staff', 'Teacher', cleaned_description)
                cleaned_description = re.sub(r'Lokale / Room', 'Room', cleaned_description)
                cleaned_description = re.sub(r'Hold / Student Set', 'Group', cleaned_description)
                line = f"DESCRIPTION:{cleaned_description}\n"

                print(f"Cleaned description: {line}")
    
            elif line.startswith("LOCATION:"):
                # Clean the location
                original_location = line[9:].strip()
                # Example: remove all characters up to the first - and including the first - + " "
                cleaned_location = re.sub(r'^[^-]*- ', '', original_location)
                line = f"LOCATION:{cleaned_location}\n"

            if in_event and line.startswith("SUMMARY:"):
                # Clean the title
                original_title = line[8:].strip()
                # Example: Remove course codes and other unwanted text

                cleaned_title = clean_title(original_title)
                line = f"SUMMARY:{cleaned_title}\n"
            
            outfile.write(line)
# Usage
ical_url = "https://personligtskema.ku.dk/ical.asp?objectclass=student&id=bgd215"
downloaded_ical = download_ical(ical_url, "latest_calendar.ics")

if downloaded_ical:
    process_ical(downloaded_ical, "cleaned_calendar.ics")
    print("Processed iCal file saved as cleaned_calendar.ics")
