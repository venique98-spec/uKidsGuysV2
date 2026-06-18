# app_fixed.py
# uKids Guys Availability Form
# - Login/profile-based
# - Uses uKids Guys SB: Name | Username | Password | Active
# - Deadlines from Guys Deadlines
# - Service dates from Kids & Guys ServiceDates
# - Raw responses to uKids Guys responses
# - Final long-format responses to Final Guys Responses
# - Styled like the uKids Kids Availability app

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
        pass

    class WorksheetNotFound(Exception):
        pass


# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
TAB_RESPONSES = "uKids Guys responses"
TAB_FINAL_RESPONSES = "Final Guys Responses"
TAB_SB = "uKids Guys SB"
TAB_DEADLINES = "Guys Deadlines"
TAB_DATES = "Kids & Guys ServiceDates"

TEAL = "#5BC4C0"
ORANGE = "#E8724A"
PURPLE = "#7B4FA6"
YELLOW = "#F5C842"
CREAM = "#FAF6EE"
WHITE = "#FFFFFF"
DARK = "#2A2A2A"
MUTED = "#7A6F6F"


# ─────────────────────────────────────────────────────────────
# Page config & CSS
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="uKids Guys Availability", page_icon="🗓️", layout="centered")

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Nunito', sans-serif;
  }}

  :root {{
    --teal:{TEAL};
    --orange:{ORANGE};
    --purple:{PURPLE};
    --yellow:{YELLOW};
    --cream:{CREAM};
    --white:{WHITE};
    --dark:{DARK};
    --muted:{MUTED};
  }}

  .stApp {{
    background:var(--cream);
  }}

  section[data-testid="stSidebar"] {{
    display:none;
  }}

  .block-container {{
    padding-top: 1.5rem;
    max-width: 720px;
  }}

  .ukids-hero {{
    background:var(--teal);
    border-radius:20px;
    padding:34px 28px 28px;
    margin-bottom:28px;
    text-align:center;
    position:relative;
    overflow:hidden;
  }}

  .ukids-hero::before {{
    content:'';
    position:absolute;
    top:-40px;
    right:-40px;
    width:160px;
    height:160px;
    background:var(--orange);
    border-radius:50%;
    opacity:0.28;
  }}

  .ukids-hero::after {{
    content:'';
    position:absolute;
    bottom:-30px;
    left:-30px;
    width:110px;
    height:110px;
    background:var(--purple);
    border-radius:50%;
    opacity:0.22;
  }}

  .ukids-hero-content {{
    position:relative;
    z-index:2;
  }}

  .ukids-hero h1 {{
    font-size:2rem;
    font-weight:900;
    color:var(--white);
    margin:0 0 6px;
    letter-spacing:-0.5px;
    text-shadow:0 2px 8px rgba(0,0,0,0.15);
  }}

  .ukids-hero p {{
    font-size:1rem;
    color:var(--white);
    opacity:0.93;
    margin:0;
  }}

  .ukids-card {{
    background:var(--white);
    border-radius:14px;
    padding:20px 20px 16px;
    margin-bottom:16px;
    box-shadow:0 2px 8px rgba(0,0,0,0.06);
    border-top:4px solid var(--teal);
  }}

  .ukids-card-orange {{
    border-top-color:var(--orange);
  }}

  .ukids-card-purple {{
    border-top-color:var(--purple);
  }}

  .ukids-card-yellow {{
    border-top-color:var(--yellow);
  }}

  .ukids-card h3 {{
    font-size:1.05rem;
    font-weight:800;
    color:var(--dark);
    margin:0 0 12px;
    text-transform:uppercase;
    letter-spacing:0.04em;
  }}

  .info-banner {{
    background:linear-gradient(135deg, var(--purple) 0%, #9B6FC6 100%);
    border-radius:12px;
    padding:14px 18px;
    font-size:0.88rem;
    color:var(--white);
    margin-bottom:16px;
    line-height:1.75;
  }}

  .info-banner strong {{
    font-weight:800;
  }}

  .closed-banner {{
    background:linear-gradient(135deg, var(--purple) 0%, #9B6FC6 100%);
    border-radius:12px;
    padding:16px 18px;
    font-size:0.95rem;
    color:var(--white);
    margin-bottom:16px;
    line-height:1.7;
    text-align:center;
  }}

  .profile-banner {{
    background:#F7F5FF;
    border:1.5px solid #D6CCF0;
    border-radius:12px;
    padding:14px 16px;
    margin-bottom:16px;
  }}

  .profile-name {{
    font-size:1.12rem;
    font-weight:900;
    color:var(--purple);
  }}

  .profile-sub {{
    font-size:0.82rem;
    color:var(--muted);
    margin-top:2px;
  }}

  .section-pill {{
    display:inline-block;
    background:var(--yellow);
    color:var(--dark);
    font-size:0.7rem;
    font-weight:800;
    text-transform:uppercase;
    letter-spacing:0.08em;
    padding:3px 10px;
    border-radius:20px;
    margin-bottom:10px;
  }}

  .login-wrap {{
    max-width:430px;
    margin:0 auto;
  }}

  .sticky-submit {{
    position:sticky;
    bottom:0;
    z-index:999;
    background:var(--cream);
    padding:10px 0 4px;
    border-top:2px solid #EDE8DC;
  }}

  .stButton > button {{
    width:100%;
    height:52px;
    font-size:1.05rem;
    font-weight:800;
    border-radius:12px;
    background:var(--teal) !important;
    color:var(--white) !important;
    border:none !important;
    letter-spacing:0.02em;
    transition:background 0.2s, transform 0.1s;
  }}

  .stButton > button:hover {{
    background:#3AADA9 !important;
    transform:translateY(-1px);
  }}

  .stButton > button:active {{
    transform:translateY(0);
  }}

  .stTextInput > div > div > input {{
    border-radius:12px;
  }}

  .stCheckbox {{
    background:#FFF8F0;
    border:1.5px solid #FCDAB8;
    border-radius:12px;
    padding:10px 12px;
    margin-bottom:8px;
  }}

  div[data-testid="stMetric"] {{
    background:#F7F5FF;
    border:1.5px solid #D6CCF0;
    border-radius:12px;
    padding:12px;
  }}

  hr {{
    border-color:#EDE8DC;
    margin:10px 0;
  }}

  @media (max-width:520px) {{
    div[data-testid="column"] {{
      width:100% !important;
      flex:0 0 100% !important;
    }}

    .ukids-hero h1 {{
      font-size:1.55rem;
    }}
  }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ukids-hero">
  <div class="ukids-hero-content">
    <h1>uKids Guys Availability</h1>
    <p>Let us know which services you can serve next month.</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Secrets
# ─────────────────────────────────────────────────────────────
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


ADMIN_KEY = str(_get_secret_any(["ADMIN_KEY"], ["general", "ADMIN_KEY"]) or "")


def is_sheets_enabled() -> bool:
    if gspread is None:
        return False

    return bool(
        _get_secret_any(["gcp_service_account"], ["general", "gcp_service_account"])
        and _get_secret_any(["GSHEET_ID"], ["general", "GSHEET_ID"])
    )


if not is_sheets_enabled():
    st.error("Google Sheets is not configured. Add GSHEET_ID and [gcp_service_account] to Secrets.")
    st.stop()


# ─────────────────────────────────────────────────────────────
# Google Sheets
# ─────────────────────────────────────────────────────────────
def gs_retry(func, *args, **kwargs):
    for attempt in range(6):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status in (429, 500, 502, 503):
                time.sleep(min(15, (2 ** attempt) + random.random()))
                continue
            raise


@st.cache_resource
def get_spreadsheet():
    sa = _get_secret_any(["gcp_service_account"], ["general", "gcp_service_account"])
    sheet_id = _get_secret_any(["GSHEET_ID"], ["general", "GSHEET_ID"])

    if not sa or not sheet_id:
        raise RuntimeError("Missing GSHEET_ID or gcp_service_account in secrets.")

    sa = dict(sa)
    pk = sa.get("private_key", "")

    if isinstance(pk, str):
        pk = pk.replace("\\n", "\n").strip()
        if not pk.endswith("\n"):
            pk += "\n"
        sa["private_key"] = pk

    gc = gspread.service_account_from_dict(sa)
    return gs_retry(gc.open_by_key, sheet_id)


def ensure_worksheet(sh, title: str, rows: int = 2000, cols: int = 50):
    try:
        return sh.worksheet(title)
    except WorksheetNotFound:
        return sh.add_worksheet(title=title, rows=rows, cols=cols)


def make_unique_headers(header: list) -> list:
    counts = {}
    out = []

    for h in header:
        base = str(h).strip() or "Unnamed"
        counts[base] = counts.get(base, 0) + 1
        out.append(base if counts[base] == 1 else f"{base}_{counts[base]}")

    return out


def ws_get_values_and_df(ws):
    values = gs_retry(ws.get_all_values)

    if not values:
        return [], [], pd.DataFrame()

    header_raw = values[0]
    header_unique = make_unique_headers(header_raw)
    rows = values[1:]

    return header_raw, header_unique, pd.DataFrame(rows, columns=header_unique)


def ws_ensure_header(ws, desired_header: list) -> list:
    header = gs_retry(ws.row_values, 1)

    if not header:
        gs_retry(ws.update, "A1", [desired_header])
        return desired_header

    missing = [c for c in desired_header if c not in header]

    if missing:
        header = header + missing
        gs_retry(ws.update, "A1", [header])

    return header


@st.cache_data(ttl=30, show_spinner=False)
def fetch_sb_df():
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_SB, rows=4000, cols=20)
    _, _, df = ws_get_values_and_df(ws)
    return df


@st.cache_data(ttl=30, show_spinner=False)
def fetch_deadlines_df():
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_DEADLINES, rows=500, cols=10)
    _, _, df = ws_get_values_and_df(ws)
    return df


@st.cache_data(ttl=30, show_spinner=False)
def fetch_service_dates_df():
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_DATES, rows=4000, cols=20)
    _, _, df = ws_get_values_and_df(ws)
    return df


