# app_apmthr/paiements/utils.py
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import get_template

def html_to_pdf(source_html, output_filename):
    """
    Génère un PDF et l'enregistre sur disque.
    """
    with open(output_filename, "wb") as output_file:
        pisa_status = pisa.CreatePDF(source_html, dest=output_file)
        if pisa_status.err:
            raise Exception("Erreur lors de la génération du PDF")

def generate_pdf(template_name, context, filename):
    """
    Génère un PDF à partir d'un template Django et d'un contexte.
    Retourne un HttpResponse contenant le PDF pour téléchargement.
    """
    template = get_template(template_name)
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)
    return response
