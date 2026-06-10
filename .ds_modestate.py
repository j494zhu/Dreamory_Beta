from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pg = [x for x in b.contexts[0].pages if "deepseek" in x.url][0]
    state = pg.evaluate("""() => {
        const res={toggles:[], segs:[]};
        document.querySelectorAll('.ds-toggle-button').forEach(t=>{
            res.toggles.push({txt:(t.innerText||'').trim(), cls:t.className, pressed:t.getAttribute('aria-pressed')});
        });
        // segmented options: leaf elements Instant/Expert -> climb to clickable seg
        document.querySelectorAll('*').forEach(e=>{
            const t=(e.textContent||'').trim();
            if(e.children.length===0 && /^(Instant|Expert)$/.test(t)){
                const seg=e.parentElement && e.parentElement.parentElement;
                if(seg) res.segs.push({txt:t, cls:seg.className});
            }
        });
        return res;
    }""")
    print("TOGGLES:")
    for x in state["toggles"]: print(" ", x)
    print("SEGS:")
    for x in state["segs"]: print(" ", x)
    b.close()
