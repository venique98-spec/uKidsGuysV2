# app_fixed.py
import time
import random
from datetime import datetime

import pandas as pd
import streamlit as st

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

try:
    import gspread
    from gspread.exceptions import APIError, WorksheetNotFound
except Exception:
    gspread = None

    class APIError(Exception):
        ...

    class WorksheetNotFound(Exception):
        ...


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="uKids Guys Availability Form",
    page_icon="🗓️",
    layout="centered",
)

# ---------------------------------------------------------------------------
# THEME
# Palette pulled directly from the uKids logo:
#   cream background #FFFAE7   teal #4FB8C9   purple #9B4F98
#   orange #C1502E   yellow #F6D24A
# ---------------------------------------------------------------------------

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:wght@400;600;700;800&display=swap');

:root{
  --cream:        #FFFAE7;
  --cream-soft:   #FFF6DA;
  --ink:          #3B2E2A;
  --teal:         #4FB8C9;
  --teal-dark:    #2E8FA0;
  --purple:       #9B4F98;
  --purple-dark:  #7A3B79;
  --orange:       #C1502E;
  --orange-dark:  #A23F22;
  --yellow:       #F6D24A;
  --yellow-dark:  #E0B520;
  --card-shadow:  0 6px 0 rgba(59,46,42,0.08), 0 10px 24px rgba(59,46,42,0.07);
}

/* ---------- base canvas ---------- */
.stApp{
  background:
    radial-gradient(circle at 8% 12%, rgba(79,184,201,0.10) 0, transparent 38%),
    radial-gradient(circle at 92% 18%, rgba(155,79,152,0.10) 0, transparent 40%),
    radial-gradient(circle at 50% 95%, rgba(246,210,74,0.12) 0, transparent 45%),
    var(--cream);
}

html, body, [class*="css"]{
  font-family: 'Nunito', sans-serif;
  color: var(--ink);
}

.block-container{
  padding-top: 1.2rem;
  max-width: 720px;
}

/* ---------- confetti header banner ---------- */
.ukids-confetti-top{
  height: 14px;
  width: 100%;
  border-radius: 999px;
  margin-bottom: 22px;
  background: repeating-linear-gradient(
    90deg,
    var(--teal) 0 26px,
    transparent 26px 36px,
    var(--orange) 36px 62px,
    transparent 62px 72px,
    var(--purple) 72px 98px,
    transparent 98px 108px,
    var(--yellow) 108px 134px,
    transparent 134px 144px
  );
  opacity: 0.85;
}

.ukids-hero{
  text-align: center;
  margin-bottom: 6px;
  position: relative;
}

.ukids-hero-emoji-row{
  font-size: 1.4rem;
  letter-spacing: 18px;
  margin-bottom: 2px;
  opacity: 0.9;
}

.ukids-title{
  font-family: 'Baloo 2', sans-serif;
  font-weight: 800;
  font-size: 2.5rem;
  line-height: 1.05;
  margin: 0;
  letter-spacing: 0.5px;
}
.ukids-title .u1{ color: var(--teal-dark); }
.ukids-title .u2{ color: var(--purple); }
.ukids-title .u3{ color: var(--orange); }
.ukids-title .u4{ color: var(--yellow-dark); }
.ukids-title .u5{ color: var(--teal-dark); }

.ukids-subtitle{
  font-family: 'Baloo 2', sans-serif;
  font-weight: 600;
  font-size: 1.18rem;
  color: var(--ink);
  margin-top: 2px;
  opacity: 0.85;
}

.ukids-tagline{
  font-size: 0.95rem;
  color: var(--ink);
  opacity: 0.62;
  margin-top: 6px;
  margin-bottom: 18px;
}

/* ---------- generic "hand drawn" card ---------- */
.ukids-card{
  background: #FFFFFF;
  border: 2.5px solid var(--ink);
  border-radius: 22px;
  padding: 22px 24px;
  margin: 18px 0;
  box-shadow: var(--card-shadow);
  position: relative;
}

