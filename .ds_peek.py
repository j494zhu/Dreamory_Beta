from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pg = [x for x in b.contexts[0].pages if "deepseek" in x.url][0]
    md = pg.query_selector_all(".ds-markdown")
    print("ds-markdown count:", len(md))
    if md:
        print("LAST REPLY:", repr(md[-1].inner_text()[:200]))
    ta = pg.query_selector("textarea")
    print("textarea value:", repr(ta.input_value()[:120]) if ta else "no ta")
    # any stop/generating button?
    body = pg.inner_text("body")
    print("has '停止'/'Stop' near:", ("停止" in body) or ("Stop" in body))
    b.close()
