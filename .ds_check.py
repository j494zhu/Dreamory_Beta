from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    pages = ctx.pages
    print("pages:", len(pages))
    for pg in pages:
        print("URL:", pg.url)
        print("TITLE:", pg.title())
    # report whether a chat textarea exists on the deepseek page
    ds = [pg for pg in pages if "deepseek" in pg.url]
    if ds:
        pg = ds[0]
        ta = pg.query_selector("textarea")
        print("textarea_present:", ta is not None)
        # heuristics for logged-in vs login screen
        body = pg.inner_text("body")[:500]
        print("BODY_SNIPPET:", repr(body))
    b.close()
