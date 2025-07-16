import csv

class CSVWriter:
    def __init__(self, filename):
        self.file = open(filename, mode='w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=[
            "Name", "Email", "Source URL", "Platform"
        ])
        self.writer.writeheader()

    def write_row(self, data):
        self.writer.writerow(data)

    def close(self):
        self.file.close()
