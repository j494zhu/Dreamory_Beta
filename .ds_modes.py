from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pg = [x for x in b.contexts[0].pages if "deepseek" in x.url][0]
    items = pg.eval_on_selector_all("*", """els => {
        const out=[];
        for(const e of els){
            const t=(e.textContent||'').trim();
            if(e.children.length===0 && /^(Instant|Expert|DeepThink|Search)$/i.test(t)){
                let cur=e, chain=[];
                for(let i=0;i<4 && cur;i++){chain.push(cur.className||cur.tagName); cur=cur.parentElement;}
                out.push({t, chain});
            }
        }
        return out;
    }""")
    for it in items:
        print(it)
    b.close()
