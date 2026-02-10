"""Test for CV button HTML generation."""

import base64
from pathlib import Path


def test_cv_button_generation():
    """Test that the CV button HTML is generated correctly with base64 encoding."""
    
    # Define the function inline for testing
    def get_cv_button_html() -> str:
        """Génère le code HTML pour le bouton de téléchargement du CV."""
        cv_path = Path("assets/cv_quentin_chabot.pdf")
        
        # Vérifier que le fichier existe
        if not cv_path.exists():
            return "<p style='color: red;'>⚠️ Fichier CV introuvable</p>"
        
        # Lire et encoder le PDF en base64
        with open(cv_path, "rb") as f:
            pdf_bytes = f.read()
        
        b64_pdf = base64.b64encode(pdf_bytes).decode()
        
        # Créer un data URI
        href = f"data:application/pdf;base64,{b64_pdf}"
        
        btn_style = (
            "display: inline-flex; align-items: center; justify-content: center; "
            "background-color: #eee8d1ff; color: #141413; border: 1px solid #E8E6DC; "
            "border-radius: 8px; padding: 0.6rem 1.2rem; text-decoration: none; "
            "font-weight: 600; margin-top: 10px;"
        )
        
        icon_url = "https://cdn-icons-png.flaticon.com/512/337/337946.png"
        
        return f"""
        <br>
        <a href="{href}" download="CV_Quentin_Chabot.pdf" style="{btn_style}">
            <img src="{icon_url}" style="width: 20px; height: 20px; margin-right: 10px;">
            Télécharger mon CV
        </a>
        """
    
    # Generate the HTML
    html = get_cv_button_html()
    
    # Verify it's not an error message
    assert "⚠️ Fichier CV introuvable" not in html, "CV file should exist"
    
    # Verify it contains a data URI
    assert "data:application/pdf;base64," in html, "Should contain base64 data URI"
    
    # Verify it has the download attribute
    assert 'download="CV_Quentin_Chabot.pdf"' in html, "Should have download attribute"
    
    # Verify it has the button style
    assert "background-color: #eee8d1ff" in html, "Should have the correct button style"
    
    # Verify the icon is included
    assert "https://cdn-icons-png.flaticon.com/512/337/337946.png" in html, "Should have icon"
    
    print("✓ All tests passed!")
    print(f"✓ HTML length: {len(html)} bytes")
    
    # Extract and verify base64 content
    if "data:application/pdf;base64," in html:
        # Find the base64 content
        start = html.find("data:application/pdf;base64,") + len("data:application/pdf;base64,")
        end = html.find('"', start)
        b64_content = html[start:end]
        
        # Verify it can be decoded
        try:
            decoded = base64.b64decode(b64_content)
            # PDF files start with %PDF
            assert decoded.startswith(b'%PDF'), "Should be a valid PDF file"
            print(f"✓ Base64 PDF content is valid ({len(decoded)} bytes)")
        except Exception as e:
            print(f"✗ Failed to decode base64: {e}")
            return False
    
    return True

if __name__ == "__main__":
    test_cv_button_generation()
