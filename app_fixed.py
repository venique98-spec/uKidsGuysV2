# app_fixed.py
# uKids Availability Form
# - Login/profile-based
# - Home menu with 3 sections
# - Uses uKids Guys SB: Name | Username | Password | Active
# - Deadlines from Guys Deadlines
# - Service dates from Kids & Guys ServiceDates
# - Raw responses to uKids Guys responses
# - Final long-format responses to Final Guys Responses
# - Schedule review from per-month tab (format: "Jul 25")
# - Change log to uKids Change Log tab

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
TAB_RESPONSES       = "uKids Guys responses"
TAB_FINAL_RESPONSES = "Final Guys Responses"
TAB_SB              = "uKids Guys SB"
TAB_DEADLINES       = "Guys Deadlines"
TAB_DATES           = "Kids & Guys ServiceDates"
TAB_CHANGE_LOG      = "uKids Change Log"
TAB_MAPPING         = "Mapping sheet"

TEAL   = "#5BC4C0"
ORANGE = "#E8724A"
PURPLE = "#7B4FA6"
YELLOW = "#F5C842"
CREAM  = "#FFFAE7"
WHITE  = "#FFFFFF"
DARK   = "#2A2A2A"
MUTED  = "#7A6F6F"


# ─────────────────────────────────────────────────────────────
# Page config & CSS
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="uKids Availability", page_icon="🗓️", layout="centered")

# Serve the logo from the repo root via Streamlit's static file support
import base64, pathlib

def _img_to_b64(path: str) -> str:
    try:
        data = pathlib.Path(path).read_bytes()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

