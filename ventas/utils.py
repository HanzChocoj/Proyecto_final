# proyectof/ventas/utils.py
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

def render_to_pdf(template_src: str, context: dict, *, download: bool = False, filename: str = "comprobante.pdf"):
    """
    Renderiza una plantilla HTML a PDF usando xhtml2pdf.
    - template_src: ruta de la plantilla (p.ej. 'ventas/pdf/venta_comprobante.html')
    - context: contexto con datos
    - download: si True, fuerza descarga; si False, lo abre en el navegador
    - filename: nombre sugerido del archivo
    """
    html = render_to_string(template_src, context)
    result = BytesIO()
    pdf = pisa.CreatePDF(src=html, dest=result, encoding='utf-8')

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        dispo = 'attachment' if download else 'inline'
        response['Content-Disposition'] = f'{dispo}; filename="{filename}"'
        return response
    # Si hay error, devolver el HTML para depurar
    return HttpResponse("Error generando PDF.<br><pre>" + html + "</pre>")
