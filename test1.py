from bs4 import BeautifulSoup
import os

report_path = "C:\\Windows\\Temp\\battery-report.html"

with open(report_path, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')
    tables = soup.find_all('table')

    for idx, table in enumerate(tables):
        heading = table.find_previous("h2")
        print(f"\n[🔹 Table {idx+1}] Title: {heading.text.strip() if heading else 'No heading'}")
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_data = [cell.text.strip() for cell in cells]
            print(f" - {row_data}")
