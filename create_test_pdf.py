"""
Generates a test PDF in data/uploads/ with known content for RAG validation.
The PDF simulates a rental contract so we can assert the RAG system retrieves
the right arrendador/arrendatario names.

Usage:
    python create_test_pdf.py
"""
import os

OUTPUT_PATH = os.path.join("data", "uploads", "contrato-arrendamiento.pdf")

def create_pdf_fpdf2():
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    lines = [
        "CONTRATO DE ARRENDAMIENTO",
        "",
        "En la ciudad de Mexico, a 1 de enero de 2025, se celebra el presente",
        "contrato de arrendamiento entre las siguientes partes:",
        "",
        "ARRENDADOR: Juan Carlos Perez Lopez, con RFC PELJ800101XXX,",
        "domicilio en Calle Reforma 123, Col. Centro, Ciudad de Mexico.",
        "",
        "ARRENDATARIO: Maria Fernanda Torres Ruiz, con RFC TORM900202YYY,",
        "domicilio en Av. Insurgentes 456, Col. Roma Norte, Ciudad de Mexico.",
        "",
        "OBJETO DEL CONTRATO:",
        "El arrendador da en arrendamiento al arrendatario el inmueble ubicado",
        "en Calle Juarez 789, Col. Polanco, Ciudad de Mexico, CP 11550.",
        "El inmueble es de uso exclusivamente habitacional.",
        "",
        "VIGENCIA:",
        "El presente contrato tendra una vigencia de 12 (doce) meses,",
        "contados a partir del 1 de enero de 2025 hasta el 31 de diciembre de 2025.",
        "",
        "RENTA MENSUAL:",
        "La renta mensual pactada es de $15,000.00 (quince mil pesos 00/100 M.N.),",
        "pagadera los primeros cinco dias naturales de cada mes.",
        "",
        "DEPOSITO EN GARANTIA:",
        "El arrendatario entrega en este acto la cantidad de $30,000.00",
        "(treinta mil pesos 00/100 M.N.) como deposito en garantia.",
        "",
        "CLAUSULAS:",
        "1. El arrendatario no podra subarrendar el inmueble sin autorizacion escrita.",
        "2. El arrendatario es responsable del pago de servicios (agua, luz, gas).",
        "3. El arrendador se compromete a entregar el inmueble en buenas condiciones.",
        "4. Cualquier modificacion al inmueble requiere autorizacion del arrendador.",
        "",
        "FIRMAS:",
        "",
        "________________________           ________________________",
        "Juan Carlos Perez Lopez            Maria Fernanda Torres Ruiz",
        "ARRENDADOR                         ARRENDATARIO",
    ]

    for line in lines:
        pdf.cell(0, 8, line, ln=True)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    pdf.output(OUTPUT_PATH)
    print(f"PDF created: {OUTPUT_PATH}")
    print("Known facts for RAG validation:")
    print("  - Arrendador: Juan Carlos Perez Lopez")
    print("  - Arrendatario: Maria Fernanda Torres Ruiz")
    print("  - Renta: $15,000 MXN/mes")
    print("  - Vigencia: 1 ene 2025 - 31 dic 2025")


def create_pdf_raw():
    """Fallback: write a minimal valid PDF manually (no library needed)."""
    content_lines = [
        "CONTRATO DE ARRENDAMIENTO",
        "Arrendador: Juan Carlos Perez Lopez",
        "Arrendatario: Maria Fernanda Torres Ruiz",
        "Objeto: Inmueble en Calle Juarez 789 Col. Polanco Ciudad de Mexico",
        "Renta mensual: $15,000 MXN",
        "Vigencia: 1 enero 2025 al 31 diciembre 2025",
        "Deposito en garantia: $30,000 MXN",
    ]
    text = "\n".join(content_lines)

    # Build minimal PDF structure
    stream = f"BT\n/F1 12 Tf\n50 750 Td\n"
    for i, line in enumerate(content_lines):
        safe = line.replace("(", r"\(").replace(")", r"\)").replace("\\", "\\\\")
        stream += f"({safe}) Tj\n0 -18 Td\n"
    stream += "ET"

    stream_bytes = stream.encode("latin-1", errors="replace")
    stream_len = len(stream_bytes)

    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
        b" /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        + f"4 0 obj\n<< /Length {stream_len} >>\nstream\n".encode()
        + stream_bytes
        + b"\nendstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000266 00000 n \n"
        b"0000000999 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\n"
        b"startxref\n1100\n%%EOF\n"
    )

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "wb") as f:
        f.write(pdf)
    print(f"PDF created (raw fallback): {OUTPUT_PATH}")


if __name__ == "__main__":
    try:
        create_pdf_fpdf2()
    except ImportError:
        print("fpdf2 not installed, using raw PDF fallback...")
        create_pdf_raw()
        print(f"Created: {OUTPUT_PATH}")
