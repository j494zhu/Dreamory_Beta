from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pg = [x for x in b.contexts[0].pages if "deepseek" in x.url][0]
    # textarea attributes
    ta = pg.query_selector("textarea")
    print("textarea id/class:", ta.get_attribute("id"), "|", ta.get_attribute("class"))
    # look for class names that hint at message/markdown containers
    classes = pg.eval_on_selector_all("*[class]", """els => {
        const m = {};
        for (const e of els){ for (const c of e.classList){
            if(/markdown|message|chat|msg|response|content/i.test(c)) m[c]=(m[c]||0)+1;
        }}
        return m;
    }""")
    print(json.dumps(classes, ensure_ascii=False, indent=1))
    b.close()
