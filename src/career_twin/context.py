from pypdf import PdfReader

reader = PDFReader("src/docs/profile.pdf")

linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

with open("src/docs/summary.txt", "r", encoding="utf-8") as file:
    summary = file.read()

TWIN_SYSTEM_PROMPT = f"""

    """.strip()