@st.cache_data(ttl=30, show_spinner=False)
def fetch_responses_df():
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_RESPONSES, rows=8000, cols=250)
    _, _, df = ws_get_values_and_df(ws)
    return df


def clear_caches():
    try:
        st.cache_data.clear()
    except Exception:
        pass


def append_response_row(desired_header: list, row_map: dict):
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_RESPONSES, rows=8000, cols=max(250, len(desired_header) + 10))

    header = ws_ensure_header(ws, desired_header)
    row = [row_map.get(col, "") for col in header]

    gs_retry(ws.append_row, row)


def replace_final_guys_responses_tab(final_df: pd.DataFrame):
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_FINAL_RESPONSES, rows=8000, cols=10)

    header = ["timestamp", "Service", "Name"]
    rows = final_df.values.tolist() if not final_df.empty else []

    gs_retry(ws.clear)
    gs_retry(ws.update, "A1", [header] + rows)


# ─────────────────────────────────────────────────────────────
# Time helpers
# ─────────────────────────────────────────────────────────────
def get_now_in_tz(tz_name: str):
    if ZoneInfo:
        return datetime.now(ZoneInfo(tz_name))
    return datetime.utcnow()


def add_one_month(dt: datetime):
    y, m = dt.year, dt.month

    if m == 12:
        return datetime(y + 1, 1, 1, tzinfo=dt.tzinfo)

    return datetime(y, m + 1, 1, tzinfo=dt.tzinfo)