_logo_b64 = _img_to_b64("uKids logo.png")
_logo_src  = f"data:image/png;base64,{_logo_b64}" if _logo_b64 else ""

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

  .stApp {{ background:var(--cream); }}

  section[data-testid="stSidebar"] {{ display:none; }}

  .block-container {{ padding-top:1.5rem; max-width:720px; }}

  /* ── Hero ── */
  .ukids-hero {{
    background:var(--teal);border-radius:20px;padding:34px 28px 28px;
    margin-bottom:28px;text-align:center;position:relative;overflow:hidden;
  }}
  .ukids-hero::before {{
    content:'';position:absolute;top:-40px;right:-40px;
    width:160px;height:160px;background:var(--orange);border-radius:50%;opacity:0.28;
  }}
  .ukids-hero::after {{
    content:'';position:absolute;bottom:-30px;left:-30px;
    width:110px;height:110px;background:var(--purple);border-radius:50%;opacity:0.22;
  }}
  .ukids-hero-content {{ position:relative;z-index:2; }}
  .ukids-hero h1 {{
    font-size:2rem;font-weight:900;color:var(--white);
    margin:0 0 6px;letter-spacing:-0.5px;text-shadow:0 2px 8px rgba(0,0,0,0.15);
  }}
  .ukids-hero p {{ font-size:1rem;color:var(--white);opacity:0.93;margin:0; }}

  /* ── Cards ── */
  .ukids-card {{
    background:var(--white);border-radius:14px;padding:20px 20px 16px;
    margin-bottom:16px;box-shadow:0 2px 8px rgba(0,0,0,0.06);border-top:4px solid var(--teal);
  }}
  .ukids-card-orange {{ border-top-color:var(--orange); }}
  .ukids-card-purple {{ border-top-color:var(--purple); }}
  .ukids-card-yellow {{ border-top-color:var(--yellow); }}
  .ukids-card h3 {{
    font-size:1.05rem;font-weight:800;color:var(--dark);
    margin:0 0 12px;text-transform:uppercase;letter-spacing:0.04em;
  }}

  /* ── Banners ── */
  .info-banner {{
    background:linear-gradient(135deg,var(--purple) 0%,#9B6FC6 100%);
    border-radius:12px;padding:14px 18px;font-size:0.88rem;
    color:var(--white);margin-bottom:16px;line-height:1.75;
  }}
  .info-banner strong {{ font-weight:800; }}
  .closed-banner {{
    background:linear-gradient(135deg,var(--purple) 0%,#9B6FC6 100%);
    border-radius:12px;padding:16px 18px;font-size:0.95rem;
    color:var(--white);margin-bottom:16px;line-height:1.7;text-align:center;
  }}
  .success-banner {{
    background:linear-gradient(135deg,#2ECC8A 0%,#27AE72 100%);
    border-radius:12px;padding:14px 18px;font-size:0.9rem;
    color:var(--white);margin-bottom:16px;line-height:1.7;
  }}

  /* ── Profile ── */
  .profile-banner {{
    background:#F7F5FF;border:1.5px solid #D6CCF0;
    border-radius:12px;padding:14px 16px;margin-bottom:16px;
  }}
  .profile-name {{ font-size:1.12rem;font-weight:900;color:var(--purple); }}
  .profile-sub  {{ font-size:0.82rem;color:var(--muted);margin-top:2px; }}

  /* ── Schedule table ── */
  .schedule-table {{
    width:100%;border-collapse:collapse;margin-top:8px;
  }}
  .schedule-table th {{
    background:var(--teal);color:var(--white);font-size:0.78rem;font-weight:800;
    text-transform:uppercase;letter-spacing:0.05em;padding:8px 12px;text-align:left;
  }}
  .schedule-table td {{
    padding:9px 12px;font-size:0.9rem;border-bottom:1px solid #EDE8DC;color:var(--dark);
  }}
  .schedule-table tr:last-child td {{ border-bottom:none; }}
  .schedule-table tr:nth-child(even) td {{ background:#FAF6EE; }}

  /* ── Change log table ── */
  .log-table {{ width:100%;border-collapse:collapse;margin-top:8px;font-size:0.82rem; }}
  .log-table th {{
    background:var(--purple);color:var(--white);font-size:0.75rem;font-weight:800;
    text-transform:uppercase;letter-spacing:0.05em;padding:7px 10px;text-align:left;
  }}
  .log-table td {{
    padding:8px 10px;border-bottom:1px solid #EDE8DC;color:var(--dark);vertical-align:top;
  }}
  .log-table tr:last-child td {{ border-bottom:none; }}
  .log-table tr:nth-child(even) td {{ background:#FAF6EE; }}

  /* ── Serving positions ── */
  .priority-block {{
    margin-bottom:20px;
  }}
  .priority-label {{
    font-size:0.72rem;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;
    color:var(--muted);margin-bottom:8px;display:flex;align-items:center;gap:8px;
  }}
  .priority-badge {{
    display:inline-block;border-radius:20px;padding:3px 12px;font-size:0.7rem;
    font-weight:800;text-transform:uppercase;letter-spacing:0.06em;color:var(--white);
  }}
  .badge-1 {{ background:var(--teal); }}
  .badge-2 {{ background:var(--orange); }}
  .badge-3 {{ background:var(--purple); }}
  .badge-4 {{ background:#888; }}
  .badge-5 {{ background:#aaa; }}
  .position-chips {{
    display:flex;flex-wrap:wrap;gap:8px;
  }}
  .position-chip {{
    background:var(--white);border:2px solid var(--teal);border-radius:10px;
    padding:8px 14px;font-size:0.88rem;font-weight:700;color:var(--dark);
    box-shadow:0 1px 4px rgba(0,0,0,0.06);
  }}
  .position-chip-2 {{ border-color:var(--orange); }}
  .position-chip-3 {{ border-color:var(--purple); }}
  .position-chip-4 {{ border-color:#aaa; }}
  .position-chip-5 {{ border-color:#ccc;color:var(--muted); }}
  .no-positions {{
    font-size:0.88rem;color:var(--muted);font-style:italic;
  }}

  /* ── Misc ── */
  .section-pill {{
    display:inline-block;background:var(--yellow);color:var(--dark);
    font-size:0.7rem;font-weight:800;text-transform:uppercase;
    letter-spacing:0.08em;padding:3px 10px;border-radius:20px;margin-bottom:10px;
  }}
  .login-wrap {{ max-width:430px;margin:0 auto; }}
  .sticky-submit {{
    position:sticky;bottom:0;z-index:999;background:var(--cream);
    padding:10px 0 4px;border-top:2px solid #EDE8DC;
  }}

  /* ── Buttons ── */
  .stButton > button {{
    width:100%;height:52px;font-size:1.05rem;font-weight:800;
    border-radius:12px;background:var(--teal) !important;
    color:var(--white) !important;border:none !important;
    letter-spacing:0.02em;transition:background 0.2s,transform 0.1s;
  }}
  .stButton > button:hover {{ background:#3AADA9 !important;transform:translateY(-1px); }}
  .stButton > button:active {{ transform:translateY(0); }}
  .stTextInput > div > div > input {{ border-radius:12px; }}
  .stTextArea textarea {{ border-radius:12px; }}
  .stCheckbox {{
    background:#FFF8F0;border:1.5px solid #FCDAB8;
    border-radius:12px;padding:10px 12px;margin-bottom:8px;
  }}
  div[data-testid="stMetric"] {{
    background:#F7F5FF;border:1.5px solid #D6CCF0;border-radius:12px;padding:12px;
  }}
  hr {{ border-color:#EDE8DC;margin:10px 0; }}

  @media (max-width:520px) {{
    div[data-testid="column"] {{ width:100% !important;flex:0 0 100% !important; }}
    .ukids-hero h1 {{ font-size:1.55rem; }}
  }}
</style>
""", unsafe_allow_html=True)

if _logo_src:
    st.markdown(f"""
<div style="text-align:center;padding:18px 0 10px;">
  <img src="{_logo_src}" alt="uKids"
       style="width:100%;max-width:430px;object-fit:contain;">
</div>
""", unsafe_allow_html=True)
else:
    st.markdown(f"""
<div style="text-align:center;padding:18px 0 10px;">
  <h2 style="color:{TEAL};font-weight:900;margin:0;">uKids Availability</h2>
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
        c, ok = cur, True
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
# Google Sheets helpers
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
    counts, out = {}, []
    for h in header:
        base = str(h).strip() or "Unnamed"
        counts[base] = counts.get(base, 0) + 1
        out.append(base if counts[base] == 1 else f"{base}_{counts[base]}")
    return out


def ws_get_values_and_df(ws):
    values = gs_retry(ws.get_all_values)
    if not values:
        return [], [], pd.DataFrame()
    header_raw    = values[0]
    header_unique = make_unique_headers(header_raw)
    rows          = values[1:]
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


# ─────────────────────────────────────────────────────────────
# Cached data fetches
# ─────────────────────────────────────────────────────────────
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


@st.cache_data(ttl=60, show_spinner=False)
def fetch_schedule_df(tab_name: str):
    """Fetch the per-month schedule tab, e.g. 'Jul 25'."""
    sh = get_spreadsheet()
    try:
        ws = sh.worksheet(tab_name)
    except WorksheetNotFound:
        return pd.DataFrame()
    _, _, df = ws_get_values_and_df(ws)
    return df


@st.cache_data(ttl=30, show_spinner=False)
def fetch_change_log_df():
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_CHANGE_LOG, rows=4000, cols=10)
    _, _, df = ws_get_values_and_df(ws)
    return df


@st.cache_data(ttl=300, show_spinner=False)
def fetch_mapping_df():
    """Fetch the Mapping sheet: column A = shortened name, column B = display name."""
    sh = get_spreadsheet()
    try:
        ws = sh.worksheet(TAB_MAPPING)
    except WorksheetNotFound:
        return pd.DataFrame(columns=["shortened_name", "display_name"])
    _, _, df = ws_get_values_and_df(ws)
    if df.empty:
        return pd.DataFrame(columns=["shortened_name", "display_name"])
    cols = list(df.columns)
    # Use first two columns regardless of their header names
    df = df[[cols[0], cols[1]]].copy()
    df.columns = ["shortened_name", "display_name"]
    df["shortened_name"] = df["shortened_name"].astype(str).str.strip()
    df["display_name"]   = df["display_name"].astype(str).str.strip()
    df = df[df["shortened_name"].ne("") & df["display_name"].ne("")]
    return df


def clear_caches():
    try:
        st.cache_data.clear()
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# Write helpers
# ─────────────────────────────────────────────────────────────
def append_response_row(desired_header: list, row_map: dict):
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_RESPONSES, rows=8000, cols=max(250, len(desired_header) + 10))
    header = ws_ensure_header(ws, desired_header)
    row    = [row_map.get(col, "") for col in header]
    gs_retry(ws.append_row, row)


def replace_final_guys_responses_tab(final_df: pd.DataFrame):
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_FINAL_RESPONSES, rows=8000, cols=10)
    header = ["timestamp", "Service", "Name"]
    rows   = final_df.values.tolist() if not final_df.empty else []
    gs_retry(ws.clear)
    gs_retry(ws.update, "A1", [header] + rows)


def append_change_log_row(row_map: dict):
    desired_header = ["timestamp", "logged_by", "change_type", "old_value", "new_value", "notes"]
    sh = get_spreadsheet()
    ws = ensure_worksheet(sh, TAB_CHANGE_LOG, rows=4000, cols=10)
    header = ws_ensure_header(ws, desired_header)
    row    = [row_map.get(col, "") for col in header]
    gs_retry(ws.append_row, row)


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


def get_current_month_tab_name(now_local: datetime) -> str:
    """Returns schedule tab name e.g. 'Jul 25' for the current calendar month."""
    return now_local.strftime("%b %y")


def parse_deadline_local(deadline_local: str, tz_name: str):
    dt_naive = datetime.strptime(deadline_local, "%Y-%m-%d %H:%M")
    if ZoneInfo:
        return dt_naive.replace(tzinfo=ZoneInfo(tz_name))
    return dt_naive


def format_minutes_remaining(delta_seconds: float):
    mins  = max(0, int(delta_seconds // 60))
    hrs   = mins // 60
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
    for tok in ("Morning Service", "Evening Service", "Morning", "Evening", "Service"):
        s = s.replace(tok, "")
    return " ".join(s.split()).strip(" -")


def _build_display_map(labels):
    display_map, used = {}, set()
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
    missing  = required - set(sb_df.columns)
    if missing:
        return None, f"uKids SB is missing columns: {', '.join(sorted(missing))}"
    df = sb_df.copy()
    for col in ["Name", "Username", "Password"]:
        df[col] = df[col].astype(str).str.strip()
    df["Active"] = df["Active"].astype(str).str.strip().str.lower()
    match = df[
        (df["Username"].str.lower() == str(username).strip().lower())
        & (df["Password"] == str(password).strip())
        & (df["Active"].isin(["true", "yes", "1", "active"]))
    ]
    if match.empty:
        return None, "Incorrect username/password, or account is inactive."
    row = match.iloc[0]
    return {"name": row["Name"], "username": row["Username"]}, ""


def build_final_guys_df(responses_df: pd.DataFrame, month_key: str):
    if responses_df is None or responses_df.empty:
        return pd.DataFrame(columns=["timestamp", "Service", "Name"])
    df = responses_df.copy()
    for col in ["timestamp", "Availability month", "Serving Guy"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype(str).str.strip()
    df = df[df["Availability month"] == month_key].copy()
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "Service", "Name"])
    df = df.sort_values("timestamp").drop_duplicates(subset=["Serving Guy"], keep="last")
    meta_cols    = {"timestamp", "Availability month", "Serving Guy",
                    "Director", "Serving Girl", "Name", "Service"}
    service_cols = [c for c in df.columns if c not in meta_cols]
    rows = []
    for _, row in df.iterrows():
        ts   = str(row.get("timestamp", "")).strip()
        name = str(row.get("Serving Guy", "")).strip()
        if not name:
            continue
        for service in service_cols:
            if str(row.get(service, "")).strip().lower() == "yes":
                rows.append({"timestamp": ts, "Service": service, "Name": name})
    return pd.DataFrame(rows, columns=["timestamp", "Service", "Name"])


def auto_update_final_sheet(month_key: str):
    try:
        responses_df = fetch_responses_df()
        final_df     = build_final_guys_df(responses_df, month_key)
        replace_final_guys_responses_tab(final_df)
        clear_caches()
        return True, len(final_df), ""
    except Exception as e:
        return False, 0, str(e)


def compute_nonresponders_current_month(sb_df, responses_df, month_key):
    if sb_df is None or sb_df.empty or "Name" not in sb_df.columns:
        return pd.DataFrame(columns=["Name", "Status"])
    base = sb_df.copy()
    if "Active" in base.columns:
        base["Active"] = base["Active"].astype(str).str.strip().str.lower()
        base = base[base["Active"].isin(["true", "yes", "1", "active"])]
    base_names = sorted({str(x).strip() for x in base["Name"] if str(x).strip()})
    out_base   = pd.DataFrame({"Name": base_names})
    if responses_df is None or responses_df.empty:
        out_base["Status"] = "Non-responder"
        return out_base
    df = responses_df.copy()
    for col in ["Availability month", "Serving Guy"]:
        if col not in df.columns:
            df[col] = ""
    df["Availability month"] = df["Availability month"].astype(str).str.strip()
    df["Serving Guy"]        = df["Serving Guy"].astype(str).str.strip()
    df        = df[df["Availability month"] == month_key]
    responded = set(df["Serving Guy"].dropna().tolist())
    out       = out_base[~out_base["Name"].isin(responded)].copy()
    out["Status"] = "Non-responder"
    return out.reset_index(drop=True)


# ─────────────────────────────────────────────────────────────
# Load always-needed data
# ─────────────────────────────────────────────────────────────
try:
    sb_df             = fetch_sb_df()
    deadlines_df      = fetch_deadlines_df()
    service_dates_all = fetch_service_dates_df()
except Exception as e:
    st.error(f"Failed to load Google Sheets: {e}")
    st.stop()


# ─────────────────────────────────────────────────────────────
# Session state defaults
# ─────────────────────────────────────────────────────────────
for key, default in [
    ("logged_in", False),
    ("user_name", ""),
    ("username",  ""),
    ("page",      "home"),   # home | availability | schedule | changes | positions
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────────────────────
# LOGIN SCREEN
# ─────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown("""
<div class="ukids-card">
  <span class="section-pill">Login</span>
  <h3>Access your profile</h3>
</div>
""", unsafe_allow_html=True)
    username      = st.text_input("Username")
    password      = st.text_input("Password", type="password")
    login_clicked = st.button("Login")
    st.caption("Forgot your password? Contact Veniqué to reset it.")
    st.markdown("</div>", unsafe_allow_html=True)

    if login_clicked:
        user, err = login_user(sb_df, username, password)
        if err:
            st.error(err)
        else:
            st.session_state.logged_in = True
            st.session_state.user_name = user["name"]
            st.session_state.username  = user["username"]
            st.session_state.page      = "home"
            st.rerun()
    st.stop()


# ─────────────────────────────────────────────────────────────
# SHARED TOP BAR
# ─────────────────────────────────────────────────────────────
col_prof, col_out = st.columns([5, 1])
with col_prof:
    st.markdown(f"""
<div class="profile-banner">
  <div class="profile-name">Welcome, {st.session_state.user_name}</div>
  <div class="profile-sub">Logged in as @{st.session_state.username}</div>
</div>
""", unsafe_allow_html=True)
with col_out:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout"):
        for k in ["logged_in", "user_name", "username", "page", "final_sheet_updated"]:
            st.session_state.pop(k, None)
        st.rerun()


def back_button():
    if st.button("← Back to menu"):
        st.session_state.page = "home"
        st.rerun()


# ─────────────────────────────────────────────────────────────
# Resolve timezone once for all pages
# ─────────────────────────────────────────────────────────────
BASE_TZ = "Africa/Johannesburg"
if not deadlines_df.empty and "timezone" in deadlines_df.columns:
    tz0 = str(deadlines_df["timezone"].iloc[0]).strip()
    if tz0:
        BASE_TZ = tz0

now_base = get_now_in_tz(BASE_TZ)


# ═════════════════════════════════════════════════════════════
# PAGE: HOME MENU
# ═════════════════════════════════════════════════════════════
if st.session_state.page == "home":

    st.markdown("""
<div style="margin-bottom:8px;">
  <p style="font-size:0.92rem;color:#7A6F6F;margin:0 0 16px;">What would you like to do?</p>
</div>
""", unsafe_allow_html=True)

    # Row 1
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
<div style="background:#fff;border-radius:16px;padding:22px 10px 18px;text-align:center;
box-shadow:0 2px 10px rgba(0,0,0,0.07);border-top:5px solid #5BC4C0;margin-bottom:4px;">
  <div style="font-size:2rem;margin-bottom:8px;">🗓️</div>
  <div style="font-size:0.8rem;font-weight:800;color:#2A2A2A;text-transform:uppercase;
  letter-spacing:0.05em;line-height:1.3;">Submit<br>Availability</div>
</div>
""", unsafe_allow_html=True)
        if st.button("Open", key="btn_avail"):
            st.session_state.page = "availability"
            st.rerun()

    with c2:
        st.markdown("""
<div style="background:#fff;border-radius:16px;padding:22px 10px 18px;text-align:center;
box-shadow:0 2px 10px rgba(0,0,0,0.07);border-top:5px solid #E8724A;margin-bottom:4px;">
  <div style="font-size:2rem;margin-bottom:8px;">📋</div>
  <div style="font-size:0.8rem;font-weight:800;color:#2A2A2A;text-transform:uppercase;
  letter-spacing:0.05em;line-height:1.3;">Review<br>Scheduling</div>
</div>
""", unsafe_allow_html=True)
        if st.button("Open", key="btn_sched"):
            st.session_state.page = "schedule"
            st.rerun()

    # Row 2
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("""
<div style="background:#fff;border-radius:16px;padding:22px 10px 18px;text-align:center;
box-shadow:0 2px 10px rgba(0,0,0,0.07);border-top:5px solid #7B4FA6;margin-bottom:4px;">
  <div style="font-size:2rem;margin-bottom:8px;">✏️</div>
  <div style="font-size:0.8rem;font-weight:800;color:#2A2A2A;text-transform:uppercase;
  letter-spacing:0.05em;line-height:1.3;">Log<br>Changes</div>
</div>
""", unsafe_allow_html=True)
        if st.button("Open", key="btn_log"):
            st.session_state.page = "changes"
            st.rerun()

    with c4:
        st.markdown("""
<div style="background:#fff;border-radius:16px;padding:22px 10px 18px;text-align:center;
box-shadow:0 2px 10px rgba(0,0,0,0.07);border-top:5px solid #F5C842;margin-bottom:4px;">
  <div style="font-size:2rem;margin-bottom:8px;">⭐</div>
  <div style="font-size:0.8rem;font-weight:800;color:#2A2A2A;text-transform:uppercase;
  letter-spacing:0.05em;line-height:1.3;">Serving<br>Positions</div>
</div>
""", unsafe_allow_html=True)
        if st.button("Open", key="btn_positions"):
            st.session_state.page = "positions"
            st.rerun()

    st.stop()


# ═════════════════════════════════════════════════════════════
# PAGE: SUBMIT AVAILABILITY
# ═════════════════════════════════════════════════════════════
elif st.session_state.page == "availability":

    back_button()

    # Validate required tabs
    for df, name, needed in [
        (deadlines_df,      TAB_DEADLINES, {"month", "deadline_local", "timezone"}),
        (service_dates_all, TAB_DATES,     {"target_month", "date", "label", "is_service_day"}),
    ]:
        missing = needed - set(df.columns)
        if missing:
            st.error(f"Google Sheet tab '{name}' is missing columns: {', '.join(sorted(missing))}")
            st.stop()

    for col in ["month", "deadline_local", "timezone"]:
        deadlines_df[col] = deadlines_df[col].astype(str).str.strip()
    for col in ["target_month", "date", "label", "is_service_day"]:
        service_dates_all[col] = service_dates_all[col].astype(str).str.strip()

    target_month_key = get_target_month_key(now_base)

    month_dates = service_dates_all[
        (service_dates_all["target_month"] == target_month_key)
        & (service_dates_all["is_service_day"].map(_is_truthy))
    ].copy()

    if month_dates.empty:
        st.markdown(f"""
<div class="closed-banner">
  <strong>No service dates found for {target_month_key}.</strong><br>
  The form isn't open yet — check back soon.
</div>
""", unsafe_allow_html=True)
        st.stop()

    month_dates["_sort"] = month_dates["date"].map(_safe_parse_date_ymd)
    month_dates          = month_dates.sort_values("_sort").drop(columns=["_sort"])
    date_labels          = month_dates["label"].astype(str).tolist()

    morning_labels      = [l for l in date_labels if "morning" in l.lower()]
    evening_labels      = [l for l in date_labels if "evening" in l.lower()]
    morning_display_map = _build_display_map(morning_labels)
    evening_display_map = _build_display_map(evening_labels)
    morning_options     = list(morning_display_map.keys())
    evening_options     = list(evening_display_map.keys())

    def get_deadline_for_target_month(deadlines, month_key):
        match = deadlines[deadlines["month"] == month_key]
        if match.empty:
            return None, BASE_TZ
        row      = match.iloc[0]
        tz_name  = str(row["timezone"]).strip() or BASE_TZ
        deadline = parse_deadline_local(str(row["deadline_local"]).strip(), tz_name)
        return deadline, tz_name

    deadline_dt, deadline_tz = get_deadline_for_target_month(deadlines_df, target_month_key)

    is_closed = True
    if deadline_dt is not None:
        now_local = get_now_in_tz(deadline_tz)
        is_closed = (deadline_dt - now_local).total_seconds() <= 0

    if is_closed:
        if not st.session_state.get("final_sheet_updated"):
            ok, rows_written, err = auto_update_final_sheet(target_month_key)
            st.session_state["final_sheet_updated"] = True
            if ok:
                st.success(f"Final Responses updated automatically with {rows_written} row(s).")
            else:
                st.warning(f"Final Responses could not update automatically: {err}")
        target_month_name = datetime.strptime(target_month_key, "%Y-%m").strftime("%B")
        st.markdown(f"""
<div class="closed-banner">
  <strong>{target_month_name} availability submissions are now closed.</strong>
</div>
""", unsafe_allow_html=True)
        st.stop()

    now_local         = get_now_in_tz(deadline_tz)
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

    # Morning
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
        if st.checkbox(opt, key=f"morn_{target_month_key}_{opt}"):
            morning_selected.append(opt)

    # Evening
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
        if st.checkbox(opt, key=f"eve_{target_month_key}_{opt}"):
            evening_selected.append(opt)

    # Review
    st.markdown("""
<div class="ukids-card ukids-card-orange">
  <span class="section-pill">Review</span>
  <h3>Your selection</h3>
</div>
""", unsafe_allow_html=True)
    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        st.metric("Name", st.session_state.user_name)
    with rc2:
        st.metric("Morning selected", len(morning_selected))
    with rc3:
        st.metric("Evening selected", len(evening_selected))

    # Submit
    st.markdown('<div class="sticky-submit">', unsafe_allow_html=True)
    submitted = st.button("Submit availability")
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        now_check = get_now_in_tz(deadline_tz)
        if (deadline_dt - now_check).total_seconds() <= 0:
            st.error("The form has just closed.")
            st.stop()
        selected_all = (
            {morning_display_map[d] for d in morning_selected if d in morning_display_map}
            | {evening_display_map[d] for d in evening_selected if d in evening_display_map}
        )
        yes_map = {lbl: ("Yes" if lbl in selected_all else "No") for lbl in date_labels}
        now_iso = datetime.utcnow().isoformat() + "Z"
        row_map = {
            "timestamp":          now_iso,
            "Availability month": target_month_key,
            "Serving Guy":        st.session_state.user_name,
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

    st.stop()


# ═════════════════════════════════════════════════════════════
# PAGE: REVIEW SCHEDULING
# ═════════════════════════════════════════════════════════════
elif st.session_state.page == "schedule":

    back_button()

    st.markdown("""
<div class="ukids-card ukids-card-orange">
  <span class="section-pill">This month</span>
  <h3>Your schedule</h3>
</div>
""", unsafe_allow_html=True)

    tab_name      = get_current_month_tab_name(now_base)
    display_month = now_base.strftime("%B %Y")

    st.markdown(f"""
<div class="info-banner">
  Showing schedule for <strong>{display_month}</strong>
</div>
""", unsafe_allow_html=True)

    with st.spinner("Loading schedule…"):
        sched_df = fetch_schedule_df(tab_name)

    if sched_df.empty:
        st.markdown(f"""
<div class="closed-banner">
  No schedule found for <strong>{display_month}</strong>.<br>
  The tab "<strong>{tab_name}</strong>" may not exist yet.
</div>
""", unsafe_allow_html=True)
    else:
        person_name = st.session_state.user_name.strip().lower()
        mask        = sched_df.apply(
            lambda col: col.astype(str).str.strip().str.lower() == person_name
        ).any(axis=1)
        person_rows = sched_df[mask].copy()

        if person_rows.empty:
            st.markdown(f"""
<div class="closed-banner">
  You don't appear to be scheduled for any services in <strong>{display_month}</strong> yet.
</div>
""", unsafe_allow_html=True)
        else:
            display_cols = [c for c in person_rows.columns
                            if person_rows[c].astype(str).str.strip().ne("").any()]
            display_df   = person_rows[display_cols].reset_index(drop=True)

            headers_html = "".join(f"<th>{c}</th>" for c in display_df.columns)
            rows_html    = "".join(
                f"<tr>{''.join(f'<td>{v}</td>' for v in row)}</tr>"
                for _, row in display_df.iterrows()
            )

            st.markdown(f"""
<div class="ukids-card">
  <table class="schedule-table">
    <thead><tr>{headers_html}</tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)

            st.markdown(f"""
<div class="success-banner">
  You are scheduled for <strong>{len(person_rows)}</strong> service(s) this month.
</div>
""", unsafe_allow_html=True)

    if st.button("Refresh schedule"):
        clear_caches()
        st.rerun()

    st.stop()


# ═════════════════════════════════════════════════════════════
# PAGE: LOG CHANGES
# ═════════════════════════════════════════════════════════════
elif st.session_state.page == "changes":

    back_button()

    st.markdown("""
<div class="ukids-card ukids-card-purple">
  <span class="section-pill">Log a change</span>
  <h3>Submit a change</h3>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="info-banner">
  Use this to log serving position changes, surname changes, or anything else
  that needs to be noted. Veniqué will be notified and can action it.
</div>
""", unsafe_allow_html=True)

    change_type = st.selectbox(
        "What type of change is this?",
        ["Serving position change", "Surname change", "Other"],
    )

    if change_type == "Serving position change":
        old_value = st.text_input("Current serving position (what it is now)")
        new_value = st.text_input("New serving position (what it should change to)")
        notes     = st.text_area("Any extra details (optional)", height=80)

    elif change_type == "Surname change":
        old_value = st.text_input("Current surname")
        new_value = st.text_input("New surname")
        notes     = st.text_area("Any extra details (optional)", height=80)

    else:
        old_value = ""
        new_value = ""
        notes     = st.text_area("Describe the change", height=120)

    st.markdown("<br>", unsafe_allow_html=True)
    submit_change = st.button("Submit change")

    if submit_change:
        if change_type != "Other" and (not old_value.strip() or not new_value.strip()):
            st.error("Please fill in both the current and new values before submitting.")
        elif change_type == "Other" and not notes.strip():
            st.error("Please describe the change before submitting.")
        else:
            row_map = {
                "timestamp":   datetime.utcnow().isoformat() + "Z",
                "logged_by":   st.session_state.user_name,
                "change_type": change_type,
                "old_value":   old_value.strip(),
                "new_value":   new_value.strip(),
                "notes":       notes.strip(),
            }
            try:
                append_change_log_row(row_map)
                clear_caches()
                st.success("Change logged. Veniqué will review and action it.")
                st.balloons()
            except Exception as e:
                st.error(f"Failed to save change: {e}")

    # Show this person's own log history
    st.markdown("---")
    st.markdown("""
<div class="ukids-card ukids-card-yellow">
  <span class="section-pill">History</span>
  <h3>Your previous submissions</h3>
</div>
""", unsafe_allow_html=True)

    with st.spinner("Loading…"):
        log_df = fetch_change_log_df()

    if log_df.empty or "logged_by" not in log_df.columns:
        st.caption("No change log entries found yet.")
    else:
        my_logs = log_df[
            log_df["logged_by"].astype(str).str.strip().str.lower()
            == st.session_state.user_name.strip().lower()
        ].copy()

        if my_logs.empty:
            st.caption("You haven't logged any changes yet.")
        else:
            if "timestamp" in my_logs.columns:
                my_logs = my_logs.sort_values("timestamp", ascending=False)

            show_cols   = [c for c in ["timestamp", "change_type", "old_value", "new_value", "notes"]
                           if c in my_logs.columns]
            display_log = my_logs[show_cols].reset_index(drop=True)

            headers_html = "".join(
                f"<th>{c.replace('_', ' ').title()}</th>" for c in display_log.columns
            )
            rows_html = "".join(
                f"<tr>{''.join(f'<td>{v}</td>' for v in row)}</tr>"
                for _, row in display_log.iterrows()
            )

            st.markdown(f"""
<div class="ukids-card">
  <table class="log-table">
    <thead><tr>{headers_html}</tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)

    st.stop()


# ═════════════════════════════════════════════════════════════
# PAGE: SERVING POSITIONS
# ═════════════════════════════════════════════════════════════
elif st.session_state.page == "positions":

    back_button()

    st.markdown("""
<div class="ukids-card ukids-card-yellow">
  <span class="section-pill">Your roles</span>
  <h3>Serving Positions</h3>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="info-banner">
  These are the positions you are able to serve in.<br>
  <strong>Priority 1</strong> is your best fit — at least one of those must be met when you're scheduled.
  The other priorities are used to fill gaps.
</div>
""", unsafe_allow_html=True)

    # Load mapping sheet (acronym → full name)
    with st.spinner("Loading positions…"):
        mapping_df  = fetch_mapping_df()
        person_row  = sb_df[
            sb_df["Name"].astype(str).str.strip().str.lower()
            == st.session_state.user_name.strip().lower()
        ]

    if person_row.empty:
        st.error("Could not find your profile in the team sheet.")
        st.stop()

    person_row = person_row.iloc[0]

    # Build a lookup dict: shortened_name → display_name
    if not mapping_df.empty:
        name_map = dict(zip(
            mapping_df["shortened_name"].str.lower(),
            mapping_df["display_name"]
        ))
    else:
        name_map = {}

    def resolve_name(acronym: str) -> str:
        """Return the full display name for an acronym, or the acronym itself if not found."""
        return name_map.get(str(acronym).strip().lower(), str(acronym).strip())

    def get_positions_for_group(columns: list) -> list:
        """
        Given a list of column names (e.g. ['1A','1B','1C','1D','1E']),
        return the list of non-empty, non-N/A display names.
        """
        results = []
        for col in columns:
            if col not in person_row.index:
                continue
            val = str(person_row[col]).strip()
            if val == "" or val.lower() in ("n/a", "na", "none", "-"):
                continue
            results.append(resolve_name(val))
        return results

    # Define priority groups: label, slot columns, badge class, chip class, description
    priority_groups = [
        ("Priority 1 — Primary fit",
         ["1A", "1B", "1C", "1D", "1E"],
         "badge-1", "position-chip",
         "At least one of these will always be met when you're scheduled."),
        ("Priority 2 — Secondary fit",
         ["2A", "2B", "2C", "2D", "2E"],
         "badge-2", "position-chip position-chip-2",
         "Used when there are gaps to fill."),
        ("Priority 3 — Third option",
         ["3A", "3B", "3C", "3D", "3E"],
         "badge-3", "position-chip position-chip-3",
         "Used when higher priorities are fully covered."),
        ("Priority 4 — Fourth option",
         ["4A", "4B"],
         "badge-4", "position-chip position-chip-4",
         "Occasional fill-in positions."),
        ("Priority 5 — Last resort",
         ["5"],
         "badge-5", "position-chip position-chip-5",
         "Only used when all other options are exhausted."),
    ]

    any_positions_found = False

    for label, cols, badge_cls, chip_cls, description in priority_groups:
        positions = get_positions_for_group(cols)
        if not positions:
            continue
        any_positions_found = True

        chips_html = "".join(
            f'<div class="{chip_cls}">{pos}</div>' for pos in positions
        )

        st.markdown(f"""
<div class="ukids-card" style="margin-bottom:14px;">
  <div class="priority-label">
    <span class="priority-badge {badge_cls}">{label}</span>
  </div>
  <div style="font-size:0.78rem;color:#7A6F6F;margin-bottom:10px;">{description}</div>
  <div class="position-chips">{chips_html}</div>
</div>
""", unsafe_allow_html=True)

    if not any_positions_found:
        st.markdown("""
<div class="closed-banner">
  No serving positions have been set up for your profile yet.<br>
  Contact Veniqué if you think this is a mistake.
</div>
""", unsafe_allow_html=True)

    st.stop()


# ─────────────────────────────────────────────────────────────
# ADMIN PANEL (home page only)
# ─────────────────────────────────────────────────────────────
if st.session_state.page == "home":

    st.markdown("---")
    with st.expander("Admin"):
        st.caption("Mode: Google Sheets profile app")

        if not ADMIN_KEY:
            st.info("To protect exports, set an ADMIN_KEY in Streamlit Secrets.")

        admin_key_input = st.text_input("Enter admin key", type="password")

        if ADMIN_KEY and admin_key_input != ADMIN_KEY:
            if admin_key_input:
                st.error("Incorrect admin key.")
        else:
            if admin_key_input or not ADMIN_KEY:
                st.success("Admin unlocked.")

                try:
                    responses_df = fetch_responses_df()
                except Exception as e:
                    st.error(f"Could not load responses: {e}")
                    responses_df = pd.DataFrame()

                target_month_key = get_target_month_key(now_base)

                st.write(f"Total submissions: **{len(responses_df)}**")
                if not responses_df.empty:
                    st.dataframe(responses_df, use_container_width=True)

                st.divider()
                st.markdown("### Build Final Responses")
                final_preview_df = build_final_guys_df(responses_df, target_month_key)
                st.write(f"Rows for **{target_month_key}**: **{len(final_preview_df)}**")
                if not final_preview_df.empty:
                    st.dataframe(final_preview_df, use_container_width=True)
                if st.button("Rebuild Final Responses tab"):
                    try:
                        replace_final_guys_responses_tab(final_preview_df)
                        clear_caches()
                        st.success(f"Final Responses rebuilt with {len(final_preview_df)} row(s).")
                    except Exception as e:
                        st.error(f"Failed: {e}")

                st.divider()
                st.markdown("### Non-responders")
                nonresp_df = compute_nonresponders_current_month(sb_df, responses_df, target_month_key)
                st.write(f"Shown: **{len(nonresp_df)}**")
                st.dataframe(nonresp_df, use_container_width=True)

                st.divider()
                st.markdown("### Change Log (all entries)")
                try:
                    all_logs = fetch_change_log_df()
                    st.write(f"Total entries: **{len(all_logs)}**")
                    if not all_logs.empty:
                        st.dataframe(all_logs, use_container_width=True)
                    else:
                        st.caption("No change log entries yet.")
                except Exception as e:
                    st.error(f"Could not load change log: {e}")
