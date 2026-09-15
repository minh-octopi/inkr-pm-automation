import asyncio
import os
from playwright.async_api import async_playwright, BrowserContext
import config

# --- Constants ---
LOGIN_URL = "https://mystudio.inkr.com/"

# The file to save session cookies and local storage. This is in .gitignore.
SESSION_FILE = "session.json"

# A selector for an element that is ONLY visible after a successful login.
# This is critical for verifying the session is valid.
# TODO: UNVERIFIED. Requires a real INKR account to reach the studio dashboard
# and confirm this selector (the .env file currently has placeholder credentials).
DASHBOARD_SELECTOR = "div.studio-dashboard"  # Example: a class on the main dashboard container


async def _perform_login(context: BrowserContext):
    """
    Private function to perform the login action on the website.
    It fills the form, submits, and saves the session state upon success.

    Args:
        context: The Playwright browser context to use.
    """
    page = await context.new_page()
    try:
        await page.goto(LOGIN_URL, wait_until="networkidle")
        print("Navigated to login page.")

        print("Attempting to log in with provided credentials...")
        if not config.INKR_EMAIL or not config.INKR_PASSWORD:
            raise ValueError("INKR_EMAIL and INKR_PASSWORD must be set in the .env file.")

        # --- Verified selectors (confirmed via live inspection of mystudio.inkr.com) ---
        # Step 1: The landing page has no login form directly. Clicking "Sign In"
        # redirects to account.inkr.com/login, which handles auth via a separate flow.
        await page.get_by_role("button", name="Sign In", exact=True).click()
        await page.wait_for_url("**/account.inkr.com/login**", timeout=15000)

        # Step 2: Enter email and continue. INKR branches here based on whether the
        # email is registered (password step) or not (signup step).
        email_input_selector = 'input[placeholder="Enter your email..."]'
        await page.fill(email_input_selector, config.INKR_EMAIL)
        await page.get_by_role("button", name="Continue", exact=True).first.click()
        await page.wait_for_timeout(1000)

        # --- TODO: UNVERIFIED beyond this point ---
        # Could not confirm the password-step selectors because the .env file has
        # placeholder credentials (your_email@example.com), which INKR treats as an
        # unregistered email and routes to a signup form instead of a password field.
        # Once real credentials are set, re-run inspection to confirm/adjust these:
        password_input_selector = 'input[type="password"]'
        submit_button_selector = 'button:has-text("Continue")'

        await page.fill(password_input_selector, config.INKR_PASSWORD)
        await page.click(submit_button_selector)

        # Wait for the dashboard to appear after login to confirm success.
        await page.wait_for_selector(DASHBOARD_SELECTOR, timeout=30000)
        print("Login successful, dashboard element found.")

        # Save the session state (cookies, local storage, etc.) to the file.
        await context.storage_state(path=SESSION_FILE)
        print(f"Session state saved to '{SESSION_FILE}'.")

    except Exception as e:
        await context.browser.close()
        raise Exception(f"Login failed: {e}")
    finally:
        await page.close()


async def get_authenticated_context(playwright) -> BrowserContext:
    """
    Ensures we have a logged-in browser context.

    It first tries to load a saved session from session.json. If the session is
    invalid or the file doesn't exist, it performs a new login and saves the session.

    Args:
        playwright: The Playwright instance.

    Returns:
        A logged-in BrowserContext ready for scraping.
    """
    # For development, `headless=False` is useful to watch the browser actions.
    browser = await playwright.chromium.launch(headless=False)

    # 1. Try to load the saved session state.
    if os.path.exists(SESSION_FILE):
        print(f"Loading session from '{SESSION_FILE}'...")
        context = await browser.new_context(storage_state=SESSION_FILE)
        page = await context.new_page()
        await page.goto(LOGIN_URL, wait_until="networkidle")

        # 2. Check if the session is still valid by looking for the dashboard element.
        try:
            await page.wait_for_selector(DASHBOARD_SELECTOR, timeout=5000)
            print("Session is valid. Skipping login.")
            await page.close()
            return context  # Return the valid, logged-in context
        except Exception:
            print("Session is expired or invalid. Performing a new login.")
            await context.close()  # Close the invalid context.

    # 3. If no valid session exists, perform a new login.
    print("No valid session found. A new login is required.")
    context = await browser.new_context()
    await _perform_login(context)
    return context


async def main_test():
    """A simple test function to run authentication directly."""
    print("--- Testing auth.py directly ---")
    async with async_playwright() as playwright:
        context = None
        try:
            context = await get_authenticated_context(playwright)
            print("\n[SUCCESS] auth.py test complete. Session file should be created/updated.")
            # Keep browser open for a moment to observe if needed
            await asyncio.sleep(3)
        except Exception as e:
            print(f"\n[ERROR] auth.py test failed: {e}")
        finally:
            if context:
                await context.browser.close()
                print("Browser closed.")
    print("--- Finished auth.py test ---")


if __name__ == "__main__":
    # This block allows you to run `python auth.py` directly to test authentication.
    # It will create or update `session.json` in your project folder.
    asyncio.run(main_test())