.ukids-card.teal-edge{ border-color: var(--teal-dark); }
.ukids-card.purple-edge{ border-color: var(--purple); }
.ukids-card.orange-edge{ border-color: var(--orange); }
.ukids-card.yellow-edge{ border-color: var(--yellow-dark); }

.ukids-card-title{
  font-family: 'Baloo 2', sans-serif;
  font-weight: 700;
  font-size: 1.18rem;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ukids-pill{
  display:inline-block;
  font-family: 'Baloo 2', sans-serif;
  font-weight: 700;
  font-size: 0.78rem;
  padding: 3px 12px;
  border-radius: 999px;
  color: white;
  letter-spacing: 0.3px;
}
.pill-teal{ background: var(--teal-dark); }
.pill-purple{ background: var(--purple); }
.pill-orange{ background: var(--orange); }
.pill-yellow{ background: var(--yellow-dark); color: var(--ink); }

/* ---------- countdown banner ---------- */
.ukids-countdown{
  background: linear-gradient(135deg, #FFF1C2 0%, #FFE9A8 100%);
  border: 2.5px dashed var(--yellow-dark);
  border-radius: 20px;
  padding: 16px 20px;
  margin: 16px 0 20px 0;
  font-size: 0.96rem;
}
.ukids-countdown b{ color: var(--orange-dark); }
.ukids-countdown-time{
  font-family: 'Baloo 2', sans-serif;
  font-weight: 800;
  font-size: 1.3rem;
  color: var(--orange-dark);
}

/* ---------- login card ---------- */
.ukids-login-wrap{
  max-width: 420px;
  margin: 30px auto 0 auto;
}

/* ---------- streamlit widget restyles ---------- */

/* buttons */
.stButton > button{
  width: 100%;
  height: 48px;
  font-family: 'Baloo 2', sans-serif;
  font-weight: 700;
  font-size: 16px;
  border-radius: 14px;
  border: 2.5px solid var(--ink);
  background: var(--teal);
  color: var(--ink);
  box-shadow: 0 4px 0 var(--ink);
  transition: transform 0.05s ease, box-shadow 0.05s ease;
}
.stButton > button:hover{
  background: var(--teal-dark);
  color: white;
  border-color: var(--ink);
}
.stButton > button:active{
  transform: translateY(3px);
  box-shadow: 0 1px 0 var(--ink);
}

/* primary submit button gets the orange treatment via key targeting below */
div[data-testid="stVerticalBlock"] .ukids-submit-zone .stButton > button{
  background: var(--orange);
  color: white;
  font-size: 18px;
  height: 56px;
  box-shadow: 0 5px 0 var(--orange-dark);
}
div[data-testid="stVerticalBlock"] .ukids-submit-zone .stButton > button:hover{
  background: var(--orange-dark);
}

/* text inputs */
.stTextInput > div > div > input{
  border-radius: 12px;
  border: 2px solid #E4D9B8;
  padding: 10px 14px;
  font-family: 'Nunito', sans-serif;
}
.stTextInput > div > div > input:focus{
  border-color: var(--teal-dark);
  box-shadow: 0 0 0 2px rgba(79,184,201,0.25);
}
.stTextInput label{
  font-weight: 700;
  color: var(--ink);
}

/* checkboxes -> chunky pill chips */
.stCheckbox{
  background: var(--cream-soft);
  border: 2px solid #EADFB9;
  border-radius: 14px;
  padding: 10px 14px;
  margin-bottom: 8px;
  transition: border-color 0.12s ease, background 0.12s ease;
}
.stCheckbox:hover{
  border-color: var(--teal);
}
.stCheckbox label p{
  font-weight: 700;
  font-size: 0.95rem;
}
.stCheckbox input:checked ~ span{
  background-color: var(--teal-dark) !important;
  border-color: var(--teal-dark) !important;
}

/* alerts */
div[data-testid="stAlert"]{
  border-radius: 16px;
  border: 2px solid rgba(0,0,0,0.06);
}

/* metrics */
div[data-testid="stMetric"]{
  background: var(--cream-soft);
  border: 2px solid #EADFB9;
  border-radius: 16px;
  padding: 12px 10px 6px 10px;
  text-align: center;
}
div[data-testid="stMetricLabel"]{
  font-family: 'Baloo 2', sans-serif;
  font-weight: 700;
  justify-content: center;
}
div[data-testid="stMetricValue"]{
  color: var(--purple);
  font-weight: 800;
}

/* expander (admin) */
div[data-testid="stExpander"]{
  border-radius: 16px;
  border: 2px solid #EADFB9;
  background: #FFFDF6;
}
summary{
  font-family: 'Baloo 2', sans-serif;
  font-weight: 700;
}

/* dataframes */
div[data-testid="stDataFrame"]{
  border-radius: 14px;
  overflow: hidden;
  border: 2px solid #EADFB9;
}

/* dividers -> dotted confetti rule instead of plain line */
hr{
  border: none;
  height: 6px;
  margin: 22px 0;
  background: repeating-linear-gradient(
    90deg,
    var(--purple) 0 8px,
    transparent 8px 16px,
    var(--teal) 16px 24px,
    transparent 24px 32px,
    var(--yellow-dark) 32px 40px,
    transparent 40px 48px
  );
  opacity: 0.55;
  border-radius: 999px;
}

/* sticky submit bar */
.sticky-submit{
  position: sticky;
  bottom: 0;
  z-index: 999;
  background: linear-gradient(180deg, rgba(255,250,231,0) 0%, var(--cream) 35%);
  padding: 14px 0 8px 0;
}

/* mobile column stacking, preserved from original */
@media (max-width: 520px){
  div[data-testid="column"] { width: 100% !important; flex: 0 0 100% !important; }
  .ukids-title{ font-size: 1.9rem; }
}

/* small footer note */
.ukids-footer{
  text-align:center;
  font-size: 0.78rem;
  opacity: 0.45;
  margin-top: 30px;
  margin-bottom: 6px;
}

</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header / hero
# ---------------------------------------------------------------------------

st.markdown('<div class="ukids-confetti-top"></div>', unsafe_allow_html=True)

st.markdown(
    """
<div class="ukids-hero">
  <div class="ukids-hero-emoji-row">🧡💛💜💙</div>
  <h1 class="ukids-title">
    <span class="u1">u</span><span class="u2">K</span><span class="u3">i</span><span class="u4">d</span><span class="u5">s</span>
  </h1>
  <div class="ukids-subtitle">Guys Availability Form</div>
  <div class="ukids-tagline">Tell us when you're free to serve next month 🙌</div>
</div>
""",
    unsafe_allow_html=True,
)

TAB_RESPONSES = "uKids Guys responses"
TAB_FINAL_RESPONSES = "Final Guys Responses"
TAB_SB = "uKids Guys SB"
TAB_DEADLINES = "Guys Deadlines"
TAB_DATES = "Kids & Guys ServiceDates"


def _get_secret_any(*paths):
    try:
        cur = st.secrets
    except Exception:
        return None

    for path in paths:
        c = cur
        ok = True
        for k in path:
            if k in c:
                c = c[k]
            else:
                ok = False
                break
        if ok:
            return c
    return None


def get_admin_key():
    v = _get_secret_any(["ADMIN_KEY"], ["general", "ADMIN_KEY"])
    return str(v) if v else ""


ADMIN_KEY = get_admin_key()


def is_sheets_enabled():
    if gspread is None:
        return False
    sa = _get_secret_any(["gcp_service_account"], ["general", "gcp_service_account"])
    sid = _get_secret_any(["GSHEET_ID"], ["general", "GSHEET_ID"])
    return bool(sa and sid)


if not is_sheets_enabled():
    st.error("Google Sheets is not configured. Add GSHEET_ID and [gcp_service_account] to Secrets.")
    st.stop()


def gs_retry(func, *args, **kwargs):
    for attempt in range(5):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status in (429, 500, 502, 503):
                time.sleep(min(10, (2**attempt) + random.random()))
                continue
            raise


@st.cache_resource
def get_spreadsheet():
    sa = _get_secret_any(["gcp_service_account"], ["general", "gcp_service_account"])
    sheet_id = _get_secret_any(["GSHEET_ID"], ["general", "GSHEET_ID"])

    sa = dict(sa)
    pk = sa.get("private_key", "")
    if isinstance(pk, str):
        pk = pk.replace("\\n", "\n").strip()
        if not pk.endswith("\n"):
            pk += "\n"
        sa["private_key"] = pk

    gc = gspread.service_account_from_dict(sa)
    return gs_retry(gc.open_by_key, sheet_id)


def ensure_worksheet(sh, title, rows=2000, cols=50):
    try:
        return sh.worksheet(title)
    except WorksheetNotFound:
        return sh.add_worksheet(title=title, rows=rows, cols=cols)


def ws_get_df(ws):
    values = gs_retry(ws.get_all_values)
    if not values:
        return pd.DataFrame()

    header, rows = values[0], values[1:]
    if not header:
        return pd.DataFrame()

    return pd.DataFrame(rows, columns=header)


def ws_ensure_header(ws, desired_header):
    header = gs_retry(ws.row_values, 1)
    if not header:
        gs_retry(ws.update, "1:1", [desired_header])
        return desired_header

    missing = [c for c in desired_header if c not in header]
    if missing:
        header = header + missing
        gs_retry(ws.update, "1:1", [header])
    return header


@st.cache_data(ttl=30, show_spinner=False)
def fetch_sb_df():
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_SB, rows=4000, cols=20)
    return ws_get_df(ws)


@st.cache_data(ttl=30, show_spinner=False)
def fetch_deadlines_df():
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_DEADLINES, rows=500, cols=10)
    return ws_get_df(ws)


