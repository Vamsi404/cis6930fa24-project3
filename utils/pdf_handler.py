import re
import pandas as pd
from PyPDF2 import PdfReader

import pypdf
import re

#Global Variables
MODE_EXTRACTION = "layout"
MODE_LAYOUT = False



def extract_incidents(pdf_filepath):
    rows = []
    pdf_reader = pypdf.PdfReader(pdf_filepath)
    for page in pdf_reader.pages:
        text = page.extract_text(layout_mode_space_vertically=MODE_LAYOUT, extraction_mode=MODE_EXTRACTION)
        #print(text)
        if check_page(page):
            rows.extend(text.split('\n'))
        else:
            pass
            #print("No Text Found")
    result_data= parse_lines(rows[3:])
    df = pd.DataFrame(result_data, columns=["Date / Time", "Incident Number", "incident_location", "incident_nature","Incident ORI"])
    return df


def parse_lines(rows):
    pattern = r"(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2})\s+(\S+)\s+(.+?)(?=\s{2,}\S+)\s{2,}(.+?)\s{2,}(\S+)"

    parsed_data = []
    for row in rows:
        matches = re.findall(pattern, row)
        if matches:
            parsed_data.append(matches[0])
        else:
            pass
            # print("No match found")
    return parsed_data

def check_page(page):
    if(page):
        return True
    return False

