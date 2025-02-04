import pdfkit

# Caminho para o executável do wkhtmltopdf (se necessário)
path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe" 

# Converter HTML em PDF
pdfkit.from_file(r'C:\Users\ieubi\OneDrive\Documentos\Vg\JuridicoPrimeSoho\JuridicoPrimeSoho\Proposta\PROPOSTA.html', 'output.pdf', configuration=pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf))
