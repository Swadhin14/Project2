import fitz

doc = fitz.open()
page = doc.new_page()
page.insert_text((50, 50), "John Doe\nSoftware Engineer\nExperience: Python, FastAPI\nEducation: Computer Science")
doc.save("d:/Hirable/test_resume.pdf")
print("PDF created successfully at d:/Hirable/test_resume.pdf")
