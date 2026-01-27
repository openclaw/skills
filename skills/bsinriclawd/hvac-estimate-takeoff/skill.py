import os
from clawdbot import AgentSkill

class HVACEstimateTakeoff(AgentSkill):
    def __init__(self):
        super().__init__(name="hvac_estimate_takeoff")

    def trigger(self, event):
        if event['type'] == 'file_upload' and event['file_type'] == 'pdf':
            self.process_pdf(event['file_path'])

    def process_pdf(self, file_path):
        import fitz  # pymupdf
        doc = fitz.open(file_path)
        data = []
        for page in doc:
            text = page.get_text()
            items = self.extract_items(text)
            data.extend(items)
        self.output_table(data)

    def extract_items(self, text):
        items = []
        # Logic to extract items from text
        return items

    def output_table(self, items):
        for item in items:
            print(f"{item['name']} | {item['description']} | {item['size_capacity']} | {item['qty']} | {item['notes']}")

skill = HVACEstimateTakeoff()