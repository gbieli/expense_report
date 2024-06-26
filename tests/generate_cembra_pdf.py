from xhtml2pdf import pisa


def convert_html_to_pdf(html_string, pdf_path):
    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_string, dest=pdf_file)

    return not pisa_status.err


# HTML content
html_content = """
<html>
<style>
table, th, td {
  border:1px solid black;
}
</style>
<body>
    Neue Belastungen CHF 1'555.95<br><br><br>
    <table style="width:100%">
      <tr>
        <th width="15%">Einkaufs-Datum</th>
        <th width="15%">Verbucht am</th>
        <th width="40%">Beschreibung</th>
        <th width="15%">Gutschrift CHF</th>
        <th width="15%">Belastung CHF</th>
      </tr>
      <tr>
        <td>02.12.2023</td>
        <td>03.12.2023</td>
        <td>Musterladen Musterstadt AG CHE</td>
        <td></td>
        <td>114.15</td>
      </tr>
      <tr>
        <td>04.12.2023</td>
        <td>05.12.2023</td>
        <td>Dummy Musterstadt AG CHE</td>
        <td></td>
        <td>85.15</td>
      </tr>
    </table>
</body>
</html>
"""

# Generate PDF
pdf_path = "test_data/cembra_dummy.pdf"
if convert_html_to_pdf(html_content, pdf_path):
    print(f"PDF generated and saved at {pdf_path}")
else:
    print("PDF generation failed")