@st.cache_data(ttl=30, show_spinner=False)
def fetch_service_dates_df():
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_DATES, rows=4000, cols=10)
    return ws_get_df(ws)


@st.cache_data(ttl=30, show_spinner=False)
def fetch_responses_df():
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_RESPONSES, rows=8000, cols=250)
    return ws_get_df(ws)


def append_response_row(desired_header, row_map):
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_RESPONSES, rows=8000, cols=max(250, len(desired_header) + 10))
    header = ws_ensure_header(ws, desired_header)
    row = [row_map.get(col, "") for col in header]
    gs_retry(ws.append_row, row)


def replace_final_guys_responses_tab(final_df):
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_FINAL_RESPONSES, rows=8000, cols=10)

    header = ["timestamp", "Service", "Name"]
    rows = final_df.values.tolist() if not final_df.empty else []

    gs_retry(ws.clear)
    gs_retry(ws.update, "A1", [header] + rows)


def clear_caches():
    try:
        st.cache_data.clear()
    except Exception:
        pass


def get_now_in_tz(tz_name):
    if ZoneInfo is None:
        return datetime.utcnow()
    return datetime.now(ZoneInfo(tz_name))


def add_one_month(dt):
    y, m = dt.year, dt.month
    if m == 12:
        return datetime(y + 1, 1, 1, tzinfo=dt.tzinfo)
    return datetime(y, m + 1, 1, tzinfo=dt.tzinfo)


