"""Send one message to DeepSeek web chat (CDP-attached browser), wait for the full
reply, log both to a transcript, and print the reply.

Usage: python .ds_send.py <message_file> [speaker_label]
"""
import sys
import time
import datetime
from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"
REPLY_SEL = ".ds-markdown"
STABLE_SECS = 3.0
MAX_WAIT = 240.0
TRANSCRIPT = "C:\\code\\python\\Dreamory_beta\\.ds_transcript.md"


def get_page(b):
    for ctx in b.contexts:
        for pg in ctx.pages:
            if "deepseek" in pg.url:
                return pg
    raise SystemExit("No DeepSeek page found.")


def log(role, text):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    with open(TRANSCRIPT, "a", encoding="utf-8") as f:
        f.write(f"\n**{role}** ({ts}):\n{text}\n")


def main():
    msg = open(sys.argv[1], encoding="utf-8").read().strip()
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(CDP)
        pg = get_page(b)

        def last_reply():
            els = pg.query_selector_all(REPLY_SEL)
            return els[-1].inner_text() if els else ""

        prev_last = last_reply()

        ta = pg.query_selector("textarea")
        ta.click()
        ta.fill(msg)
        pg.keyboard.press("Enter")
        log("陈舟(我)", msg)

        # wait until a NEW reply starts rendering (last reply text changes)
        t0 = time.time()
        while time.time() - t0 < MAX_WAIT:
            cur = last_reply()
            if cur and cur != prev_last:
                break
            time.sleep(0.5)
        else:
            raise SystemExit("Timed out waiting for reply to start.")

        # stabilize on the new reply
        last_text = cur
        last_change = time.time()
        while time.time() - t0 < MAX_WAIT:
            cur = last_reply()
            if cur != last_text:
                last_text = cur
                last_change = time.time()
            elif cur and time.time() - last_change >= STABLE_SECS:
                break
            time.sleep(0.6)

        log("林晚(DeepSeek)", last_text)
        print(last_text)
        b.close()


if __name__ == "__main__":
    main()
