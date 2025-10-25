
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:5173/analise-peticao")

        # Explicitly wait for the button to be visible
        upload_button = page.get_by_role("button", name="Simular Upload (Dev)")
        expect(upload_button).to_be_visible(timeout=60000)

        upload_button.click()

        # Now, wait for the second step's title to appear
        step2_title = page.get_by_text("Documentos Sugeridos")
        expect(step2_title).to_be_visible(timeout=30000)

        # Take a screenshot of the second step
        page.screenshot(path="jules-scratch/verification/verification.png")
        browser.close()

run()