def get_target_month_key(now_local):
    return add_one_month(now_local).strftime("%Y-%m")


def parse_deadline_local(deadline_local, tz_name):
    dt_naive = datetime.strptime(deadline_local, "%Y-%m-%d %H:%M")
    if ZoneInfo is None:
        return dt_naive
    return dt_naive.replace(tzinfo=ZoneInfo(tz_name))


def format_minutes_remaining(delta_seconds):
    mins = max(0, int(delta_seconds // 60))
    hrs = mins // 60
    rem_m = mins % 60
    return f"{hrs}h {rem_m}m" if hrs else f"{rem_m}m"


def _safe_parse_date_ymd(s):
    try:
        return datetime.strptime(str(s).strip(), "%Y-%m-%d")
    except Exception:
        return datetime(1900, 1, 1)


def _is_truthy(v):
    return str(v).strip().lower() in ("1", "true", "yes", "y", "t")


def _display_date_only(label):
    s = str(label).strip()
    s = s.replace("Morning Service", "").replace("Evening Service", "")
    s = s.replace("Morning", "").replace("Evening", "")
    s = s.replace("Service", "")
    return " ".join(s.split()).strip(" -")


def _build_display_map(labels):
    display_map = {}
    used = set()

    for lbl in labels:
        base = _display_date_only(lbl)
        disp = base
        i = 2
        while disp in used:
            disp = f"{base} ({i})"
            i += 1
        used.add(disp)
        display_map[disp] = lbl

    return display_map


def build_final_guys_df(responses_df):
    if responses_df is None or responses_df.empty:
        return pd.DataFrame(columns=["timestamp", "Service", "Name"])

    df = responses_df.copy()

    for col in ["timestamp", "Serving Guy"]:
        if col not in df.columns:
            df[col] = ""

    meta_cols = {
        "timestamp",
        "Availability month",
        "Serving Guy",
        "Director",
        "Serving Girl",
        "Name",
        "Service",
    }

    service_cols = [c for c in df.columns if c not in meta_cols]

    rows = []
    for _, row in df.iterrows():
        ts = str(row.get("timestamp", "")).strip()
        name = str(row.get("Serving Guy", "")).strip()

        if not name:
            continue

        for service in service_cols:
            if str(row.get(service, "")).strip().lower() == "yes":
                rows.append({"timestamp": ts, "Service": service, "Name": name})

    return pd.DataFrame(rows, columns=["timestamp", "Service", "Name"])


def auto_update_final_sheet():
    try:
        responses_df = fetch_responses_df()
        final_df = build_final_guys_df(responses_df)
        replace_final_guys_responses_tab(final_df)
        clear_caches()
        return True, len(final_df), ""
    except Exception as e:
        return False, 0, str(e)


def login_user(sb_df, username, password):
    df = sb_df.copy()

    required = {"Name", "Username", "Password", "Active"}
    missing = required - set(df.columns)
    if missing:
        return None, f"uKids Guys SB is missing columns: {', '.join(sorted(missing))}"

    df["Name"] = df["Name"].astype(str).str.strip()
    df["Username"] = df["Username"].astype(str).str.strip()
    df["Password"] = df["Password"].astype(str).str.strip()
    df["Active"] = df["Active"].astype(str).str.strip().str.lower()

    match = df[
        (df["Username"].str.lower() == str(username).strip().lower())
        & (df["Password"] == str(password).strip())
        & (df["Active"].isin(["true", "yes", "1", "active"]))
    ]

    if match.empty:
        return None, "Incorrect username/password, or user is inactive."

    row = match.iloc[0]
    return {"name": row["Name"], "username": row["Username"]}, ""


try:
    sb_df = fetch_sb_df()
    deadlines_df = fetch_deadlines_df()
    service_dates_all = fetch_service_dates_df()
except Exception as e:
    st.error(f"Failed to load Google Sheets: {e}")
    st.stop()


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "username" not in st.session_state:
    st.session_state.username = ""


if not st.session_state.logged_in:

    st.markdown('<div class="ukids-login-wrap">', unsafe_allow_html=True)

    st.markdown(
        """
    <div class="ukids-card teal-edge">
      <div class="ukids-card-title">🔑 Login</div>
    """,
        unsafe_allow_html=True,
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login_clicked = st.button("Login")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if login_clicked:
        user, err = login_user(sb_df, username, password)
        if err:
            st.error(err)
        else:
            st.session_state.logged_in = True
            st.session_state.user_name = user["name"]
            st.session_state.username = user["username"]
            st.rerun()

    st.markdown(
        '<div class="ukids-footer">uKids · Guys Team Scheduling 💙</div>',
        unsafe_allow_html=True,
    )

    st.stop()


st.markdown(
    f"""
<div class="ukids-card purple-edge" style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
  <div>
    <span class="ukids-pill pill-purple">👋 Welcome</span>
    <div style="font-family:'Baloo 2',sans-serif; font-weight:800; font-size:1.25rem; margin-top:8px;">
      {st.session_state.user_name}
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.username = ""
    st.rerun()


for df, name, needed in [
    (deadlines_df, TAB_DEADLINES, {"month", "deadline_local", "timezone"}),
    (service_dates_all, TAB_DATES, {"target_month", "date", "label", "is_service_day"}),
]:
    missing = needed - set(df.columns)
    if missing:
        st.error(f"Google Sheet tab '{name}' is missing columns: {', '.join(sorted(missing))}")
        st.stop()


deadlines_df["month"] = deadlines_df["month"].astype(str).str.strip()
deadlines_df["deadline_local"] = deadlines_df["deadline_local"].astype(str).str.strip()
deadlines_df["timezone"] = deadlines_df["timezone"].astype(str).str.strip()

service_dates_all["target_month"] = service_dates_all["target_month"].astype(str).str.strip()
service_dates_all["date"] = service_dates_all["date"].astype(str).str.strip()
service_dates_all["label"] = service_dates_all["label"].astype(str).str.strip()
service_dates_all["is_service_day"] = service_dates_all["is_service_day"].astype(str).str.strip()

BASE_TZ = "Africa/Johannesburg"
if not deadlines_df.empty:
    tz0 = str(deadlines_df["timezone"].iloc[0]).strip()
    if tz0:
        BASE_TZ = tz0

now_base = get_now_in_tz(BASE_TZ)
target_month_key = get_target_month_key(now_base)

month_dates = service_dates_all[
    (service_dates_all["target_month"] == target_month_key)
    & (service_dates_all["is_service_day"].map(_is_truthy))
].copy()

if month_dates.empty:
    st.markdown(
        f"""
<div class="ukids-card yellow-edge" style="text-align:center;">
  <div style="font-size:2.4rem;">🔒</div>
  <div class="ukids-card-title" style="justify-content:center;">This month's availability form is not open yet</div>
  <div>No service dates found for <b>{target_month_key}</b>.</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.stop()

month_dates["_sort"] = month_dates["date"].map(_safe_parse_date_ymd)
month_dates = month_dates.sort_values("_sort").drop(columns=["_sort"])

date_labels = month_dates["label"].astype(str).tolist()
morning_labels = [l for l in date_labels if "morning" in l.lower()]
evening_labels = [l for l in date_labels if "evening" in l.lower()]

morning_display_map = _build_display_map(morning_labels)
evening_display_map = _build_display_map(evening_labels)

morning_options = list(morning_display_map.keys())
evening_options = list(evening_display_map.keys())


def get_deadline_for_target_month(deadlines, month_key):
    match = deadlines[deadlines["month"] == month_key]
    if match.empty:
        return None, BASE_TZ

    row = match.iloc[0]
    tz_name = str(row["timezone"]).strip() or BASE_TZ
    dl = parse_deadline_local(str(row["deadline_local"]).strip(), tz_name)
    return dl, tz_name


deadline_dt, deadline_tz = get_deadline_for_target_month(deadlines_df, target_month_key)

is_closed = True
if deadline_dt is not None:
    now_local = get_now_in_tz(deadline_tz)
    is_closed = (deadline_dt - now_local).total_seconds() <= 0

if is_closed:
    ok, rows_written, err = auto_update_final_sheet()
    if ok:
        st.success(f"Final Guys Responses updated automatically with {rows_written} row(s).")
    else:
        st.warning(f"Final Guys Responses could not update automatically: {err}")

    target_month_name = datetime.strptime(target_month_key, "%Y-%m").strftime("%B")
    st.markdown(
        f"""
<div class="ukids-card orange-edge" style="text-align:center;">
  <div style="font-size:2.4rem;">🔒</div>
  <div class="ukids-card-title" style="justify-content:center;">{target_month_name} availability submissions are now closed</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.stop()


now_local = get_now_in_tz(deadline_tz)
remaining_seconds = (deadline_dt - now_local).total_seconds()

st.markdown(
    f"""
<div class="ukids-countdown">
  🗓️ Submitting availability for <b>{target_month_key}</b><br><br>
  ⏳ Form closes at <b>{deadline_dt.strftime('%Y-%m-%d %H:%M')}</b> ({deadline_tz})<br>
  <span class="ukids-countdown-time">{format_minutes_remaining(remaining_seconds)} remaining</span>
  <br><br>
  🔁 You can submit more than once — we'll use your most recent submission.
</div>
""",
    unsafe_allow_html=True,
)

if st.button("🔄 Refresh timer"):
    st.rerun()


st.markdown(
    f"""
<div style="text-align:center; margin: 26px 0 4px 0;">
  <span class="ukids-pill pill-teal">📋 Availability for {target_month_key}</span>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="ukids-card teal-edge">', unsafe_allow_html=True)
st.markdown('<div class="ukids-card-title">☀️ Which morning services are you available?</div>', unsafe_allow_html=True)

m1, m2 = st.columns(2)

with m1:
    if st.button("✅ Select all mornings"):
        for opt in morning_options:
            st.session_state[f"morn_{target_month_key}_{opt}"] = True

with m2:
    if st.button("🧹 Clear mornings"):
        for opt in morning_options:
            st.session_state[f"morn_{target_month_key}_{opt}"] = False

morning_selected = []
for opt in morning_options:
    key = f"morn_{target_month_key}_{opt}"
    checked = st.checkbox(opt, key=key)
    if checked:
        morning_selected.append(opt)

st.markdown("</div>", unsafe_allow_html=True)


st.markdown('<div class="ukids-card purple-edge">', unsafe_allow_html=True)
st.markdown('<div class="ukids-card-title">🌙 Which evening services are you available?</div>', unsafe_allow_html=True)

e1, e2 = st.columns(2)

with e1:
    if st.button("✅ Select all evenings"):
        for opt in evening_options:
            st.session_state[f"eve_{target_month_key}_{opt}"] = True

with e2:
    if st.button("🧹 Clear evenings"):
        for opt in evening_options:
            st.session_state[f"eve_{target_month_key}_{opt}"] = False

evening_selected = []
for opt in evening_options:
    key = f"eve_{target_month_key}_{opt}"
    checked = st.checkbox(opt, key=key)
    if checked:
        evening_selected.append(opt)

st.markdown("</div>", unsafe_allow_html=True)


st.markdown('<div class="ukids-card yellow-edge">', unsafe_allow_html=True)
st.markdown('<div class="ukids-card-title">📝 Review</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Name", st.session_state.user_name)
with c2:
    st.metric("Morning selected", len(morning_selected))
with c3:
    st.metric("Evening selected", len(evening_selected))

st.markdown("</div>", unsafe_allow_html=True)


st.markdown('<div class="sticky-submit ukids-submit-zone">', unsafe_allow_html=True)
submitted = st.button("🎉 Submit my availability")
st.markdown("</div>", unsafe_allow_html=True)


if submitted:
    now_check = get_now_in_tz(deadline_tz)
    if (deadline_dt - now_check).total_seconds() <= 0:
        st.error("Form is closed.")
        st.stop()

    selected_morning_labels = {
        morning_display_map[d] for d in morning_selected if d in morning_display_map
    }
    selected_evening_labels = {
        evening_display_map[d] for d in evening_selected if d in evening_display_map
    }

    selected_all = selected_morning_labels.union(selected_evening_labels)
    yes_map = {lbl: ("Yes" if lbl in selected_all else "No") for lbl in date_labels}

    now = datetime.utcnow().isoformat() + "Z"

    row_map = {
        "timestamp": now,
        "Availability month": target_month_key,
        "Serving Guy": st.session_state.user_name,
    }

    row_map.update(yes_map)

    desired_header = ["timestamp", "Availability month", "Serving Guy"] + date_labels

    try:
        append_response_row(desired_header, row_map)
        clear_caches()
        st.success("🎉 Submission saved to Google Sheets. Thank you!")
        st.balloons()
    except Exception as e:
        st.error(f"Failed to save submission: {e}")


def compute_nonresponders_current_month(sb_df, responses_df, month_key):
    if sb_df is None or sb_df.empty or "Name" not in sb_df.columns:
        return pd.DataFrame(columns=["Serving Guy", "Status"])

    base = sb_df.copy()
    if "Active" in base.columns:
        base["Active"] = base["Active"].astype(str).str.strip().str.lower()
        base = base[base["Active"].isin(["true", "yes", "1", "active"])]

    base_names = sorted({str(x).strip() for x in base["Name"] if str(x).strip()})

    out_base = pd.DataFrame({"Serving Guy": base_names})

    if responses_df is None or responses_df.empty:
        out_base["Status"] = "Non-responder"
        return out_base

    df = responses_df.copy()
    for col in ["Availability month", "Serving Guy"]:
        if col not in df.columns:
            df[col] = ""

    df["Availability month"] = df["Availability month"].astype(str).str.strip()
    df["Serving Guy"] = df["Serving Guy"].astype(str).str.strip()

    df = df[df["Availability month"] == month_key]
    responded = set(df["Serving Guy"].dropna().tolist())

    out = out_base[~out_base["Serving Guy"].isin(responded)].copy()
    out["Status"] = "Non-responder"

    return out.reset_index(drop=True)


st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)

with st.expander("⚙️ Admin"):
    st.caption("Mode: Google Sheets guys profile app")

    if not ADMIN_KEY:
        st.info("To protect exports, set an ADMIN_KEY in Streamlit Secrets.")

    key = st.text_input("Enter admin key", type="password")

    if ADMIN_KEY and key != ADMIN_KEY:
        if key:
            st.error("Incorrect admin key.")
    else:
        st.success("Admin unlocked.")

        try:
            responses_df = fetch_responses_df()
        except Exception as e:
            st.error(f"Could not load responses: {e}")
            responses_df = pd.DataFrame()

        st.write(f"Total submissions: **{len(responses_df)}**")

        if not responses_df.empty:
            st.dataframe(responses_df, use_container_width=True)

        st.divider()
        st.markdown("### 🔄 Build Final Guys Responses")

        final_preview_df = build_final_guys_df(responses_df)
        st.write(f"Rows that will be written: **{len(final_preview_df)}**")

        if not final_preview_df.empty:
            st.dataframe(final_preview_df, use_container_width=True)

        if st.button("Rebuild Final Guys Responses tab"):
            try:
                replace_final_guys_responses_tab(final_preview_df)
                clear_caches()
                st.success(f"Final Guys Responses rebuilt with {len(final_preview_df)} row(s).")
            except Exception as e:
                st.error(f"Failed to rebuild Final Guys Responses: {e}")

        st.divider()
        st.markdown("### ❌ Non-responders")

        nonresp_df = compute_nonresponders_current_month(sb_df, responses_df, target_month_key)
        st.write(f"Shown: **{len(nonresp_df)}**")
        st.dataframe(nonresp_df, use_container_width=True)

st.markdown(
    '<div class="ukids-footer">uKids · Guys Team Scheduling 💙</div>',
    unsafe_allow_html=True,
)
