"""Dreamory 极简前端。运行:uv run streamlit run frontend/app.py
依赖后端:uv run main.py(默认 http://localhost:7234)"""
import requests
import streamlit as st

st.set_page_config(page_title="Dreamory", layout="wide")
ss = st.session_state
ss.setdefault("user_id", "")
ss.setdefault("chat_id", None)


def api_get(path: str):
    r = requests.get(f"{ss.api}{path}", timeout=180)
    r.raise_for_status()
    return r.json()


def api_post(path: str, body: dict | None = None):
    r = requests.post(f"{ss.api}{path}", json=body, timeout=180)
    r.raise_for_status()
    return r.json()


def api_put(path: str, body: dict | None = None):
    r = requests.put(f"{ss.api}{path}", json=body, timeout=180)
    r.raise_for_status()
    return r.json()


# ── 侧边栏:用户 + 对话列表 ──────────────────────────────────
with st.sidebar:
    st.header("🌙 Dreamory")
    ss.api = st.text_input("后端地址", "http://localhost:7234")
    ss.user_id = st.text_input("user_id", ss.user_id)

    c1, c2 = st.columns(2)
    if c1.button("新建用户", use_container_width=True):
        ss.user_id = api_post("/users/")["user_id"]
        ss.chat_id = None
        st.rerun()
    if c2.button("新建对话", use_container_width=True, disabled=not ss.user_id):
        ss.chat_id = api_post("/chats/", {"user_id": ss.user_id, "title": "新对话"})["chat_id"]
        st.rerun()

    st.divider()
    st.caption("对话列表")
    if ss.user_id:
        try:
            for ch in api_get(f"/users/{ss.user_id}/chats"):
                label = ch.get("title") or str(ch["chat_id"])[:8]
                if st.button(label, key=str(ch["chat_id"]), use_container_width=True):
                    ss.chat_id = ch["chat_id"]
                    st.rerun()
        except Exception as e:
            st.error(f"加载对话列表失败:{e}")


# ── 主区:对话 ───────────────────────────────────────────────
if not ss.chat_id:
    st.info("← 左侧新建用户 / 新建对话,或选择一个已有对话")
    st.stop()

chat = api_get(f"/chats/{ss.chat_id}")
st.subheader(chat.get("title") or "对话")

# ── 人设编辑(选预设 + 改名字/简介)─────────────────────────
try:
    presets = api_get("/chats/presets")
except Exception:
    presets = {}
persona = chat.get("persona") or {}
preset_keys = list(presets.keys())
_default = "anxious" if "anxious" in preset_keys else (preset_keys[0] if preset_keys else None)
cur_preset = persona.get("preset") if persona.get("preset") in preset_keys else _default

with st.expander(f"🎭 人设 · {persona.get('name') or '(未设置,默认 anxious)'}"):
    if not preset_keys:
        st.warning("加载预设失败,确认后端在运行")
    else:
        sel = st.selectbox(
            "预设人格", preset_keys,
            index=preset_keys.index(cur_preset),
            format_func=lambda k: f"{k}(anx={presets[k]['anxiety']} / avo={presets[k]['avoidance']} / expr={presets[k]['expressiveness']})",
            key=f"preset_{ss.chat_id}",
        )
        name = st.text_input("名字", value=persona.get("name", ""),
                             placeholder=presets[sel]["name"], key=f"pname_{ss.chat_id}")
        profile = st.text_area("简介 profile", value=persona.get("profile", ""),
                               placeholder=presets[sel]["profile"], key=f"pprofile_{ss.chat_id}")
        st.caption("名字/简介留空则用所选预设的默认值。")
        if st.button("保存人设", use_container_width=True):
            api_put(f"/chats/{ss.chat_id}/persona",
                    {"preset": sel, "name": name or None, "profile": profile or None})
            st.success("已保存,下一条消息生效")
            st.rerun()

for m in chat["messages"]:
    if m["role"] == "system":
        continue
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

if prompt := st.chat_input("说点什么…"):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("思考中…"):
            res = api_post(f"/chats/{ss.chat_id}/messages", {"content": prompt})
        st.markdown(res["content"])
        dbg = res.get("debug")
        if dbg:
            with st.expander(f"🧠 内心 · mode = {dbg.get('mode')}"):
                st.markdown(f"**内心独白**\n\n{dbg.get('thinking') or '(无)'}")
                st.write("**标量**", dbg.get("scalars"))
                st.write("**trace**", dbg.get("trace"))
                if dbg.get("open_loops"):
                    st.write("**挂起回路**", dbg.get("open_loops"))
                if dbg.get("grievances"):
                    st.write("**旧账**", dbg.get("grievances"))
    st.rerun()