def get_target_month_key(now_local: datetime):
    return add_one_month(now_local).strftime("%Y-%m")


def parse_deadline_local(deadline_local: str, tz_name: str):
    dt_naive = datetime.strptime(deadline_local, "%Y-%m-%d %H:%M")

    if ZoneInfo:
        return dt_naive.replace(tzinfo=ZoneInfo(tz_name))

    return dt_naive


def format_minutes_remaining(delta_seconds: float):
    mins = max(0, int(delta_seconds // 60))
    hrs = mins // 60
    rem_m = mins % 60

    return f"{hrs}h {rem_m}m" if hrs else f"{rem_m}m"


# ─────────────────────────────────────────────────────────────
# Data helpers
# ─────────────────────────────────────────────────────────────
def _is_truthy(v):
    return str(v).strip().lower() in ("1", "true", "yes", "y", "t", "active")


def _safe_parse_date_ymd(s):
    try:
        return datetime.strptime(str(s).strip(), "%Y-%m-%d")
    except Exception:
        return datetime(1900, 1, 1)


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


def login_user(sb_df: pd.DataFrame, username: str, password: str):
    required = {"Name", "Username", "Password", "Active"}
    missing = required - set(sb_df.columns)

    if missing:
        return None, f"uKids Guys SB is missing columns: {', '.join(sorted(missing))}"

    df = sb_df.copy()
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


def build_final_guys_df(responses_df: pd.DataFrame, month_key: str):
    """
    Current month only.
    Latest submission per guy only.
    Output: timestamp | Service | Name
    """
    if responses_df is None or responses_df.empty:
        return pd.DataFrame(columns=["timestamp", "Service", "Name"])

    df = responses_df.copy()

    for col in ["timestamp", "Availability month", "Serving Guy"]:
        if col not in df.columns:
            df[col] = ""

    df["timestamp"] = df["timestamp"].astype(str).str.strip()
    df["Availability month"] = df["Availability month"].astype(str).str.strip()
    df["Serving Guy"] = df["Serving Guy"].astype(str).str.strip()

    df = df[df["Availability month"] == month_key].copy()

    if df.empty:
        return pd.DataFrame(columns=["timestamp", "Service", "Name"])

    df = df.sort_values("timestamp").drop_duplicates(subset=["Serving Guy"], keep="last")

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
                rows.append({
                    "timestamp": ts,
                    "Service": service,
                    "Name": name,
                })

    return pd.DataFrame(rows, columns=["timestamp", "Service", "Name"])


def auto_update_final_sheet(month_key: str):
    try:
        responses_df = fetch_responses_df()
        final_df = build_final_guys_df(responses_df, month_key)
        replace_final_guys_responses_tab(final_df)
        clear_caches()
        return True, len(final_df), ""
    except Exception as e:
        return False, 0, str(e)


def compute_nonresponders_current_month(sb_df: pd.DataFrame, responses_df: pd.DataFrame, month_key: str):
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


# ─────────────────────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────────────────────
try:
    sb_df = fetch_sb_df()
    deadlines_df = fetch_deadlines_df()
    service_dates_all = fetch_service_dates_df()
except Exception as e:
    st.error(f"Failed to load Google Sheets: {e}")
    st.stop()


# ─────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown("""
<div class="ukids-card">
  <span class="section-pill">Login</span>
  <h3>Access your profile</h3>
</div>
""", unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login_clicked = st.button("Login")

    if st.button("Forgot password?"):
        st.info("Please contact Veniqué to reset your password.")

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

    st.stop()


# ─────────────────────────────────────────────────────────────
# Validate tabs
# ─────────────────────────────────────────────────────────────
for df, name, needed in [
    (deadlines_df, TAB_DEADLINES, {"month", "deadline_local", "timezone"}),
    (service_dates_all, TAB_DATES, {"target_month", "date", "label", "is_service_day"}),
]:
    missing = needed - set(df.columns)

    if missing:
        st.error(f"Google Sheet tab '{name}' is missing columns: {', '.join(sorted(missing))}")
        st.stop()


# ─────────────────────────────────────────────────────────────
# Prepare month/date data
# ─────────────────────────────────────────────────────────────
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
    st.markdown(f"""
<div class="closed-banner">
  <strong>This month's availability form is not open yet.</strong><br><br>
  No service dates found for <strong>{target_month_key}</strong>.
</div>
""", unsafe_allow_html=True)
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


def get_deadline_for_target_month(deadlines: pd.DataFrame, month_key: str):
    match = deadlines[deadlines["month"] == month_key]

    if match.empty:
        return None, BASE_TZ

    row = match.iloc[0]
    tz_name = str(row["timezone"]).strip() or BASE_TZ
    deadline = parse_deadline_local(str(row["deadline_local"]).strip(), tz_name)

    return deadline, tz_name


deadline_dt, deadline_tz = get_deadline_for_target_month(deadlines_df, target_month_key)

is_closed = True
if deadline_dt is not None:
    now_local = get_now_in_tz(deadline_tz)
    is_closed = (deadline_dt - now_local).total_seconds() <= 0

if is_closed:
    ok, rows_written, err = auto_update_final_sheet(target_month_key)

    if ok:
        st.success(f"Final Guys Responses updated automatically with {rows_written} row(s).")
    else:
        st.warning(f"Final Guys Responses could not update automatically: {err}")

    target_month_name = datetime.strptime(target_month_key, "%Y-%m").strftime("%B")

    st.markdown(f"""
<div class="closed-banner">
  <strong>{target_month_name} availability submissions are now closed.</strong>
</div>
""", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="profile-banner">
  <div class="profile-name">Welcome, {st.session_state.user_name}</div>
  <div class="profile-sub">You are logged in as @{st.session_state.username}</div>
</div>
""", unsafe_allow_html=True)

if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_name = ""
    st.session_state.username = ""
    st.rerun()

now_local = get_now_in_tz(deadline_tz)
remaining_seconds = (deadline_dt - now_local).total_seconds()

st.markdown(f"""
<div class="info-banner">
  Submitting availability for <strong>{target_month_key}</strong><br>
  Form closes at <strong>{deadline_dt.strftime('%A %d %b, %H:%M')}</strong> ({deadline_tz})<br>
  Time remaining: <strong>{format_minutes_remaining(remaining_seconds)}</strong><br>
  You can submit more than once — we will use your most recent submission.
</div>
""", unsafe_allow_html=True)

if st.button("Refresh timer"):
    st.rerun()

st.markdown("""
<div class="ukids-card">
  <span class="section-pill">Step 1</span>
  <h3>Morning services</h3>
</div>
""", unsafe_allow_html=True)

m1, m2 = st.columns(2)

with m1:
    if st.button("Select all mornings"):
        for opt in morning_options:
            st.session_state[f"morn_{target_month_key}_{opt}"] = True

with m2:
    if st.button("Clear mornings"):
        for opt in morning_options:
            st.session_state[f"morn_{target_month_key}_{opt}"] = False

morning_selected = []

for opt in morning_options:
    key = f"morn_{target_month_key}_{opt}"
    if st.checkbox(opt, key=key):
        morning_selected.append(opt)


st.markdown("""
<div class="ukids-card ukids-card-purple">
  <span class="section-pill">Step 2</span>
  <h3>Evening services</h3>
</div>
""", unsafe_allow_html=True)

e1, e2 = st.columns(2)

with e1:
    if st.button("Select all evenings"):
        for opt in evening_options:
            st.session_state[f"eve_{target_month_key}_{opt}"] = True

with e2:
    if st.button("Clear evenings"):
        for opt in evening_options:
            st.session_state[f"eve_{target_month_key}_{opt}"] = False

evening_selected = []

for opt in evening_options:
    key = f"eve_{target_month_key}_{opt}"
    if st.checkbox(opt, key=key):
        evening_selected.append(opt)


st.markdown("""
<div class="ukids-card ukids-card-orange">
  <span class="section-pill">Review</span>
  <h3>Your selection</h3>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Name", st.session_state.user_name)
with c2:
    st.metric("Morning selected", len(morning_selected))
with c3:
    st.metric("Evening selected", len(evening_selected))


st.markdown('<div class="sticky-submit">', unsafe_allow_html=True)
submitted = st.button("Submit availability")
st.markdown("</div>", unsafe_allow_html=True)


if submitted:
    now_check = get_now_in_tz(deadline_tz)

    if (deadline_dt - now_check).total_seconds() <= 0:
        st.error("The form is closed.")
        st.stop()

    selected_morning_labels = {
        morning_display_map[d] for d in morning_selected if d in morning_display_map
    }

    selected_evening_labels = {
        evening_display_map[d] for d in evening_selected if d in evening_display_map
    }

    selected_all = selected_morning_labels.union(selected_evening_labels)

    yes_map = {
        lbl: ("Yes" if lbl in selected_all else "No")
        for lbl in date_labels
    }

    now_iso = datetime.utcnow().isoformat() + "Z"

    row_map = {
        "timestamp": now_iso,
        "Availability month": target_month_key,
        "Serving Guy": st.session_state.user_name,
    }

    row_map.update(yes_map)

    desired_header = ["timestamp", "Availability month", "Serving Guy"] + date_labels

    try:
        append_response_row(desired_header, row_map)
        clear_caches()
        st.success("Submitted. Your availability has been saved.")
        st.balloons()

    except Exception as e:
        st.error(f"Failed to save: {e}")


# ─────────────────────────────────────────────────────────────
# Admin
# ─────────────────────────────────────────────────────────────
st.markdown("---")

with st.expander("Admin"):
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
        st.markdown("### Build Final Guys Responses")

        final_preview_df = build_final_guys_df(responses_df, target_month_key)

        st.write(f"Rows that will be written for **{target_month_key}**: **{len(final_preview_df)}**")

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
        st.markdown("### Non-responders")

        nonresp_df = compute_nonresponders_current_month(sb_df, responses_df, target_month_key)

        st.write(f"Shown: **{len(nonresp_df)}**")
        st.dataframe(nonresp_df, use_container_width=True)
