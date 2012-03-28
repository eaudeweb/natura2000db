#use http://pybrary.net/pyPdf/

from pyPdf import PdfFileWriter, PdfFileReader
import re

pattern = re.compile(r"RO(SCI|SPA)\d{4}") 

source_path = "/Users/cornel/Downloads/2011-10-20_protectia_naturii_RO_SPA_SDF_2011.pdf"
pdf = PdfFileReader(file(source_path, "rb"))

def save_pdf(output, name):
    outputStream = file("%s.pdf" % name, "wb")
    output.write(outputStream)
    outputStream.close()

output = PdfFileWriter()
for i in range(0, pdf.getNumPages()):
    page = pdf.getPage(i)
    #skip empty pages
    if page.has_key('/Contents'):
        text = page.extractText()
        if text.find('1. IDENTIFICAREA SITULUI') > 0:
            if i:
                save_pdf(output, name)
                output = PdfFileWriter()
            match = pattern.search(text)
            name = match.group(0)
        output.addPage(pdf.getPage(i))

#save last pages
save_pdf(output, name)
