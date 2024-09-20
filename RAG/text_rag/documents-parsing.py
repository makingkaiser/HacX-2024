"""
PLACE DOCUMENTS INSIDE OF DATA/DOCUMENTS AND RUN THIS TO PARSE DOCUMENTS 
FOR IMAGES, TEXT AND TABLES 
"""
import csv
import os
from pymupdf import open as open_pdf, Rect

base_path = os.path.dirname(__file__)
pdf_directory = os.path.join(base_path, "..", "..", "data-ingress", "documents")
pdf_directory = os.path.abspath(pdf_directory)

def save_images(doc, image_dir):
    # Function to save images from the PDF
    for i in range(len(doc)):
        for img in doc.get_page_images(i):
            xref = img[0]  # image reference number
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"image_page_{i+1}_{xref}.{image_ext}"
            image_filepath = os.path.join(image_dir, image_filename)
            with open(image_filepath, "wb") as img_file:
                img_file.write(image_bytes)
            print(f"Saved {image_filepath}")

def save_tables(doc, csv_dir):
    # Function to extract and save tables as CSV
    for page_num, page in enumerate(doc):
        tables = page.find_tables()
        for i, table in enumerate(tables):
            csv_filename = f"table_page_{page_num+1}_{i}.csv"
            csv_filepath = os.path.join(csv_dir, csv_filename)
            table_data = table.extract()
            with open(csv_filepath, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(table_data)
            print(f"Saved {csv_filepath}")

def extract_text_excluding_tables(doc, text_filepath):
    # Function to extract non-table text
    full_text = ""
    for page in doc:
        text_instances = page.get_text("blocks")
        page_tables = page.find_tables()
        table_rects = [Rect(table.bbox) for table in page_tables]
        for block in text_instances:
            block_rect = Rect(block[:4])
            if not any(block_rect.intersects(table_rect) for table_rect in table_rects):
                full_text += block[4] + "\n"
    with open(text_filepath, "w", encoding="utf-8") as text_file:
        text_file.write(full_text)
    print(f"Saved non-table text to {text_filepath}")

image_dir = os.path.join(base_path, "data", "images", "extracted_images")
csv_dir = os.path.join(base_path, "data", "documents", "extracted_csvs")
text_directory = os.path.join(base_path, "data", "documents", "raw_text")
os.makedirs(image_dir, exist_ok=True)
os.makedirs(csv_dir, exist_ok=True)
os.makedirs(text_directory, exist_ok=True)

# for pdf in pdf_directory:
for file_name in os.listdir(pdf_directory):
    if file_name.endswith('.pdf'):
        pdf_path = os.path.join(pdf_directory, file_name)
        doc = open_pdf(pdf_path)
        print(f"Processing {file_name}...")

        # create subdirectories for iamge and csv output
        pdf_base_name = os.path.splitext(file_name)[0]
        pdf_image_dir = os.path.join(image_dir, pdf_base_name)
        pdf_csv_dir = os.path.join(csv_dir, pdf_base_name)

        os.makedirs(pdf_image_dir, exist_ok=True)
        os.makedirs(pdf_csv_dir, exist_ok=True)


        # extract and save
        save_images(doc, pdf_image_dir)
        save_tables(doc, pdf_csv_dir)
        text_filename = os.path.join(text_directory, os.path.splitext(file_name)[0]+'.txt' )
        extract_text_excluding_tables(doc, text_filename)

        doc.close()
