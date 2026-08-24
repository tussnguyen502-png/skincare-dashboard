# -*- coding: utf-8 -*-
"""
6 DASHBOARD SKINCARE · PYTHON (Streamlit) — Soft Feminine + Luxury
==================================================================
1. Tong quan Kinh doanh          (Executive Overview · Descriptive)
2. Hanh vi Khach hang            (Customer Behavior · Descriptive)
3. Phan khuc Khach hang RFM      (RFM Segmentation · Diagnostic)
4. Phan tich Giu chan Khach hang (Cohort & Retention · Diagnostic)
5. Phat hien Bat thuong          (Anomaly Detection · Diagnostic)
6. Du bao & Khuyen nghi          (Predictive + Prescriptive)

CHAY:  pip install -r requirements.txt  ->  streamlit run quytusapp.py
Dat thu muc DW_SCHEMA_VI canh quytusapp.py (hoac dat bien DW_DIR).
"""

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── DESIGN TOKENS — Soft Feminine + Luxury ───────────────────────────────
INK="#2B2420"; MUTED="#8A7B6C"; CREAM="#FBF6F1"; PANEL="#FFFFFF"; LINE="#EDE2D8"
ROSE="#C97E8C"; ROSE_SOFT="#F3DEE1"; SAGE="#8FAE96"; SAGE_SOFT="#DCE7DE"
GOLD="#B0873F"; GOLD_SOFT="#EFE1C4"; SKY="#9FBFC9"; MAUVE="#A9829A"; STONE="#B7ACA0"; RED="#B5555A"
PAL=[ROSE, SAGE, GOLD, SKY, MAUVE, STONE]
def _tim_thu_muc_du_lieu():
    """Tu dong tim thu muc chua fact_transaction.csv (chiu duoc truong hop giai nen long thu muc)."""
    base = os.path.dirname(os.path.abspath(__file__))
    ung_vien = []
    env = os.environ.get("DW_DIR")
    if env: ung_vien.append(env)
    ung_vien += [
        os.path.join(base, "DW_SCHEMA_VI"),
        os.path.join(base, "DW_SCHEMA_VI", "DW_SCHEMA_VI"),
        base,
        os.path.join(base, "data", "DW_SCHEMA_VI"),
        os.path.join(base, "DW_SCHEMA_VI_v2", "DW_SCHEMA_VI"),
        os.path.join(os.path.dirname(base), "DW_SCHEMA_VI"),
    ]
    def _co(c):  # file goc hoac ban nen .gz (file lon duoc nen de giam dung luong repo)
        return os.path.isfile(os.path.join(c, "fact_transaction.csv")) or os.path.isfile(os.path.join(c, "fact_transaction.csv.gz"))
    for c in ung_vien:
        if c and _co(c):
            return c, ung_vien
    # Quet sau toi da 3 cap tu thu muc chua quytusapp.py
    for root, dirs, files in os.walk(base):
        if root[len(base):].count(os.sep) > 3:
            dirs[:] = []; continue
        if "fact_transaction.csv" in files or "fact_transaction.csv.gz" in files:
            return root, ung_vien
    return None, ung_vien

DATA_DIR, _UNG_VIEN = _tim_thu_muc_du_lieu()

st.set_page_config(page_title="Skincare Insights · Báo cáo", layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500;600;700&display=swap');
  .stApp {{ background:{CREAM}; }}
  html, body, [class*="css"] {{ font-family:'Inter',system-ui,sans-serif; }}
  h1,h2,h3 {{ font-family:'Playfair Display',serif; color:{INK}; font-weight:600; letter-spacing:.01em; }}
  h1 {{ font-style:italic; text-align:center; }}
  div[data-testid="stCaptionContainer"] {{ text-align:center; }}

  /* Report header (logo + title) */
  .report-hero {{ display:flex; align-items:center; gap:16px; background:linear-gradient(120deg,#fff,{ROSE_SOFT});
      border:1px solid {LINE}; border-radius:20px; padding:16px 22px; margin:2px 0 12px;
      box-shadow:0 8px 26px rgba(43,36,32,.07); }}
  .report-hero .logo {{ width:52px; height:52px; border-radius:14px; background:linear-gradient(135deg,{ROSE},{MAUVE});
      display:flex; align-items:center; justify-content:center; font-size:26px; box-shadow:0 4px 12px rgba(201,126,140,.35); }}
  .rtitle {{ font-family:'Playfair Display',serif; font-size:24px; font-weight:700; color:{INK}; line-height:1.1; letter-spacing:.03em; }}
  .rsub {{ color:{MUTED}; font-size:12.5px; margin-top:2px; }}
  .rbadge {{ margin-left:auto; text-align:right; color:{GOLD}; font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; }}

  /* Hero image banner */
  .hero-wrap {{ position:relative; border-radius:22px; overflow:hidden; margin:6px 0 18px; box-shadow:0 10px 30px rgba(43,36,32,.12); border:1px solid {LINE}; }}
  .hero-wrap img {{ width:100%; height:170px; object-fit:cover; display:block; filter:saturate(.92) brightness(.97); }}
  .hero-overlay {{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(43,36,32,0) 40%, rgba(43,36,32,.55) 100%); }}
  .hero-caption {{ position:absolute; left:20px; bottom:12px; color:#fff; font-family:'Playfair Display',serif; font-style:italic; font-size:14px; text-shadow:0 1px 4px rgba(0,0,0,.35); }}

  .tip {{ display:inline-block; margin-left:6px; width:15px; height:15px; line-height:15px; text-align:center; border-radius:50%; background:{ROSE_SOFT}; color:{ROSE}; font-size:10px; font-weight:700; cursor:help; border:1px solid {ROSE}; vertical-align:middle; }}
  .eyebrow {{ font-size:10.5px; letter-spacing:.14em; text-transform:uppercase; color:{GOLD}; font-weight:700; margin-bottom:2px; }}
  .card-title {{ font-family:'Playfair Display',serif; font-weight:600; font-size:17px; color:{INK}; margin:0 0 3px; }}
  .card-sub {{ color:{MUTED}; font-size:12px; margin:0 0 10px; }}
  .goldrule {{ height:2px; width:34px; background:linear-gradient(90deg,{GOLD},{ROSE}); border-radius:2px; margin:6px 0 12px; }}

  div[data-testid="stMetric"] {{ background:{PANEL}; border:1px solid {LINE}; border-top:3px solid {ROSE}; border-radius:14px; padding:12px 14px; box-shadow:0 1px 2px rgba(43,36,32,.04); }}
  div[data-testid="stMetricValue"] {{ font-family:'Playfair Display',serif; font-size:23px; color:{INK}; font-weight:600; }}
  div[data-testid="stMetricLabel"] {{ color:{MUTED}; text-transform:uppercase; font-size:10.5px; letter-spacing:.08em; }}
  div[data-testid="stVerticalBlockBorderWrapper"] {{ border:1px solid {LINE} !important; border-radius:18px; background:{PANEL}; padding:16px 18px 8px; box-shadow:0 1px 2px rgba(43,36,32,.04), 0 10px 26px rgba(43,36,32,.05); }}
  .note {{ background:{ROSE_SOFT}; border-left:3px solid {ROSE}; border-radius:10px; padding:10px 14px; color:{INK}; font-size:13px; margin:6px 0 14px; }}
  .read {{ background:{SAGE_SOFT}; border-left:3px solid {SAGE}; border-radius:10px; padding:10px 14px; color:#25352a; font-size:13px; margin:6px 0 14px; }}
  .warn {{ background:{GOLD_SOFT}; border-left:3px solid {GOLD}; border-radius:10px; padding:9px 14px; color:#5c460f; font-size:13px; margin:6px 0 14px; }}
  .risk {{ background:#F6E4E6; border-left:4px solid #B5555A; border-radius:10px; padding:12px 16px; color:#6d2e33; font-size:13.5px; margin:8px 0 14px; }}
  .risk b {{ color:#8f3a40; }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{ background:{PANEL}; border-right:1px solid {LINE}; }}
  section[data-testid="stSidebar"] * {{ color:{INK}; }}
  section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {{ color:{MUTED} !important; }}
  .slicer-group {{ font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:{GOLD}; font-weight:700; margin:10px 0 2px; }}
  .stMultiSelect [data-baseweb="tag"] {{ background:{ROSE} !important; border-radius:8px; }}
  section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span {{ color:#fff !important; }}
  /* Bo loc gon: it padding, label nho, khoang cach hep */
  section[data-testid="stSidebar"] div[data-testid="stDateInput"],
  section[data-testid="stSidebar"] div[data-testid="stSelectbox"],
  section[data-testid="stSidebar"] div[data-testid="stSlider"] {{ border:1px solid {LINE}; border-radius:9px; padding:5px 9px 6px; margin-bottom:6px; background:{PANEL}; }}
  section[data-testid="stSidebar"] div[data-testid="stDateInput"]:hover,
  section[data-testid="stSidebar"] div[data-testid="stSelectbox"]:hover,
  section[data-testid="stSidebar"] div[data-testid="stSlider"]:hover {{ border-color:{ROSE}; }}
  section[data-testid="stSidebar"] div[data-testid="stDateInput"] label,
  section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label,
  section[data-testid="stSidebar"] div[data-testid="stSlider"] label {{ font-size:11.5px !important; font-weight:600; margin-bottom:1px; }}
  section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] {{ font-size:12px; }}
  section[data-testid="stSidebar"] div[data-testid="stDateInput"] input {{ font-size:11px; padding:3px 6px; }}
  section[data-testid="stSidebar"] .stCaption {{ font-size:10.5px; }}

  /* Top navigation bar buttons */
  div.stButton > button {{ border-radius:12px; border:1px solid {LINE}; background:{PANEL}; color:{INK};
      font-weight:600; font-size:13px; padding:9px 6px; box-shadow:0 1px 2px rgba(43,36,32,.04); transition:all .15s; }}
  div.stButton > button:hover {{ border-color:{ROSE}; color:{ROSE}; }}
  div.stButton > button[kind="primary"] {{ background:linear-gradient(135deg,{ROSE},{MAUVE}); border:1px solid {ROSE}; color:#fff; }}
</style>""", unsafe_allow_html=True)


# ── Load ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Đang tải dữ liệu DW_SCHEMA_VI...")
def load(dir_):
    def r(n):
        p=os.path.join(dir_,n)
        if not os.path.isfile(p) and os.path.isfile(p+".gz"): p=p+".gz"  # file lon duoc nen .gz de giam dung luong repo
        return pd.read_csv(p)
    d=dict(ft=r("fact_transaction.csv"),cus=r("dim_customer.csv"),prod=r("dim_product.csv"),
        date=r("dim_date.csv"),geo=r("dim_geography.csv"),chan=r("dim_channel.csv"),
        pay=r("dim_payment.csv"),brand=r("dim_brand.csv"),cat=r("dim_category.csv"),
        rfm=r("mart_customer_rfm.csv"),cohort=r("mart_cohort_retention.csv"),anom=r("mart_anomaly_flag.csv"))
    # Chi ghep cac cot thuc su dung -> giam bo nho dang ke voi 258k giao dich
    m=(d["ft"].merge(d["cus"][["ma_khach_hang","gioi_tinh","tuoi","ma_dia_ly","ma_kenh"]],on="ma_khach_hang",how="left")
       .merge(d["prod"][["ma_san_pham","ten_san_pham","ma_thuong_hieu","ma_danh_muc"]],on="ma_san_pham",how="left")
       .merge(d["brand"],on="ma_thuong_hieu",how="left").merge(d["cat"][["ma_danh_muc","ten_danh_muc"]],on="ma_danh_muc",how="left")
       .merge(d["geo"],on="ma_dia_ly",how="left").merge(d["chan"],on="ma_kenh",how="left").merge(d["pay"],on="ma_thanh_toan",how="left")
       .merge(d["date"][["khoa_ngay","ngay_day_du","nam","quy","thang","ten_thu"]],on="khoa_ngay",how="left"))
    m["ngay"]=pd.to_datetime(m["ngay_day_du"]); m["doanh_thu"]=m["so_luong"]*m["don_gia"]-m["so_tien_giam_gia"]
    m["thang_ky"]=m["ngay"].dt.to_period("M").astype(str)
    m=m.drop(columns=[c for c in ["ngay_day_du","ma_dia_ly","ma_kenh","ma_thuong_hieu","ma_danh_muc"] if c in m.columns])
    # Toi uu kieu du lieu: 299 MB -> ~121 MB
    for c in ["gioi_tinh","ten_danh_muc","phan_cap_thuong_hieu","vung_mien","thanh_pho",
              "ten_kenh_tiep_thi","phuong_thuc_thanh_toan","ten_thu","ten_thuong_hieu"]:
        if c in m.columns: m[c]=m[c].astype("category")
    for c in ["so_luong","tuoi","nam","quy","thang"]:
        if c in m.columns: m[c]=pd.to_numeric(m[c],downcast="unsigned")
    for c in ["don_gia","so_tien_giam_gia","phi_van_chuyen","doanh_thu"]:
        if c in m.columns: m[c]=pd.to_numeric(m[c],downcast="integer")
    d["tx"]=m
    d["rfm"]["ngay_mua_dau_tien"]=pd.to_datetime(d["rfm"]["ngay_mua_dau_tien"])
    d["anom"]["ngay_giao_dich"]=pd.to_datetime(d["anom"]["ngay_giao_dich"])
    return d

if DATA_DIR is None or not (os.path.isfile(os.path.join(DATA_DIR, "fact_transaction.csv")) or os.path.isfile(os.path.join(DATA_DIR, "fact_transaction.csv.gz"))):
    _base = os.path.dirname(os.path.abspath(__file__))
    st.error("Không tìm thấy dữ liệu (fact_transaction.csv / fact_transaction.csv.gz).")
    st.markdown(f"""**App đang nằm tại:** `{_base}`

**Cách khắc phục:** giải nén `DW_SCHEMA_VI_v2.zip` rồi đặt thư mục `DW_SCHEMA_VI`
ngay cạnh `quytusapp.py`, sao cho có đường dẫn:

`{os.path.join(_base,'DW_SCHEMA_VI','fact_transaction.csv')}`

Nếu sau khi giải nén bị lồng hai lớp (`DW_SCHEMA_VI\\DW_SCHEMA_VI\\*.csv`),
mở PowerShell và chạy:
```
cd "{os.path.join(_base,'DW_SCHEMA_VI')}"
move DW_SCHEMA_VI\\*.csv .
rmdir DW_SCHEMA_VI
```
Hoặc trỏ thẳng đường dẫn trước khi chạy:
```
$env:DW_DIR = "D:\\duong\\dan\\den\\DW_SCHEMA_VI"
streamlit run quytusapp.py
```""")
    with st.expander("Chi tiết: các vị trí đã tìm và nội dung thư mục hiện tại"):
        st.write("**Đã tìm ở:**"); st.code("\n".join(str(x) for x in _UNG_VIEN if x))
        try:
            muc = sorted(os.listdir(_base))
            st.write(f"**Nội dung `{_base}`:**"); st.code("\n".join(muc) if muc else "(trống)")
            for t in muc:
                p = os.path.join(_base, t)
                if os.path.isdir(p) and "DW" in t.upper():
                    st.write(f"**Nội dung `{t}`:**")
                    st.code("\n".join(sorted(os.listdir(p))[:20]) or "(trống)")
        except Exception as e:
            st.write(f"Không đọc được thư mục: {e}")
    st.stop()
D=load(DATA_DIR); TX,RFM,COH,ANOM=D["tx"],D["rfm"],D["cohort"],D["anom"]
WD_ORDER=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
WD_VN={"Monday":"Thứ 2","Tuesday":"Thứ 3","Wednesday":"Thứ 4","Thursday":"Thứ 5","Friday":"Thứ 6","Saturday":"Thứ 7","Sunday":"Chủ nhật"}


# ── Helpers ──────────────────────────────────────────────────────────────
def vnd(v):
    v=float(v);a=abs(v)
    if a>=1e9: return f"{v/1e9:.2f} tỷ"
    if a>=1e6: return f"{v/1e6:.1f} tr"
    if a>=1e3: return f"{v/1e3:.0f}K"
    return f"{v:.0f}"
def iint(v): return f"{int(v):,}".replace(",",".")
def dfh(n_rows,row_px=35,header_px=38,max_px=620):
    """Chieu cao dong cho st.dataframe de bang khong bi cat mat vai dong cuoi (co scroll noi bo)."""
    return int(min(header_px+row_px*max(n_rows,1),max_px))
def lay(fig,h=320,legend=False):
    fig.update_layout(height=h,margin=dict(l=56,r=18,t=14,b=44),paper_bgcolor="#fff",plot_bgcolor="#fff",
        font=dict(family="Inter",color=INK,size=12),showlegend=legend,uniformtext_minsize=8,uniformtext_mode="hide")
    fig.update_xaxes(gridcolor=LINE,zeroline=False); fig.update_yaxes(gridcolor=LINE,zeroline=False)
    return fig
def card(t,s=None,tip=None):
    b=st.container(border=True)
    tip_html=f"<span class='tip' title='{tip}'>i</span>" if tip else ""
    b.markdown(f"<div class='eyebrow'>Skincare Insight</div><div class='card-title'>{t}{tip_html}</div><div class='goldrule'></div>",unsafe_allow_html=True)
    if s: b.markdown(f"<div class='card-sub'>{s}</div>",unsafe_allow_html=True)
    return b
def hero(u,c): st.markdown(f"<div class='hero-wrap'><img src='{u}'/><div class='hero-overlay'></div><div class='hero-caption'>{c}</div></div>",unsafe_allow_html=True)
def holt_winters(y,m_=12,h=6,a=.3,b=.05,g=.3):
    """Holt-Winters cong tinh — tu cai bang numpy, khong can statsmodels."""
    y=np.asarray(y,float); n=len(y)
    if n<2*m_: return None,None
    s0=np.array([np.mean(y[i::m_][:2]) for i in range(m_)])
    L=np.mean(y[:m_]); T=(np.mean(y[m_:2*m_])-np.mean(y[:m_]))/m_
    S=list(s0-np.mean(y[:m_])); fit=[]
    for t in range(n):
        fit.append(L+T+S[t%m_] if t>=m_ else y[t])
        if t>=m_:
            Lp=L; L=a*(y[t]-S[t%m_])+(1-a)*(L+T); T=b*(L-Lp)+(1-b)*T
            S[t%m_]=g*(y[t]-L)+(1-g)*S[t%m_]
    return np.array(fit),np.array([L+(i+1)*T+S[(n+i)%m_] for i in range(h)])

def decompose(y,period=12):
    """Phan ra chuoi thoi gian: xu huong (TB truot) + mua vu + phan du."""
    y=np.asarray(y,float); n=len(y); k=period//2
    trend=np.full(n,np.nan)
    for i in range(k,n-k):
        w=np.ones(period+1); w[0]=w[-1]=.5
        trend[i]=np.sum(y[i-k:i+k+1]*w)/period
    det=y-trend; seas=np.zeros(period)
    for i in range(period):
        v=det[i::period]; v=v[~np.isnan(v)]
        seas[i]=v.mean() if len(v) else 0
    seas-=seas.mean()
    seasonal=np.array([seas[i%period] for i in range(n)])
    return trend,seasonal,y-trend-seasonal

def ols_fc(y,months,h=6):
    """Hoi quy OLS: xu huong + bien gia thang."""
    y=np.asarray(y,float); n=len(y); t=np.arange(n)
    M=pd.get_dummies(pd.Series(months),prefix="m").reindex(columns=[f"m_{i}" for i in range(1,13)],fill_value=0).values.astype(float)
    X=np.column_stack([np.ones(n),t,M]); b,*_=np.linalg.lstsq(X,y,rcond=None)
    return X@b,b,n

def barv(x,y,color,money=True):
    f=lambda v: vnd(v) if money else iint(v)
    fig=go.Figure(go.Bar(x=x,y=y,marker_color=color,text=[f(v) for v in y],textposition="outside",cliponaxis=False,
        textfont=dict(size=11,color=INK),hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>")); fig=lay(fig)
    if money: fig.update_yaxes(tickformat="~s")
    if len(y): fig.update_yaxes(range=[0,max(y)*1.2])
    return fig
def barh(labels,values,color,money=True):
    f=lambda v: vnd(v) if money else iint(v)
    fig=go.Figure(go.Bar(x=values,y=labels,orientation="h",marker_color=color,text=[f(v) for v in values],
        textposition="outside",cliponaxis=False,textfont=dict(size=11,color=INK),hovertemplate="%{y}<br>%{x:,.0f}<extra></extra>")); fig=lay(fig,360)
    if money: fig.update_xaxes(tickformat="~s")
    if len(values): fig.update_xaxes(range=[0,max(values)*1.18])
    return fig


# ── Sidebar: brand + slicer (dong bo toan bao cao) ───────────────────────
SIDE_IMG="https://images.pexels.com/photos/34939728/pexels-photo-34939728.jpeg?auto=compress&cs=tinysrgb&w=600"
st.sidebar.markdown(f"<div style='border-radius:16px;overflow:hidden;margin-bottom:10px;box-shadow:0 6px 18px rgba(43,36,32,.10)'><img src='{SIDE_IMG}' style='width:100%;height:110px;object-fit:cover;display:block;filter:saturate(.9)'/></div>",unsafe_allow_html=True)
st.sidebar.markdown("## 🌿 Skincare Insights")
_cap_css="font-size:12.5px;color:#8A7B6C;line-height:1.4;margin:2px 0 8px"
st.sidebar.markdown(f"<div style='{_cap_css}'>Data Warehouse v2 · 2022–2025<br>{len(TX):,} giao dịch · {TX.ma_khach_hang.nunique():,} khách</div>".replace(",","."),unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='{_cap_css}'>Nguồn: {os.path.basename(DATA_DIR)}</div>",unsafe_allow_html=True)

PAGES=["1 · Tổng quan Kinh doanh","2 · Hành vi Khách hàng","3 · Phân khúc Khách hàng RFM",
       "4 · Phân tích Giữ chân Khách hàng","5 · Phát hiện Bất thường","6 · Dự báo & Khuyến nghị"]
NAV=["Tổng quan","Hành vi KH","Phân khúc RFM","Giữ chân","Bất thường","Dự báo & Đề xuất"]
PAGE_TAGS=["Executive Overview · Descriptive","Customer Behavior · Descriptive","RFM Customer Segmentation · Diagnostic",
           "Cohort & Retention Analysis · Diagnostic","Anomaly Detection · Diagnostic","Predictive & Recommendation"]
HERO_IMG={
 0:("https://images.pexels.com/photos/34939732/pexels-photo-34939732.jpeg?auto=compress&cs=tinysrgb&w=1400","Bức tranh kinh doanh toàn cảnh"),
 1:("https://images.pexels.com/photos/34939704/pexels-photo-34939704.jpeg?auto=compress&cs=tinysrgb&w=1400","Từng thói quen mua sắm kể một câu chuyện"),
 2:("https://images.pexels.com/photos/34939761/pexels-photo-34939761.jpeg?auto=compress&cs=tinysrgb&w=1400","Champions, Loyal, At Risk — mỗi nhóm một chân dung"),
 3:("https://images.pexels.com/photos/34939731/pexels-photo-34939731.jpeg?auto=compress&cs=tinysrgb&w=1400","Giữ chân khách như giữ một thói quen chăm da"),
 4:("https://images.pexels.com/photos/34939730/pexels-photo-34939730.jpeg?auto=compress&cs=tinysrgb&w=1400","Soi kỹ từng giao dịch lạ"),
 5:("https://images.pexels.com/photos/34939691/pexels-photo-34939691.jpeg?auto=compress&cs=tinysrgb&w=1400","Nhìn trước một bước, chăm sóc đúng người"),
}

st.sidebar.markdown("<div class='slicer-group'>Bộ lọc đồng bộ (toàn báo cáo)</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div style='{_cap_css}'>Áp dụng cho trang 1, 2, 5. Trang 3, 4, 6 là snapshot RFM/cohort nên không lọc theo thời gian.</div>", unsafe_allow_html=True)
dmin,dmax=TX["ngay"].min().date(),TX["ngay"].max().date()
dr=st.sidebar.date_input("Khoảng thời gian",(dmin,dmax),min_value=dmin,max_value=dmax,help="Chọn ngày bắt đầu và kết thúc.")
d0,d1=dr if isinstance(dr,(list,tuple)) and len(dr)==2 else (dmin,dmax)
ALL="— Tất cả —"
def ddown(lb,col,h):
    o=sorted(TX[col].dropna().unique().tolist()); return st.sidebar.selectbox(lb,[ALL]+o,index=0,help=h)
f_chan=ddown("Kênh tiếp thị","ten_kenh_tiep_thi","Nguồn kéo khách vào gian hàng: nội sàn (Shopee Search, Shopee Ads, Shopee Live, Shopee Feed) và ngoại sàn (Affiliate/KOC, TikTok Referral, Facebook Ads, Google Ads). Việc bán hàng đều diễn ra trên Shopee.")
f_brand=ddown("Thương hiệu","ten_thuong_hieu","Hãng/thương hiệu của sản phẩm.")
st.sidebar.markdown("<div class='slicer-group'>Bộ lọc phụ</div>", unsafe_allow_html=True)
f_cat=ddown("Danh mục sản phẩm","ten_danh_muc","Cleanser, Serum, Moisturizer, Sunscreen…")
f_reg=ddown("Vùng miền","vung_mien","Miền Bắc/Trung/Nam/Tây.")
f_gender=st.sidebar.selectbox("Giới tính",[ALL,"Female","Male"],index=0,help="Lọc theo giới tính khách hàng.")
amin,amax=int(TX["tuoi"].min()),int(TX["tuoi"].max())
f_age=st.sidebar.slider("Độ tuổi khách hàng",amin,amax,(amin,amax),help="Giới hạn khoảng tuổi.")

def filt():
    df=TX[(TX["ngay"].dt.date>=d0)&(TX["ngay"].dt.date<=d1)]
    if f_chan!=ALL: df=df[df.ten_kenh_tiep_thi==f_chan]
    if f_brand!=ALL: df=df[df.ten_thuong_hieu==f_brand]
    if f_cat!=ALL: df=df[df.ten_danh_muc==f_cat]
    if f_reg!=ALL: df=df[df.vung_mien==f_reg]
    if f_gender!=ALL: df=df[df.gioi_tinh==f_gender]
    df=df[(df["tuoi"]>=f_age[0])&(df["tuoi"]<=f_age[1])]
    return df
FT=filt()
ANY_FILTER=any(v!=ALL for v in [f_chan,f_brand,f_cat,f_reg,f_gender]) or f_age!=(amin,amax)
st.sidebar.markdown("---")
st.sidebar.markdown(f"<div style='{_cap_css}'>Soft Feminine · Luxury — hồng đất, sage, vàng đồng trên nền kem.</div>", unsafe_allow_html=True)


# ── Report header + Navigation bar (6 nut) ───────────────────────────────
st.markdown(f"""<div class='report-hero'>
  <div class='logo'>🌿</div>
  <div><div class='rtitle'>SKINCARE ANALYTICS</div>
  <div class='rsub'>Phân tích hành vi &amp; phân khúc khách hàng ngành Skincare · Shopee Việt Nam 2022–2025</div></div>
  <div class='rbadge'>DP-01<br>DATN 2026</div>
</div>""", unsafe_allow_html=True)

if "pidx" not in st.session_state: st.session_state.pidx=0
ncols=st.columns(6)
for i,lbl in enumerate(NAV):
    if ncols[i].button(lbl,key=f"nav{i}",use_container_width=True,
                       type=("primary" if st.session_state.pidx==i else "secondary")):
        st.session_state.pidx=i; st.rerun()
page=PAGES[st.session_state.pidx]
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


# ═══ DASHBOARD 1 — TONG QUAN KINH DOANH ═════════════════════════════════
if page==PAGES[0]:
    st.title("Tổng quan Kinh doanh"); st.caption(PAGE_TAGS[0]); hero(*HERO_IMG[0])
    st.markdown("<div class='read'>Bức tranh kinh doanh tổng thể: bán được bao nhiêu tiền, bao nhiêu đơn, bao nhiêu khách, "
                "mạnh ở danh mục/thương hiệu/vùng/kênh nào.</div>", unsafe_allow_html=True)
    st.markdown("<div class='note'><b>Nguồn:</b> fact_transaction + các bảng chiều. <b>Đo lường:</b> Doanh thu thuần, Tổng đơn, "
                "Tổng khách, AOV, Repeat Rate, Tăng trưởng %MoM.</div>", unsafe_allow_html=True)
    if FT.empty: st.warning("Không có dữ liệu theo bộ lọc."); st.stop()
    rev=FT["doanh_thu"].sum(); orders=FT.ma_giao_dich.nunique(); custs=FT.ma_khach_hang.nunique()
    aov=rev/orders if orders else 0
    # Khach moi = khach co lan mua DAU TIEN (toan cuc, tinh tu RFM) roi vao khoang ngay da chon,
    # VA con phai xuat hien trong FT da loc (tuc thoa cac bo loc phu: kenh/thuong hieu/danh muc/vung/gioi tinh/tuoi).
    # Sua loi cu: truoc day chi loc theo ngay, bo qua cac bo loc phu -> so lieu "Khach moi" khong khop voi
    # phan con lai cua trang khi nguoi dung ap them bo loc thuong hieu/vung/... vi RFM la snapshot toan cuc.
    _cus_trong_FT=set(FT["ma_khach_hang"].unique())
    new_cust=RFM[(RFM.ngay_mua_dau_tien.dt.date>=d0)&(RFM.ngay_mua_dau_tien.dt.date<=d1)
                 &(RFM.ma_khach_hang.isin(_cus_trong_FT))].ma_khach_hang.nunique()
    # Repeat Rate ĐÚNG: tỷ lệ khách có >= 2 đơn trong tập đã lọc
    opc=FT.groupby("ma_khach_hang")["ma_giao_dich"].nunique()
    repeat_rate=(opc>=2).mean() if len(opc) else 0
    k=st.columns(6)
    k[0].metric("Doanh thu thuần",vnd(rev),help="Tổng (số lượng × đơn giá) − giảm giá.")
    k[1].metric("Tổng đơn hàng",iint(orders),help="Số mã giao dịch duy nhất.")
    k[2].metric("Tổng khách hàng",iint(custs),help="Số khách duy nhất đã mua.")
    k[3].metric("AOV",vnd(aov),help="Doanh thu ÷ số đơn.")
    k[4].metric("Khách mới",iint(new_cust),help="Khách có lần mua đầu tiên (toàn cục) nằm trong khoảng ngày đã chọn, và có xuất hiện trong tập đã lọc theo kênh/thương hiệu/danh mục/vùng/giới tính/tuổi ở thanh bên.")
    k[5].metric("Repeat Rate",f"{repeat_rate*100:.1f}%",help="Tỷ lệ khách có từ 2 đơn trở lên trong tập dữ liệu đã lọc (định nghĩa chuẩn).")
    if d0<=dmin and d1>=dmax:
        st.markdown("<div class='note' style='font-size:12.5px'>ℹ️ Khoảng ngày đang chọn là toàn bộ lịch sử nên "
                    "<b>Tổng khách hàng = Khách mới</b> là điều hợp lý (mọi khách đều có lần mua đầu tiên nằm trong "
                    "khoảng này). Thu hẹp khoảng ngày ở thanh bên (VD chỉ chọn năm 2025) để thấy hai số tách biệt.</div>",
                    unsafe_allow_html=True)

    b=card("Doanh thu thuần theo tháng","Đường xu hướng")
    mon=FT.groupby("thang_ky")["doanh_thu"].sum().sort_index()
    fig=go.Figure(go.Scatter(x=mon.index,y=mon.values,mode="lines+markers",line=dict(color=ROSE,width=3),
        fill="tozeroy",fillcolor="rgba(201,126,140,.10)",hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"))
    lay(fig,320); fig.update_yaxes(tickformat="~s"); b.plotly_chart(fig,width="stretch")

    c1,c2=st.columns(2)
    with c1:
        b=card("Tổng đơn hàng theo tháng","Bar chart"); s=FT.groupby("thang_ky")["ma_giao_dich"].nunique().sort_index()
        fig=go.Figure(go.Bar(x=s.index,y=s.values,marker_color=SAGE,hovertemplate="%{x}<br>%{y} đơn<extra></extra>")); lay(fig)
        b.plotly_chart(fig,width="stretch")
    with c2:
        b=card("Tăng trưởng doanh thu %MoM","So với tháng liền trước")
        g=mon.pct_change()*100; col=[SAGE if v>=0 else "#B5555A" for v in g.fillna(0)]
        fig=go.Figure(go.Bar(x=g.index,y=g.values,marker_color=col,text=[f"{v:.0f}%" if pd.notna(v) else "" for v in g],
            textposition="outside",cliponaxis=False,hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>")); lay(fig)
        b.plotly_chart(fig,width="stretch")

    c3,c4=st.columns(2)
    with c3:
        b=card("Doanh thu theo thương hiệu (Top 10)","dim_brand")
        s=FT.groupby("ten_thuong_hieu",observed=True)["doanh_thu"].sum().sort_values(ascending=False).head(10).iloc[::-1]
        f=barh(s.index,s.values,MAUVE); f.update_layout(margin=dict(l=140,r=50,t=14,b=40)); b.plotly_chart(f,width="stretch")
    with c4:
        b=card("Doanh thu theo danh mục","dim_category")
        s=FT.groupby("ten_danh_muc",observed=True)["doanh_thu"].sum().sort_values(ascending=False)
        b.plotly_chart(barv(s.index,s.values,ROSE),width="stretch")

    c5,c6=st.columns(2)
    with c5:
        b=card("Top 10 sản phẩm theo doanh thu","dim_product")
        s=FT.groupby("ten_san_pham")["doanh_thu"].sum().sort_values(ascending=False).head(10).iloc[::-1]
        f=barh(s.index,s.values,SAGE); f.update_layout(margin=dict(l=175,r=55,t=14,b=40)); b.plotly_chart(f,width="stretch")
    with c6:
        b=card("Doanh thu theo vùng miền","Thay cho Filled Map (schema không có toạ độ)")
        s=FT.groupby("vung_mien",observed=True)["doanh_thu"].sum().sort_values(ascending=False)
        b.plotly_chart(barv(s.index,s.values,GOLD),width="stretch")

    # ── So sanh theo Kenh tiep thi ───────────────────────────────────────
    b=card("So sánh theo Kênh tiếp thị","Doanh thu · Đơn · AOV · %DT theo từng kênh tiếp thị (bán hàng trên Shopee)",
        tip="Đây là nguồn kéo khách vào gian hàng, không phải sàn bán. Nội sàn: Shopee Search/Ads/Live/Feed. Ngoại sàn: Affiliate/KOC, TikTok Referral, Facebook Ads, Google Ads. Việc bán hàng đều trên Shopee.")
    g=FT.groupby("ten_kenh_tiep_thi",observed=True).agg(dt=("doanh_thu","sum"),od=("ma_giao_dich","nunique"))
    g["aov"]=g.dt/g.od; g["pct"]=g.dt/g.dt.sum()*100; g=g.sort_values("dt",ascending=False)
    cc1,cc2=b.columns([1.15,1])
    fig=go.Figure(go.Bar(x=g.index,y=g.dt,marker_color=ROSE,text=[vnd(v) for v in g.dt],textposition="outside",
        cliponaxis=False,textfont=dict(size=10,color=INK),hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"))
    lay(fig,320); fig.update_yaxes(tickformat="~s",range=[0,g.dt.max()*1.2]); fig.update_xaxes(tickangle=-20)
    cc1.plotly_chart(fig,width="stretch")
    tb=g.reset_index().rename(columns={"ten_kenh_tiep_thi":"Kênh"})
    tb["Doanh thu"]=tb.dt.map(vnd); tb["Đơn"]=tb.od.map(iint); tb["AOV"]=tb.aov.map(vnd); tb["% DT"]=tb.pct.map(lambda v:f"{v:.1f}%")
    cc2.dataframe(tb[["Kênh","Doanh thu","Đơn","AOV","% DT"]],width="stretch",hide_index=True)

    # ── Khách mới vs khách quay lại: bằng chứng cho luận điểm "sống nhờ khách cũ"
    b=card("Doanh thu từ khách mới vs khách quay lại","Tách doanh thu mỗi tháng theo khách mua lần đầu và khách đã từng mua",
        tip="Đơn của một khách được tính là 'khách mới' nếu rơi vào đúng tháng họ mua lần đầu; các tháng sau tính là 'quay lại'. Tỷ trọng khách quay lại cao chứng minh doanh nghiệp sống nhờ giữ chân.")
    _f=FT.groupby("ma_khach_hang")["ngay"].min()
    _tmp=FT[["ma_khach_hang","ngay","doanh_thu","thang_ky"]].copy()
    _tmp["la_moi"]=_tmp["ngay"].dt.to_period("M").values==_tmp["ma_khach_hang"].map(_f).dt.to_period("M").values
    gg=_tmp.groupby(["thang_ky","la_moi"])["doanh_thu"].sum().unstack(fill_value=0).sort_index()
    _moi=gg[True] if True in gg.columns else pd.Series(0,index=gg.index)
    _cu =gg[False] if False in gg.columns else pd.Series(0,index=gg.index)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=gg.index,y=_cu.values,name="Khách quay lại",mode="lines",stackgroup="one",
        line=dict(width=.5,color=ROSE),fillcolor="rgba(201,126,140,.55)",hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=gg.index,y=_moi.values,name="Khách mới",mode="lines",stackgroup="one",
        line=dict(width=.5,color=SAGE),fillcolor="rgba(143,174,150,.55)",hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"))
    lay(fig,330,legend=True); fig.update_yaxes(tickformat="~s")
    fig.update_xaxes(tickmode="array",tickvals=list(gg.index[::3]))
    b.plotly_chart(fig,width="stretch")
    _tm,_tc=_moi.sum(),_cu.sum(); _tt=_tm+_tc
    _l12=gg.tail(12); _p12=(_l12[False].sum()/_l12.sum().sum()*100) if False in _l12.columns and _l12.sum().sum()>0 else 0
    if _tt>0:
        b.markdown(f"<div class='read' style='margin-top:6px'><b>Khách quay lại tạo {_tc/_tt*100:.1f}% doanh thu</b> "
                   f"({vnd(_tc)}), khách mới chỉ {_tm/_tt*100:.1f}% ({vnd(_tm)}). Riêng 12 tháng gần nhất, tỷ trọng khách quay lại "
                   f"đạt {_p12:.1f}% — doanh thu phụ thuộc chủ yếu vào việc giữ chân, không phải thu hút mới.</div>",
                   unsafe_allow_html=True)


# ═══ DASHBOARD 2 — HANH VI KHACH HANG ═══════════════════════════════════
elif page==PAGES[1]:
    st.title("Hành vi Khách hàng"); st.caption(PAGE_TAGS[1]); hero(*HERO_IMG[1])
    st.markdown("<div class='read'>Khách mua như thế nào: bao nhiêu lần, mỗi đơn bao nhiêu sản phẩm, chi bao nhiêu, "
                "mua ngày nào trong tuần, và phản ứng ra sao với khuyến mãi.</div>", unsafe_allow_html=True)
    st.markdown("<div class='note'><b>Nguồn:</b> fact_transaction + dim_date + mart_customer_rfm. <b>Đo lường:</b> Purchase Frequency, "
                "Avg Basket Size, Average Discount, Avg Revenue/Customer, Days Between Purchases.</div>", unsafe_allow_html=True)
    if FT.empty: st.warning("Không có dữ liệu."); st.stop()
    freq=RFM["tan_suat_mua"].mean(); basket=FT["so_luong"].sum()/FT.ma_giao_dich.nunique()
    disc=FT["so_tien_giam_gia"].mean(); arpc=RFM["tong_chi_tieu"].mean()
    # Days Between Purchases: PHAI tinh rieng cho tung khach (tuoi_tho / (tan_suat-1)) roi moi lay
    # trung binh — KHONG duoc lay ty le cua 2 so trung binh cong (mean(A)/mean(B)) nhu cach cu, vi
    # 2 cach nay cho ra ket qua LECH NHAU DANG KE (da kiem chung: cach cu ra ~47 ngay, cach dung ra
    # ~61 ngay). Cach cu bi thien lech ve phia nhom khach mua tan suat cao (return dai han cua ho keo
    # trung binh chung xuong thap gia tao), khong dai dien cho khach hang dien hinh.
    _sub_days=RFM[RFM["tan_suat_mua"]>1].copy()
    _sub_days["_days_per_cust"]=_sub_days["tuoi_tho_khach_hang"]/(_sub_days["tan_suat_mua"]-1)
    days=_sub_days["_days_per_cust"].mean()
    k=st.columns(5)
    k[0].metric("Purchase Frequency (TB)",f"{freq:.2f}",help="Số lần mua TB mỗi khách.")
    k[1].metric("Avg Basket Size",f"{basket:.2f}",help="Số sản phẩm TB mỗi đơn.")
    k[2].metric("Average Discount",vnd(disc),help="Giảm giá TB mỗi dòng giao dịch.")
    k[3].metric("Avg Revenue/Customer",vnd(arpc),help="Chi tiêu TB mỗi khách (vòng đời).")
    k[4].metric("Days Between Purchases",f"{days:.0f} ngày",
                help="Tính riêng cho từng khách có ≥2 đơn (tuổi thọ khách hàng ÷ số khoảng cách giữa các lần mua), rồi lấy trung bình trên toàn bộ các khách đó — không dùng tỷ lệ của 2 số trung bình cộng vì cách đó bị thiên lệch.")

    b=card("Phân bố tần suất mua","Số khách theo từng mức tần suất mua trọn vòng đời (mart_customer_rfm)",
        tip="Phần lớn khách chỉ mua 1-2 lần; cột cuối gộp toàn bộ khách mua từ ngưỡng bách phân vị 99 trở lên (nhóm trung thành mua rất nhiều lần) để tránh trục ngang bị kéo dài do vài khách mua tới 64 lần. Đây là bức tranh tổng quan trước khi đi sâu vào từng phân khúc RFM ở Trang 3.")
    _p99=int(RFM["tan_suat_mua"].quantile(.99))
    _fr_capped=RFM["tan_suat_mua"].clip(upper=_p99)
    _vc=_fr_capped.value_counts().sort_index()
    _labels=[str(i) for i in _vc.index[:-1]]+[f"{_p99}+"]
    fig=go.Figure(go.Bar(x=_labels,y=_vc.values,marker_color=MAUVE,
        hovertemplate="%{x} lần mua<br>%{y:,} khách<extra></extra>"))
    lay(fig,300); fig.update_xaxes(title=f"Số lần mua (gộp {_p99}+ ở cột cuối)",dtick=2); fig.update_yaxes(title="Số khách")
    b.plotly_chart(fig,width="stretch")

    c1,c2=st.columns(2)
    with c1:
        b=card("Phân bố giá trị đơn hàng","Histogram")
        ov=FT.groupby("ma_giao_dich")["doanh_thu"].sum(); cnt,edg=np.histogram(ov.values,bins=30)
        fig=go.Figure(go.Bar(x=[(edg[i]+edg[i+1])/2 for i in range(len(edg)-1)],y=cnt,marker_color=SKY))
        lay(fig); fig.update_xaxes(tickformat="~s",title="Giá trị đơn"); fig.update_yaxes(title="Số đơn"); b.plotly_chart(fig,width="stretch")
    with c2:
        b=card("Phân bố số lượng sản phẩm mỗi đơn","Histogram — Avg Basket Size ở trên là số trung bình, đây là toàn bộ phân phối")
        cnt,edg=np.histogram(FT["so_luong"].values,bins=range(1,int(FT["so_luong"].max())+2))
        fig=go.Figure(go.Bar(x=[(edg[i]+edg[i+1])/2 for i in range(len(edg)-1)],y=cnt,marker_color=GOLD,
            hovertemplate="%{x:.0f} sản phẩm/đơn<br>%{y:,} đơn<extra></extra>"))
        lay(fig); fig.update_xaxes(title="Số sản phẩm/đơn",dtick=1); fig.update_yaxes(title="Số đơn"); b.plotly_chart(fig,width="stretch")

    c3,c4=st.columns(2)
    with c3:
        b=card("Số đơn theo ngày trong tuần","dim_date[ten_thu]")
        s=FT.groupby("ten_thu",observed=True)["ma_giao_dich"].nunique().reindex(WD_ORDER).fillna(0)
        fig=go.Figure(go.Bar(x=[WD_VN[w] for w in WD_ORDER],y=s.values,marker_color=MAUVE,text=[iint(v) for v in s.values],
            textposition="outside",cliponaxis=False)); lay(fig); b.plotly_chart(fig,width="stretch")
    with c4:
        b=card("Doanh thu theo giới tính","dim_customer[gioi_tinh] — % trên tổng doanh thu")
        s=FT.groupby("gioi_tinh",observed=True)["doanh_thu"].sum().sort_values(ascending=False)
        fig=go.Figure(go.Pie(labels=s.index,values=s.values,hole=.55,marker=dict(colors=[ROSE,SKY,GOLD,MAUVE][:len(s)]),
            textinfo="label+percent",textfont=dict(size=13),hovertemplate="%{label}<br>%{value:,.0f}đ (%{percent})<extra></extra>"))
        lay(fig,320); b.plotly_chart(fig,width="stretch")

    b=card("Doanh thu theo nhóm tuổi","dim_customer[tuoi], chia nhóm 5 năm")
    bins=list(range(15,65,5)); labs=[f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins)-1)]
    FTa=FT.copy(); FTa["nhom_tuoi"]=pd.cut(FTa["tuoi"],bins=bins,labels=labs,right=False)
    s=FTa.groupby("nhom_tuoi",observed=True)["doanh_thu"].sum()
    b.plotly_chart(barv(s.index.astype(str),s.values,GOLD),width="stretch")

    # ── Ảnh hưởng khuyến mãi & tương quan: bằng chứng "giảm sâu không tăng giỏ hàng"
    cc1,cc2=st.columns(2)
    with cc1:
        b=card("Ảnh hưởng khuyến mãi lên giá trị đơn","Giá trị đơn trung bình theo từng mức giảm giá",
            tip="Nếu giảm giá sâu thực sự kích thích mua nhiều hơn, cột bên phải phải cao hơn cột bên trái. Thực tế lại ngược lại.")
        _g=FT["don_gia"]*FT["so_luong"]
        _t=np.where(_g>0,FT["so_tien_giam_gia"]/_g,0)
        _bk=pd.cut(_t,bins=[-.001,.0001,.05,.10,.20,1.],labels=["0%","0-5%","5-10%","10-20%",">20%"])
        _de=FT.assign(bk=_bk).groupby("bk",observed=True)["doanh_thu"].mean().reindex(["0%","0-5%","5-10%","10-20%",">20%"]).dropna()
        fig=go.Figure(go.Bar(x=_de.index.astype(str),y=_de.values,marker_color=[SAGE,SAGE,GOLD,"#C9925A",ROSE][:len(_de)],
            text=[vnd(v) for v in _de.values],textposition="outside",cliponaxis=False,textfont=dict(size=11,color=INK),
            hovertemplate="Giảm %{x}<br>AOV %{y:,.0f}<extra></extra>"))
        lay(fig,320); fig.update_yaxes(tickformat="~s",range=[0,_de.max()*1.25]); fig.update_xaxes(title="Mức giảm giá")
        b.plotly_chart(fig,width="stretch")
        if len(_de)>=2:
            b.markdown(f"<div class='warn' style='margin-top:6px'>Đơn không giảm giá đạt {vnd(_de.iloc[0])}, "
                       f"nhưng đơn giảm sâu nhất chỉ còn {vnd(_de.iloc[-1])} — giảm "
                       f"<b>{(1-_de.iloc[-1]/_de.iloc[0])*100:.0f}%</b>. Khuyến mãi mạnh không làm giỏ hàng lớn hơn.</div>",
                       unsafe_allow_html=True)
    with cc2:
        b=card("Ma trận tương quan các yếu tố","Hệ số Pearson giữa giá, số lượng, mức giảm và doanh thu",
            tip="Giá trị gần +1: cùng tăng. Gần −1: ngược chiều. Gần 0: gần như không liên quan.")
        _cor=FT.assign(ty_le_giam=_t)[["don_gia","so_luong","ty_le_giam","doanh_thu","tuoi"]].corr()
        _nh=["Đơn giá","Số lượng","Tỷ lệ giảm","Doanh thu","Tuổi"]
        fig=go.Figure(go.Heatmap(z=_cor.values,x=_nh,y=_nh,colorscale=[[0,"#C9925A"],[.5,"#FBF6F1"],[1,ROSE]],
            zmid=0,text=np.round(_cor.values,2),texttemplate="%{text}",textfont=dict(size=11),
            colorbar=dict(thickness=10)))
        lay(fig,320); b.plotly_chart(fig,width="stretch")
        b.markdown(f"<div class='read' style='margin-top:6px'>Doanh thu gắn chặt với đơn giá "
                   f"({_cor.loc['don_gia','doanh_thu']:.2f}) và số lượng ({_cor.loc['so_luong','doanh_thu']:.2f}), "
                   f"nhưng tỷ lệ giảm giá lại tương quan <b>{_cor.loc['ty_le_giam','doanh_thu']:.2f}</b> — "
                   f"gần như không đóng góp tích cực.</div>", unsafe_allow_html=True)
    st.markdown("<div class='warn'>Ghi chú: mỗi giao dịch chỉ gồm 1 sản phẩm nên chưa phân tích “mua kèm” (market basket); "
                "schema cũng không có mốc giờ nên không vẽ “khung giờ mua”.</div>", unsafe_allow_html=True)


# ═══ DASHBOARD 3 — RFM ══════════════════════════════════════════════════
elif page==PAGES[2]:
    st.title("Phân khúc Khách hàng RFM"); st.caption(PAGE_TAGS[2]); hero(*HERO_IMG[2])
    st.markdown("<div class='read'>Chia khách thành 9 nhóm theo hành vi (mua gần đây · thường xuyên · chi nhiều) để biết nhóm nào đông, "
                "nhóm nào tạo nhiều tiền nhất.</div>", unsafe_allow_html=True)
    st.markdown("<div class='note'><b>Nguồn:</b> mart_customer_rfm (snapshot 31/12/2025 — không lọc theo thời gian).</div>", unsafe_allow_html=True)
    tot_c=RFM.ma_khach_hang.nunique(); tot_m=RFM["tong_chi_tieu"].sum()
    agg=(RFM.groupby("phan_khuc_rfm").agg(n=("ma_khach_hang","nunique"),m=("tong_chi_tieu","sum"))
         .assign(pct_kh=lambda x:x.n/tot_c*100,pct_dt=lambda x:x.m/tot_m*100).sort_values("m",ascending=False))
    ch_kh=agg.loc["Champions","pct_kh"]; ch_dt=agg.loc["Champions","pct_dt"]
    k=st.columns(4)
    k[0].metric("Tổng khách hàng",iint(tot_c)); k[1].metric("Tổng doanh thu (RFM)",vnd(tot_m))
    k[2].metric("Champions % khách",f"{ch_kh:.1f}%"); k[3].metric("Champions % doanh thu",f"{ch_dt:.1f}%")
    st.markdown(f"<div class='risk'>⚠️ <b>Rủi ro tập trung doanh thu:</b> nhóm Champions chỉ chiếm <b>{ch_kh:.1f}%</b> số khách "
                f"nhưng tạo tới <b>{ch_dt:.1f}%</b> doanh thu. Doanh nghiệp đang phụ thuộc lớn vào một nhóm nhỏ — nếu họ rời bỏ, "
                f"doanh thu sụt mạnh. Cần vừa giữ chân Champions (VIP), vừa nuôi các nhóm kế cận (Loyal, Potential) để giảm phụ thuộc.</div>", unsafe_allow_html=True)

    SEG_DESC={
        "Champions":("Mua rất gần đây, thường xuyên và chi nhiều nhất","R↑ F↑ M↑","Khách quý giá nhất — tri ân, ưu đãi độc quyền, early-access."),
        "Loyal Customers":("Mua thường xuyên, chi tiêu ổn định, gắn bó","F↑ M↑","Upsell/cross-sell, chương trình thành viên."),
        "Potential Loyalists":("Mới mua gần đây, tần suất khá — tiềm năng lên trung thành","R↑ F↔","Khuyến khích mua lặp lại, ưu đãi nâng hạng."),
        "Recent Customers":("Vừa mua lần đầu gần đây, tần suất còn thấp","R↑ F↓","Onboarding, hướng dẫn routine, voucher mua lần 2."),
        "Need Attention":("Giá trị trung bình, đang có dấu hiệu giảm tương tác","R↔ F↔","Nhắc nhở, ưu đãi nhẹ để tăng tần suất."),
        "At Risk":("Từng chi nhiều nhưng đã lâu chưa quay lại","R↓ M↑","Win-back mạnh, remarketing trong 7–14 ngày."),
        "Cant Lose Them":("Khách giá trị cao nhưng rất lâu không mua","R↓↓ M↑↑","Chăm sóc cá nhân hoá — không được để mất."),
        "Hibernating":("Lâu không mua, tần suất & chi tiêu thấp","R↓ F↓ M↓","Chiến dịch tái kích hoạt chi phí thấp."),
        "Lost":("Rời bỏ đã lâu, gần như không còn hoạt động","R↓↓ F↓↓","Tái kích hoạt chi phí thấp; dừng nếu không phản hồi."),
    }
    # Chips co tooltip (title=) cho tung phan khuc
    chips="".join(
        f"<span title=\"{v[0]} · {v[1]} · {v[2]}\" style='display:inline-block;background:#fff;border:1px solid {LINE};"
        f"border-left:4px solid {ROSE};border-radius:9px;padding:4px 9px;margin:3px 6px 3px 0;font-size:12px;color:{INK};cursor:help'>"
        f"<b>{k}</b> <span style='color:{MUTED};font-size:10.5px'>{v[1]}</span></span>"
        for k,v in SEG_DESC.items())
    st.markdown(f"<div style='margin:2px 0 12px'>{chips}</div>", unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1:
        b=card("Treemap: phân khúc theo tổng chi tiêu","phan_khuc_rfm × tong_chi_tieu",
            tip="RFM = Recency (mua gần đây), Frequency (thường xuyên), Monetary (chi nhiều). Ô càng lớn = đóng góp DT càng nhiều.")
        fig=go.Figure(go.Treemap(labels=agg.index,parents=[""]*len(agg),values=agg["m"],marker=dict(colors=PAL*3),
            texttemplate="%{label}<br>%{value:,.0f}<br>%{percentRoot}")); lay(fig,360); b.plotly_chart(fig,width="stretch")
    with c2:
        b=card("Doanh thu theo phân khúc (giảm dần)","SUM(tong_chi_tieu)")
        b.plotly_chart(barv(agg.index,agg["m"].values,ROSE).update_xaxes(tickangle=-25),width="stretch")

    c3,c4=st.columns(2)
    with c3:
        b=card("Donut: tỷ trọng khách theo phân khúc","% khách hàng")
        fig=go.Figure(go.Pie(labels=agg.index,values=agg["n"],hole=.55,marker=dict(colors=PAL*3),textinfo="label+percent",textfont=dict(size=10)))
        lay(fig,360); b.plotly_chart(fig,width="stretch")
    with c4:
        b=card("Scatter: điểm R × tổng chi tiêu","size=tan_suat_mua, màu=phân khúc")
        samp=RFM.sample(min(4000,len(RFM)),random_state=1); fig=go.Figure()
        for i,seg in enumerate(sorted(samp.phan_khuc_rfm.unique())):
            dd=samp[samp.phan_khuc_rfm==seg]
            fig.add_trace(go.Scatter(x=dd["diem_R"],y=dd["tong_chi_tieu"],mode="markers",name=seg,
                marker=dict(size=np.clip(dd["tan_suat_mua"]*2,4,18),color=PAL[i%len(PAL)],opacity=.6),
                hovertemplate=f"{seg}<br>R=%{{x}}<br>%{{y:,.0f}}<extra></extra>"))
        lay(fig,360,legend=True); fig.update_xaxes(title="diem_R"); fig.update_yaxes(title="tong_chi_tieu",tickformat="~s")
        fig.update_layout(legend=dict(font=dict(size=8))); b.plotly_chart(fig,width="stretch")

    b=card("Matrix Heatmap: điểm R × điểm F = số khách","diem_R (hàng) × diem_F (cột)",
        tip="Điểm R/F từ 1–5 (5 tốt nhất). Ô càng đậm = càng nhiều khách ở tổ hợp điểm đó.")
    mat=RFM.pivot_table(index="diem_R",columns="diem_F",values="ma_khach_hang",aggfunc="count").sort_index(ascending=False)
    fig=go.Figure(go.Heatmap(z=mat.values,x=[f"F{c}" for c in mat.columns],y=[f"R{r}" for r in mat.index],
        colorscale=[[0,"#F7ECEA"],[1,ROSE]],text=mat.values,texttemplate="%{text}",colorbar=dict(title="Số KH",thickness=10)))
    lay(fig,340); b.plotly_chart(fig,width="stretch")

    b=card("Tần suất mua trung bình theo phân khúc","mart_customer_rfm — kiểm chứng phân khúc có tách bạch đúng theo hành vi mua thật không",
        tip="Nếu định nghĩa phân khúc hợp lý, Champions/Loyal phải có tần suất mua trung bình cao hơn hẳn At Risk/Lost/Hibernating — biểu đồ này xác nhận điều đó bằng số liệu.")
    _fseg=RFM.groupby("phan_khuc_rfm")["tan_suat_mua"].mean().sort_values(ascending=False)
    fig=go.Figure(go.Bar(x=_fseg.index,y=_fseg.values,marker_color=SAGE,text=[f"{v:.1f}" for v in _fseg.values],
        textposition="outside",cliponaxis=False,hovertemplate="%{x}<br>TB %{y:.2f} lần mua<extra></extra>"))
    lay(fig,300); fig.update_xaxes(tickangle=-25); fig.update_yaxes(title="Số lần mua TB")
    b.plotly_chart(fig,width="stretch")

    disp=agg.reset_index().rename(columns={"phan_khuc_rfm":"Phân khúc","n":"Số khách"})
    disp["% khách"]=disp["pct_kh"].map(lambda v:f"{v:.1f}%"); disp["% doanh thu"]=disp["pct_dt"].map(lambda v:f"{v:.1f}%"); disp["Doanh thu"]=disp["m"].map(vnd)

    # ── Pareto & AOV theo phân khúc: định lượng mức độ tập trung doanh thu
    cc1,cc2=st.columns(2)
    with cc1:
        b=card("Pareto: mức độ tập trung doanh thu","Xếp khách từ chi nhiều đến chi ít, cộng dồn % doanh thu",
            tip="Trục ngang: % khách hàng (đã xếp hạng theo chi tiêu). Trục dọc: % doanh thu tích lũy. Đường chạm mốc 80% càng sớm thì doanh thu càng tập trung vào nhóm nhỏ.")
        _cr=RFM.set_index("ma_khach_hang")["tong_chi_tieu"].sort_values(ascending=False)
        _cum=_cr.cumsum()/_cr.sum()*100
        _xp=np.arange(1,len(_cr)+1)/len(_cr)*100
        _step=max(1,len(_cr)//600)
        _i80=int(np.searchsorted(_cum.values,80)); _p80=_xp[min(_i80,len(_xp)-1)]
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=_xp[::_step],y=_cum.values[::_step],mode="lines",line=dict(color=ROSE,width=3),
            fill="tozeroy",fillcolor="rgba(201,126,140,.10)",name="DT tích lũy",
            hovertemplate="%{x:.0f}% khách<br>%{y:.1f}% doanh thu<extra></extra>"))
        fig.add_hline(y=80,line=dict(color=GOLD,dash="dot",width=2))
        fig.add_vline(x=_p80,line=dict(color=GOLD,dash="dot",width=2))
        fig.add_annotation(x=_p80,y=80,text=f"{_p80:.1f}% khách → 80% DT",showarrow=True,arrowhead=2,
            ax=70,ay=-30,font=dict(size=11,color=GOLD),arrowcolor=GOLD)
        lay(fig,320); fig.update_xaxes(title="% khách hàng (xếp theo chi tiêu)",range=[0,100])
        fig.update_yaxes(title="% doanh thu tích lũy",range=[0,102])
        b.plotly_chart(fig,width="stretch")
        _top20=_cum.values[min(int(len(_cr)*.2),len(_cum)-1)]
        b.markdown(f"<div class='read' style='margin-top:6px'>Chỉ <b>{_p80:.1f}%</b> khách hàng tạo ra 80% doanh thu; "
                   f"nhóm top 20% đóng góp <b>{_top20:.1f}%</b>. Đây là định lượng cho rủi ro tập trung nêu ở đầu trang.</div>",
                   unsafe_allow_html=True)
    with cc2:
        b=card("Giá trị đơn trung bình theo phân khúc","So sánh AOV giữa 9 nhóm khách",
            tip="Cho biết nhóm nào chi mạnh mỗi lần mua — khác với tổng chi tiêu vốn phụ thuộc số lần mua.")
        _a=RFM.groupby("phan_khuc_rfm")["gia_tri_don_hang_tb"].mean().sort_values(ascending=False)
        fig=go.Figure(go.Bar(x=_a.index,y=_a.values,marker_color=ROSE,text=[vnd(v) for v in _a.values],
            textposition="outside",cliponaxis=False,textfont=dict(size=10,color=INK),
            hovertemplate="%{x}<br>AOV %{y:,.0f}<extra></extra>"))
        lay(fig,320); fig.update_yaxes(tickformat="~s",range=[0,_a.max()*1.25]); fig.update_xaxes(tickangle=-25)
        b.plotly_chart(fig,width="stretch")

    # Bang chi tiet 9 phan khuc dat CUOI TRANG (theo yeu cau) — tao card va do du lieu ngay tai day
    # (khac voi lan sua truoc: lan do chi doi ".dataframe()" ma khong doi vi tri goi card() nen
    # bang van nam o cho cu, vi vi tri container duoc co dinh luc goi card(), khong phai luc ghi du lieu).
    b_tbl_rfm=card("Bảng 9 phân khúc RFM","Số khách · % khách · % doanh thu — bảng tổng hợp sau khi đã xem qua các biểu đồ trực quan ở trên")
    b_tbl_rfm.dataframe(disp[["Phân khúc","Số khách","% khách","Doanh thu","% doanh thu"]],width="stretch",hide_index=True,height=dfh(len(disp)))


# ═══ DASHBOARD 4 — COHORT ═══════════════════════════════════════════════
elif page==PAGES[3]:
    st.title("Phân tích Giữ chân Khách hàng"); st.caption(PAGE_TAGS[3]); hero(*HERO_IMG[3])
    st.markdown("<div class='read'>Nhóm khách mua lần đầu ở mỗi tháng, sau đó bao nhiêu % còn quay lại. Với skincare, retention thường "
                "giảm mạnh sau ~3 tháng khi hết chu kỳ dùng sản phẩm đầu tiên.</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='note'><b>Nguồn:</b> mart_cohort_retention ({COH.thang_cohort.nunique()} cohort). Matrix retention + Retention Curve.</div>", unsafe_allow_html=True)
    k=st.columns(3)
    # Cohort Size (TB): PHAI lay tung cohort MOT LAN (drop_duplicates) roi moi tinh trung binh.
    # Loi cu: COH['quy_mo_cohort'].mean() tinh truc tiep tren toan bo 1.176 dong cua mart, nhung
    # quy_mo_cohort la HANG SO lap lai o moi ky (M0,M1,M2...) cho cung 1 cohort -> cohort cang CU
    # (co nhieu ky duoc theo doi hon, VD cohort 2022-01 co 48 dong) vo tinh duoc "dem" nhieu lan hon
    # cohort MOI (VD cohort 2025-12 chi co 1 dong vi chua co thang nao sau de theo doi) -> ket qua
    # trung binh bi lech ve phia quy mo cua cac cohort cu, sai ~8% so voi trung binh dung.
    k[0].metric("Retention Rate (TB)",f"{COH['ty_le_giu_chan'].mean()*100:.1f}%")
    k[1].metric("Cohort Size (TB)",f"{COH.drop_duplicates('thang_cohort')['quy_mo_cohort'].mean():.0f}",
                help="Trung bình quy mô của MỖI cohort (mỗi cohort tính đúng 1 lần, không lặp lại theo số kỳ theo dõi).")
    k[2].metric("Số cohort",iint(COH['thang_cohort'].nunique()))
    COH2=COH.copy(); COH2["nam_cohort"]=COH2["thang_cohort"].astype(str).str[:4]; years=sorted(COH2["nam_cohort"].unique())
    yc=st.container(border=True)
    yc.markdown("<div class='slicer-group' style='margin-top:0'>Lọc theo năm cohort</div>", unsafe_allow_html=True)
    sel_years=yc.multiselect("Năm cohort",years,default=years,help="Chọn năm để chỉ xem cohort bắt đầu mua trong năm đó.")
    COH_y=COH2[COH2["nam_cohort"].isin(sel_years)] if sel_years else COH2
    cohorts=sorted(COH_y["thang_cohort"].unique())
    if not cohorts: st.warning("Không có cohort theo năm đã chọn."); st.stop()
    # Hien thi TOAN BO cohort trong (cac) nam da chon — KHONG cat cung o 12 cohort gan nhat nua.
    # Loi cu: n_show=min(12,len(cohorts)) roi lay cohorts[-n_show:] luon lay 12 cohort GAN NHAT
    # theo thoi gian bat ke nguoi dung da chon nam nao -> chon 2 nam (VD 2022+2023 = 24 cohort)
    # van chi hien 12 cohort cuoi (toan bo la nam sau), nam truoc bi an mat du da duoc chon.
    sel=cohorts; kmax=int(COH_y["ky_cohort"].max()); max_k=min(12,kmax)
    sub=COH_y[(COH_y["thang_cohort"].isin(sel))&(COH_y["ky_cohort"]<=max_k)]
    mat=sub.pivot(index="thang_cohort",columns="ky_cohort",values="ty_le_giu_chan")*100
    _heat_h=int(max(320,min(34*len(sel)+90,1400)))  # chieu cao co dan theo so cohort, tranh bi bop met khi chon nhieu nam

    b=card("Matrix Retention (Heatmap)",f"Hàng=cohort ({len(sel)} cohort trong các năm đã chọn), Cột=kỳ, Giá trị=% giữ chân",
        tip="Mỗi hàng theo dõi 1 nhóm khách qua các kỳ; màu càng đậm khách càng quay lại nhiều.")
    fig=go.Figure(go.Heatmap(z=mat.values,x=[f"M{c}" for c in mat.columns],y=[str(i) for i in mat.index],
        colorscale=[[0,"#F4F7F5"],[1,SAGE]],text=mat.values,texttemplate="%{text:.0f}",textfont=dict(size=9),colorbar=dict(title="%",thickness=10)))
    lay(fig,_heat_h)
    # QUAN TRONG: ep truc Y thanh 'category' (khong de Plotly tu suy doan la truc thoi gian lien tuc).
    # Neu khong ep kieu, khi nguoi dung chon nam KHONG LIEN TUC (VD 2022+2023+2025, bo qua 2024),
    # Plotly se tu nhan dien nhan "Jan 2022","Jul 2022"... la chuoi ngay thang roi ve truc theo
    # KHOANG CACH THOI GIAN THUC te -> tao ra 1 khoang trang lon o vi tri nam 2024 dai duoc chon,
    # dan den bang nhiet bi "gay khuc" nhin nhu thieu du lieu dù thuc chat du lieu van du.
    fig.update_yaxes(type="category",autorange="reversed")
    fig.update_xaxes(title="Kỳ (tháng kể từ cohort)")
    b.plotly_chart(fig,width="stretch")

    b=card("Retention Curve","Đường đậm = trung bình các cohort · đường mảnh = từng cohort",
        tip="Đường hồng đậm là mức giữ chân trung bình theo kỳ, kèm nhãn %.")
    smooth_on=b.checkbox("Làm mượt đường trung bình (trung bình trượt 3 kỳ)",value=False,
        help="Bật để xem xu hướng tổng quát rõ hơn, bớt nhiễu do cỡ mẫu cohort nhỏ ở các kỳ xa.",key="smooth_ret")
    fig=go.Figure()
    for ch in sel:
        dd=sub[sub["thang_cohort"]==ch].sort_values("ky_cohort")
        fig.add_trace(go.Scatter(x=dd["ky_cohort"],y=dd["ty_le_giu_chan"]*100,mode="lines",showlegend=False,
            line=dict(width=1,color="rgba(138,123,108,.28)"),hovertemplate=ch+" · M%{x}<br>%{y:.1f}%<extra></extra>"))
    avg=sub.groupby("ky_cohort")["ty_le_giu_chan"].mean().sort_index()*100
    fig.add_trace(go.Scatter(x=avg.index,y=avg.values,mode="lines+markers+text",name="Trung bình cohort",line=dict(width=4,color=ROSE),
        marker=dict(size=7,color=ROSE),text=[f"{v:.0f}%" for v in avg.values],textposition="top center",textfont=dict(size=11,color=INK),
        cliponaxis=False,hovertemplate="Kỳ M%{x}<br>TB %{y:.1f}%<extra></extra>"))
    if smooth_on and len(avg)>=3:
        sm=avg.rolling(3,min_periods=1,center=True).mean()
        fig.add_trace(go.Scatter(x=sm.index,y=sm.values,mode="lines",name="Trung bình trượt (3 kỳ)",
            line=dict(width=2.5,color=GOLD,dash="dot"),hovertemplate="Kỳ M%{x}<br>TB trượt %{y:.1f}%<extra></extra>"))
    lay(fig,380,legend=True); fig.update_xaxes(title="Kỳ (tháng kể từ lần mua đầu)")
    fig.update_yaxes(title="% giữ chân",range=[0,max(100,avg.max()*1.15 if len(avg) else 100)]); b.plotly_chart(fig,width="stretch")
    if len(avg):
        b.markdown(f"<div class='read' style='margin-top:6px'>Trung bình {len(sel)} cohort đã chọn: giữ chân {avg.iloc[0]:.0f}% kỳ đầu, "
                   f"còn <b>{avg.iloc[-1]:.0f}%</b> ở kỳ M{int(avg.index[-1])}.</div>", unsafe_allow_html=True)
        # Phat hien hien tuong khong giam don dieu (bounce). Kiem tra CA HAI muc:
        # (1) duong TRUNG BINH hien thi tren bieu do — de biet nguoi xem co dang thay hien tuong nay khong.
        # (2) TUNG cohort rieng le trong "sel" — vi trung binh nhieu cohort co the trieu tieu bounce cua nhau
        #     (da kiem chung: du lieu tho tung cohort, vi du 1 thang, co buoc nhay M2/M6 du am tinh trung binh lai muot).
        _diffs=avg.diff().dropna()
        _bounce_avg=[int(i) for i,v in _diffs.items() if v>0.5 and i<=6]
        _n_bounce_cohort=0
        for ch in sel:
            dd=sub[sub["thang_cohort"]==ch].sort_values("ky_cohort")
            dv=dd["ty_le_giu_chan"].values*100
            if len(dv)>3 and np.any(np.diff(dv[:7])>0.5): _n_bounce_cohort+=1
        _pct_bounce=_n_bounce_cohort/len(sel)*100 if sel else 0
        if _bounce_avg:
            b.markdown(f"<div class='warn' style='margin-top:6px'>⚠️ <b>Lưu ý chất lượng dữ liệu:</b> ngay cả đường "
                       f"<b>trung bình</b> cũng tăng nhẹ trở lại ở kỳ M{', M'.join(map(str,_bounce_avg))} thay vì giảm đơn điệu. "
                       f"Đây là đặc điểm của dữ liệu nguồn <code>mart_cohort_retention</code> (không phải lỗi tính toán trong "
                       f"dashboard) — nên đối chiếu lại logic sinh mart trước khi dùng số này để ra quyết định.</div>", unsafe_allow_html=True)
        elif _pct_bounce>=30:
            b.markdown(f"<div class='warn' style='margin-top:6px'>⚠️ <b>Lưu ý chất lượng dữ liệu:</b> đường trung bình đang hiển thị "
                       f"mượt và giảm dần, nhưng <b>{_n_bounce_cohort}/{len(sel)} cohort ({_pct_bounce:.0f}%)</b> khi xét riêng lẻ "
                       f"lại có tỷ lệ giữ chân tăng nhẹ trở lại ở một vài kỳ giữa (xem chi tiết trong Matrix Retention phía trên) — "
                       f"hiện tượng này bị triệt tiêu khi gộp trung bình nên dễ bị bỏ sót. Đây là đặc điểm dữ liệu nguồn, không phải "
                       f"lỗi tính toán; nên xem từng dòng trong ma trận nếu cần phân tích sâu theo từng cohort.</div>", unsafe_allow_html=True)

    # ── Giữ chân theo kênh: kênh nào mang về khách chất lượng
    b=card("Tỷ lệ giữ chân sau 3 tháng theo kênh tiếp thị","So sánh chất lượng khách hàng do từng kênh mang về",
        tip="Với mỗi kênh, lấy số khách còn quay lại ở tháng thứ 3 chia cho số khách mua lần đầu từ kênh đó. Kênh có tỷ lệ cao mang về khách gắn bó hơn — nên ưu tiên ngân sách.")
    _c=TX[["ma_khach_hang","ngay","ten_kenh_tiep_thi"]].copy()
    _c["thg"]=_c["ngay"].dt.to_period("M")
    _fm=_c.groupby("ma_khach_hang")["thg"].min().rename("cohort")
    _c=_c.join(_fm,on="ma_khach_hang"); _c["ky"]=(_c["thg"]-_c["cohort"]).apply(lambda x:x.n)
    _rows=[]
    for _k,_g in _c.groupby("ten_kenh_tiep_thi",observed=True):
        _sz=_g[_g.ky==0].ma_khach_hang.nunique()
        if _sz>=200:
            _rows.append((_k,_g[_g.ky==3].ma_khach_hang.nunique()/_sz*100,_sz))
    if _rows:
        _df=pd.DataFrame(_rows,columns=["kenh","ret","sz"]).sort_values("ret")
        _cols=[SAGE if v>=_df.ret.median() else "#C9925A" for v in _df.ret]
        fig=go.Figure(go.Bar(x=_df.ret,y=_df.kenh,orientation="h",marker_color=_cols,
            text=[f"{v:.1f}%" for v in _df.ret],textposition="outside",cliponaxis=False,
            textfont=dict(size=11,color=INK),
            customdata=_df.sz,hovertemplate="%{y}<br>Giữ chân M3: %{x:.1f}%<br>Quy mô: %{customdata:,} khách<extra></extra>"))
        lay(fig,330); fig.update_xaxes(title="% khách còn quay lại ở tháng thứ 3",range=[0,_df.ret.max()*1.25])
        fig.update_layout(margin=dict(l=140,r=60,t=14,b=40))
        b.plotly_chart(fig,width="stretch")
        _hi,_lo=_df.iloc[-1],_df.iloc[0]
        b.markdown(f"<div class='read' style='margin-top:6px'><b>{_hi.kenh}</b> mang về khách gắn bó nhất "
                   f"({_hi.ret:.1f}% còn lại sau 3 tháng), trong khi <b>{_lo.kenh}</b> chỉ {_lo.ret:.1f}%. "
                   f"Chênh lệch {_hi.ret/max(_lo.ret,1e-9):.1f} lần — nên dịch ngân sách sang kênh giữ chân tốt "
                   f"thay vì chỉ nhìn doanh thu tức thời.</div>", unsafe_allow_html=True)


# ═══ DASHBOARD 5 — ANOMALY ══════════════════════════════════════════════
elif page==PAGES[4]:
    st.title("Phát hiện Bất thường"); st.caption(PAGE_TAGS[4]); hero(*HERO_IMG[4])
    st.markdown("<div class='read'>Khoanh vùng đơn có giá trị bất thường (ví dụ gom số lượng lớn) theo IQR, để rà soát reseller/gian lận/lỗi dữ liệu.</div>", unsafe_allow_html=True)
    st.markdown("<div class='note'><b>Nguồn:</b> mart_anomaly_flag (1–1 với fact_transaction). Ngưỡng IQR có sẵn.</div>", unsafe_allow_html=True)
    A=ANOM[(ANOM["ngay_giao_dich"].dt.date>=d0)&(ANOM["ngay_giao_dich"].dt.date<=d1)]
    if ANY_FILTER: A=A[A["ma_giao_dich"].isin(FT["ma_giao_dich"])]
    if A.empty: st.warning("Không có dữ liệu."); st.stop()
    n_an=int(A["co_bat_thuong"].sum()); rate=A["co_bat_thuong"].mean() if len(A) else 0
    val_an=A.loc[A.co_bat_thuong==1,"gia_tri_sau_giam"].sum(); cust_an=A.loc[A.co_bat_thuong==1,"ma_khach_hang"].nunique()
    k=st.columns(4)
    k[0].metric("Giao dịch bất thường",iint(n_an)); k[1].metric("Tỷ lệ bất thường",f"{rate*100:.1f}%")
    k[2].metric("Giá trị bất thường",vnd(val_an)); k[3].metric("Số khách bất thường",iint(cust_an))

    b=card("Phân phối giá trị: Bình thường vs Bất thường","Violin — hình dạng phân phối lồng bên trong box-plot (median, IQR, outlier)",
        tip="Gộp 2 góc nhìn (đường viền = mật độ phân phối như histogram; hộp bên trong = trung vị/tứ phân vị/điểm ngoại lai như box-plot) vào một biểu đồ duy nhất, tránh phải nhìn 2 chart tách rời cho cùng một biến gia_tri_sau_giam.")
    fig=go.Figure()
    fig.add_trace(go.Violin(y=A.loc[A.co_bat_thuong==0,"gia_tri_sau_giam"],name="Bình thường",
        line_color=SAGE,fillcolor="rgba(143,174,150,.35)",box_visible=True,meanline_visible=True))
    fig.add_trace(go.Violin(y=A.loc[A.co_bat_thuong==1,"gia_tri_sau_giam"],name="Bất thường",
        line_color=RED,fillcolor="rgba(181,85,90,.30)",box_visible=True,meanline_visible=True))
    lay(fig,360,legend=True); fig.update_yaxes(tickformat="~s",title="Giá trị sau giảm")
    b.plotly_chart(fig,width="stretch")

    # ── Vì sao bất thường: biến cảnh báo chung thành danh sách hành động
    b=card("Phân loại nguyên nhân bất thường","Mỗi đơn bất thường được gán nguyên nhân trội nhất",
        tip="So giá trị của đơn với ngưỡng IQR trên ba chiều: số lượng mua, mức giảm giá và giá trị đơn. Chiều nào vượt ngưỡng mạnh nhất được chọn làm nguyên nhân. Nhóm 'Số lượng lớn' là dấu hiệu điển hình của reseller/gom hàng.")
    _AF=A.merge(TX[["ma_giao_dich","so_luong","so_tien_giam_gia","don_gia"]],on="ma_giao_dich",how="left")
    _AF["ov"]=_AF["don_gia"]*_AF["so_luong"]-_AF["so_tien_giam_gia"]
    def _fen(cl):
        q1,q3=_AF[cl].quantile(.25),_AF[cl].quantile(.75); return q3+1.5*(q3-q1)
    _th={cl:_fen(cl) for cl in ["so_luong","so_tien_giam_gia","ov"]}
    _aa=_AF[_AF.co_bat_thuong==1].copy()
    for cl in _th:
        _aa[cl+"_r"]=_aa[cl]/(_th[cl] if _th[cl] else 1)
    _nm={"so_luong_r":"Số lượng lớn","so_tien_giam_gia_r":"Giảm giá cao","ov_r":"Giá trị đơn cao"}
    if len(_aa):
        _aa["ly_do"]=_aa[list(_nm)].idxmax(axis=1).map(_nm)
        _aa.loc[_aa[list(_nm)].max(axis=1)<1,"ly_do"]="Hỗn hợp"
        _rc=_aa.ly_do.value_counts()
        cc1,cc2=b.columns([1,1])
        fig=go.Figure(go.Pie(labels=_rc.index,values=_rc.values,hole=.55,
            marker=dict(colors=[RED,GOLD,MAUVE,STONE]),textinfo="label+percent",textfont=dict(size=11)))
        lay(fig,300); cc1.plotly_chart(fig,width="stretch")
        _tb=pd.DataFrame({"Nguyên nhân":_rc.index,"Số giao dịch":[iint(v) for v in _rc.values],
                          "Tỷ trọng":[f"{v/_rc.sum()*100:.1f}%" for v in _rc.values],
                          "Giá trị":[vnd(_aa[_aa.ly_do==k]["gia_tri_sau_giam"].sum()) for k in _rc.index]})
        cc2.dataframe(_tb,width="stretch",hide_index=True)
        _top=_rc.index[0]
        cc2.markdown(f"<div class='warn' style='margin-top:6px'>Nguyên nhân phổ biến nhất là <b>{_top}</b> "
                     f"({_rc.iloc[0]/_rc.sum()*100:.1f}%). Nhóm mua số lượng lớn cần rà soát thủ công vì có thể là "
                     f"reseller hoặc gian lận.</div>", unsafe_allow_html=True)

    b=card("Bất thường theo tháng: số lượng và giá trị trung bình","Cột = số giao dịch bất thường mỗi tháng (trục trái) · Đường = giá trị trung bình mỗi giao dịch bất thường (trục phải)",
        tip="Gộp 2 chart trước đây (scatter theo ngày + line đếm theo tháng) thành 1 biểu đồ 2 trục: vừa thấy xu hướng SỐ LƯỢNG bất thường tăng/giảm theo tháng, vừa thấy GIÁ TRỊ trung bình mỗi vụ có tăng theo hay không — hai chiều bổ sung cho nhau mà không cần 2 biểu đồ tách rời.")
    A2=A.copy(); A2["ym"]=A2["ngay_giao_dich"].dt.to_period("M").astype(str)
    _cnt_m=A2.groupby("ym")["co_bat_thuong"].sum().sort_index()
    _val_m=A2[A2.co_bat_thuong==1].groupby("ym")["gia_tri_sau_giam"].mean().reindex(_cnt_m.index)
    fig=go.Figure()
    fig.add_trace(go.Bar(x=_cnt_m.index,y=_cnt_m.values,name="Số GD bất thường",marker_color=RED,opacity=.75,
        yaxis="y",hovertemplate="%{x}<br>%{y} giao dịch<extra></extra>"))
    fig.add_trace(go.Scatter(x=_val_m.index,y=_val_m.values,name="Giá trị TB/GD",mode="lines+markers",
        line=dict(color=GOLD,width=3),yaxis="y2",hovertemplate="%{x}<br>TB %{y:,.0f}<extra></extra>"))
    lay(fig,340,legend=True)
    fig.update_layout(yaxis=dict(title="Số giao dịch bất thường"),
        yaxis2=dict(title="Giá trị TB/GD",overlaying="y",side="right",showgrid=False,tickformat="~s"))
    b.plotly_chart(fig,width="stretch")

    b=card("Top 20 giao dịch bất thường","Có thể là reseller / gom hàng / fraud")
    tb=(A[A.co_bat_thuong==1].sort_values("gia_tri_sau_giam",ascending=False).head(20)
        [["ma_giao_dich","ma_khach_hang","ma_san_pham","ngay_giao_dich","gia_tri_sau_giam"]].copy())
    tb["ngay_giao_dich"]=tb["ngay_giao_dich"].dt.strftime("%d/%m/%Y"); tb["gia_tri_sau_giam"]=tb["gia_tri_sau_giam"].map(lambda v:f"{int(v):,}".replace(",","."))
    b.dataframe(tb,width="stretch",hide_index=True,height=dfh(len(tb)))


# ═══ DASHBOARD 6 — PREDICTIVE + PRESCRIPTIVE ════════════════════════════
elif page==PAGES[5]:
    st.title("Dự báo & Khuyến nghị"); st.caption(PAGE_TAGS[5]); hero(*HERO_IMG[5])
    st.markdown("<div class='read'>Dự đoán tương lai (doanh thu · churn · CLV) rồi đề xuất hành động theo phong cách skincare: "
                "VIP Membership · Routine cá nhân hoá · Subscription Box · Win-back.</div>", unsafe_allow_html=True)
    st.markdown("<div class='note'>Tính bằng Python: Forecast (Prophet), Churn (RandomForest), CLV (lifetimes). Thiếu thư viện thì tự fallback.</div>", unsafe_allow_html=True)
    if "sub6" not in st.session_state: st.session_state.sub6=0
    SUB6=["Dự báo doanh thu","Rời bỏ & Giá trị KH","Phân cụm K-Means","Khuyến nghị hành động"]
    scols=st.columns(4)
    for i,lbl in enumerate(SUB6):
        if scols[i].button(lbl,key=f"sub6_{i}",use_container_width=True,
                           type=("primary" if st.session_state.sub6==i else "secondary")):
            st.session_state.sub6=i; st.rerun()
    sub6=st.session_state.sub6
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if sub6==0:
        # ═══ GOP 2 buoc lam 1: (1) so sanh 5-6 thuat toan bang backtest, (2) dung CHINH thuat toan
        # THANG CUOC do de tao du bao 6 thang toi that su. Truoc day 2 buoc nay TACH ROI: chart ket qua
        # o tren dung Prophet/OLS fallback co dinh, con phan "so sanh" o duoi lai chon ra mot thuat toan
        # KHAC (thuong la Holt-Winters) la tot nhat — 2 phan khong khop nhau, gay kho hieu vi sao dung
        # thuat toan A o tren trong khi so sanh lai noi thuat toan B tot hon. Gio dong nhat: so sanh truoc,
        # thang cuoc dung de du bao, hien thi ket qua truoc — giai thich ly do chon o duoi.
        @st.cache_data(show_spinner="Đang so sánh các thuật toán và tạo dự báo...")
        def so_sanh_va_du_bao(txser):
            mon_full=txser.set_index("ngay")["doanh_thu"].resample("MS").sum()
            tr,te=mon_full[:-6],mon_full[-6:]
            mape=lambda a,f: float(np.mean(np.abs((np.asarray(a,float)-np.asarray(f,float))/np.asarray(a,float)))*100)
            cands={}  # ten -> (gia_tri_backtest_6_thang, nguyen_ly)

            cands["Naive mùa vụ (mốc so sánh)"]=(tr[-12:-6].values,"Lấy đúng doanh thu cùng kỳ năm trước làm dự báo")

            _c=np.polyfit(np.arange(len(tr)),tr.values.astype(float),1)
            cands["Hồi quy tuyến tính (chỉ xu hướng)"]=(np.polyval(_c,np.arange(len(tr),len(tr)+6)),"Chỉ nắm xu hướng tăng, bỏ qua mùa vụ")

            cands["Trung bình trượt 3 tháng"]=(np.array([tr[-3:].mean()]*6),"Lấy trung bình 3 tháng gần nhất")

            _,_bb,_nn=ols_fc(tr.values,tr.index.month)
            _Mf=pd.get_dummies(pd.Series(te.index.month),prefix="m").reindex(columns=[f"m_{i}" for i in range(1,13)],fill_value=0).values.astype(float)
            cands["OLS (xu hướng + mùa vụ)"]=(np.column_stack([np.ones(6),np.arange(_nn,_nn+6),_Mf])@_bb,"Kết hợp xu hướng dài hạn và quy luật mùa vụ 12 tháng")

            _,_hwf=holt_winters(tr.values,12,6)
            if _hwf is not None:
                cands["Holt-Winters (làm mượt mũ)"]=(_hwf,"Cập nhật liên tục mức nền, xu hướng và mùa vụ theo thời gian")

            _prophet_ok=False
            try:
                from prophet import Prophet
                import logging; logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
                _dtr=tr.reset_index(); _dtr.columns=["ds","y"]
                _mo=Prophet(yearly_seasonality=True); _=_mo.fit(_dtr)
                _pred=_mo.predict(_mo.make_future_dataframe(periods=6,freq="MS"))
                cands["Prophet"]=(_pred["yhat"].values[-6:],"Mô hình Bayes chuyên chuỗi thời gian, tự dò điểm đổi xu hướng (changepoint)")
                _prophet_ok=True
            except Exception:
                pass

            rows=[(nm,mape(te.values,pred),princ) for nm,(pred,princ) in cands.items()]
            cmp_df=pd.DataFrame(rows,columns=["Mô hình","MAPE (%)","Nguyên lý"]).sort_values("MAPE (%)").reset_index(drop=True)
            cmp_df.insert(0,"Hạng",range(1,len(cmp_df)+1))
            best_name=cmp_df.iloc[0]["Mô hình"]
            resid_std=float(np.std(te.values-cands[best_name][0]))

            # Dung CHINH thuat toan thang cuoc, huan luyen lai tren TOAN BO du lieu, de du bao 6 thang THUC SU tiep theo
            y_full=mon_full.values.astype(float); n_full=len(y_full)
            if best_name=="Naive mùa vụ (mốc so sánh)":
                fc_vals=y_full[-12:-6] if n_full>=12 else np.array([y_full[-1]]*6)
            elif best_name=="Hồi quy tuyến tính (chỉ xu hướng)":
                _ccf=np.polyfit(np.arange(n_full),y_full,1); fc_vals=np.polyval(_ccf,np.arange(n_full,n_full+6))
            elif best_name=="Trung bình trượt 3 tháng":
                fc_vals=np.array([y_full[-3:].mean()]*6)
            elif best_name=="OLS (xu hướng + mùa vụ)":
                _,_bbf,_nnf=ols_fc(y_full,mon_full.index.month)
                _futm=pd.period_range(mon_full.index.to_period("M").max()+1,periods=6,freq="M")
                _Mff=pd.get_dummies(pd.Series([p.month for p in _futm]),prefix="m").reindex(columns=[f"m_{i}" for i in range(1,13)],fill_value=0).values.astype(float)
                fc_vals=np.column_stack([np.ones(6),np.arange(_nnf,_nnf+6),_Mff])@_bbf
            elif best_name=="Holt-Winters (làm mượt mũ)":
                _,fc_vals=holt_winters(y_full,12,6)
            elif best_name=="Prophet":
                _dfull=mon_full.reset_index(); _dfull.columns=["ds","y"]
                _mo2=Prophet(yearly_seasonality=True); _=_mo2.fit(_dfull)
                _pred2=_mo2.predict(_mo2.make_future_dataframe(periods=6,freq="MS"))
                fc_vals=_pred2["yhat"].values[-6:]
            else:
                fc_vals=np.array([y_full[-3:].mean()]*6)

            _fut_idx=pd.date_range(mon_full.index.max()+pd.DateOffset(months=1),periods=6,freq="MS")
            fc_out=pd.DataFrame({"ds":list(mon_full.index)+list(_fut_idx),"yhat":list(y_full)+list(fc_vals)})
            fc_out["yhat_lower"]=fc_out["yhat"]-1.96*resid_std; fc_out["yhat_upper"]=fc_out["yhat"]+1.96*resid_std
            fc_out.loc[fc_out["ds"]<=mon_full.index.max(),["yhat_lower","yhat_upper"]]=np.nan
            monthly_df=mon_full.reset_index(); monthly_df.columns=["ds","y"]
            return monthly_df,fc_out,cmp_df,best_name,_prophet_ok

        monthly,fc,cmp_df,best_name,prophet_ok=so_sanh_va_du_bao(TX[["ngay","doanh_thu"]])

        # ── 1) KẾT QUẢ DỰ BÁO (dùng đúng thuật toán thắng cuộc ở phần so sánh bên dưới) — hiện TRƯỚC
        b=card(f"Dự báo doanh thu — {best_name}",
               "Thực tế vs dự báo + dải tin cậy · 6 tháng tới · thuật toán được chọn dựa trên kết quả so sánh backtest ngay bên dưới")
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=fc["ds"],y=fc["yhat_upper"],mode="lines",line=dict(width=0),showlegend=False,hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=fc["ds"],y=fc["yhat_lower"],mode="lines",fill="tonexty",fillcolor="rgba(201,126,140,.14)",line=dict(width=0),showlegend=False,hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=monthly["ds"],y=monthly["y"],name="Thực tế",mode="lines+markers",line=dict(color=ROSE,width=3)))
        fig.add_trace(go.Scatter(x=fc["ds"].tail(7),y=fc["yhat"].tail(7),name="Dự báo",mode="lines",line=dict(color=GOLD,width=2.5,dash="dash")))
        lay(fig,360,legend=True); fig.update_yaxes(tickformat="~s"); b.plotly_chart(fig,width="stretch")
        st.columns(2)[0].metric("Doanh thu dự báo 6 tháng tới",vnd(fc.tail(6)["yhat"].sum()),
                                 help=f"Tính bằng thuật toán {best_name} — thuật toán có MAPE thấp nhất khi kiểm định lùi (xem bảng so sánh bên dưới).")

        # ── 2) SO SÁNH THUẬT TOÁN — giải thích TẠI SAO chọn thuật toán ở trên — hiện SAU
        b=card(f"So sánh các mô hình dự báo — vì sao chọn {best_name}?",
               "Kiểm định lùi (backtest): huấn luyện trên dữ liệu cũ, dự báo 6 tháng cuối rồi đối chiếu thực tế. Thuật toán thắng cuộc ở bảng này chính là thuật toán đang dùng cho chart kết quả ở trên.",
            tip="MAPE là sai số phần trăm tuyệt đối trung bình — càng nhỏ càng chính xác. Dưới 10% được coi là rất tốt, 10–20% là khá. Mốc 'Naive mùa vụ' là chuẩn để biết mô hình có thực sự hơn cách làm đơn giản nhất hay không.")
        if not prophet_ok:
            b.markdown("<div class='warn' style='margin-top:0 0 8px'>⚠️ Thư viện <code>prophet</code> không có sẵn trong môi trường chạy nên "
                       "không đưa vào so sánh này. Cài <code>pip install prophet</code> để bổ sung Prophet vào bảng so sánh — "
                       "nếu Prophet cho MAPE thấp hơn, thuật toán dùng cho chart kết quả ở trên sẽ tự động đổi sang Prophet.</div>",
                       unsafe_allow_html=True)
        cc1,cc2=b.columns([1.1,1])
        # Mau theo hang: hang 1 (tot nhat, MAPE thap nhat) = SAGE (xanh, tot); 2 hang cuoi (te nhat) = STONE (xam);
        # con lai = GOLD. cmp_df da sap xep MAPE tang dan (hang 1 o dong 0), khop truc tiep voi thu tu diem du lieu
        # trong bar chart (KHONG dao nguoc list mau — truoc day dao nguoc [::-1] lam mau bi gan sai hang, khien
        # thuat toan tot nhat lai to mau xam va thuat toan te nhat lai to mau xanh).
        _cols=[SAGE if i==0 else (GOLD if i<len(cmp_df)-2 else STONE) for i in range(len(cmp_df))]
        fig=go.Figure(go.Bar(x=cmp_df["MAPE (%)"],y=cmp_df["Mô hình"],orientation="h",marker_color=_cols,
            text=[f"{v:.2f}%" for v in cmp_df["MAPE (%)"]],textposition="outside",cliponaxis=False,
            textfont=dict(size=11,color=INK),hovertemplate="%{y}<br>MAPE %{x:.2f}%<extra></extra>"))
        lay(fig,300); fig.update_xaxes(title="MAPE — sai số (%) · càng thấp càng tốt",range=[0,cmp_df["MAPE (%)"].max()*1.25])
        fig.update_yaxes(autorange="reversed"); fig.update_layout(margin=dict(l=175,r=55,t=14,b=40))
        cc1.plotly_chart(fig,width="stretch")
        cc2.dataframe(cmp_df[["Hạng","Mô hình","MAPE (%)"]].round(2),width="stretch",hide_index=True)
        _best=cmp_df.iloc[0]; _naive=cmp_df[cmp_df["Mô hình"].str.startswith("Naive")]["MAPE (%)"].iloc[0]
        cc2.markdown(f"<div class='read' style='margin-top:6px'><b>{_best['Mô hình']}</b> cho sai số thấp nhất "
                     f"({_best['MAPE (%)']:.2f}%), tốt hơn mốc so sánh <b>{(1-_best['MAPE (%)']/_naive)*100:.0f}%</b> — "
                     f"đây chính là lý do chart dự báo ở trên dùng thuật toán này. Việc vượt xa mốc Naive cũng chứng minh "
                     f"dữ liệu có quy luật thật, không phải ngẫu nhiên.</div>", unsafe_allow_html=True)
        b.dataframe(cmp_df[["Mô hình","Nguyên lý"]],width="stretch",hide_index=True)

        # ── Phân rã chuỗi thời gian
        b=card("Phân rã chuỗi thời gian","Tách doanh thu thành ba thành phần: xu hướng, mùa vụ và nhiễu",
            tip="Kỹ thuật tách một chuỗi số theo thời gian thành: (1) xu hướng dài hạn, (2) quy luật lặp theo mùa, (3) phần dư không giải thích được. Phần dư càng nhỏ thì quy luật càng rõ.")
        _mon=TX.set_index("ngay")["doanh_thu"].resample("MS").sum()
        _tr,_se,_rs=decompose(_mon.values,12)
        _x=[str(p) for p in _mon.index.to_period("M")]
        for _nm,_v,_cl,_d in [("Xu hướng dài hạn",_tr,ROSE,"Bỏ qua dao động mùa vụ, doanh thu nền tăng đều"),
                              ("Thành phần mùa vụ",_se,SAGE,"Phần lặp lại hằng năm — cao điểm cuối năm"),
                              ("Phần dư (nhiễu)",_rs,STONE,"Phần không giải thích được bằng xu hướng và mùa vụ")]:
            fig=go.Figure(go.Scatter(x=_x,y=_v,mode="lines",line=dict(color=_cl,width=2.2),
                hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"))
            lay(fig,155); fig.update_yaxes(tickformat="~s")
            fig.update_xaxes(tickmode="array",tickvals=_x[::6],tickfont=dict(size=8))
            fig.update_layout(margin=dict(l=56,r=18,t=22,b=22),
                title=dict(text=f"<b>{_nm}</b> — {_d}",font=dict(size=10.5,color=INK),x=0,xanchor="left"))
            b.plotly_chart(fig,width="stretch")
        _si=pd.Series(_se[:12],index=[d.month for d in _mon.index[:12]])
        b.markdown(f"<div class='read'>Xu hướng nền tăng từ {vnd(np.nanmin(_tr))} lên {vnd(np.nanmax(_tr))} "
                   f"({np.nanmax(_tr)/np.nanmin(_tr):.1f} lần). Mùa vụ mạnh nhất vào <b>tháng {_si.idxmax()}</b> "
                   f"(cộng thêm {vnd(_si.max())}), yếu nhất tháng {_si.idxmin()}. Phần dư chỉ chiếm "
                   f"<b>{np.nanstd(_rs)/_mon.mean()*100:.1f}%</b> doanh thu trung bình — quy luật rất rõ, "
                   f"nên dự báo đáng tin.</div>", unsafe_allow_html=True)

        # ── Mua vu theo tung danh muc (chuyen tu Trang 2 sang vi day la phan tich tinh mua vu, hop voi chu de du bao hon)
        b=card("Mùa vụ theo từng danh mục","So sánh 12 tháng trong năm giữa các danh mục — danh mục nào tăng mạnh vào mùa nào",
            tip="Mỗi đường là một danh mục, trục ngang là tháng trong năm (gộp nhiều năm lại). Giúp thấy rõ danh mục nào có tính mùa vụ mạnh (VD Sunscreen tăng mùa hè) để lập kế hoạch nhập hàng theo từng nhóm sản phẩm, bổ sung cho phần phân rã chuỗi thời gian ở trên (vốn chỉ nhìn tổng doanh thu, chưa tách theo danh mục).")
        piv=TX.groupby(["thang","ten_danh_muc"],observed=True)["doanh_thu"].sum().reset_index()
        fig=go.Figure()
        for i,catn in enumerate(sorted(piv.ten_danh_muc.unique())):
            dd=piv[piv.ten_danh_muc==catn].set_index("thang").reindex(range(1,13)).fillna(0)
            fig.add_trace(go.Scatter(x=[f"T{i}" for i in range(1,13)],y=dd["doanh_thu"],mode="lines+markers",name=catn,
                line=dict(width=2.4,color=PAL[i%len(PAL)]),hovertemplate=catn+" · %{x}<br>%{y:,.0f}<extra></extra>"))
        lay(fig,330,legend=True); fig.update_yaxes(tickformat="~s"); b.plotly_chart(fig,width="stretch")

        # ── Dự báo riêng cho từng danh mục
        b=card("Dự báo 6 tháng tới theo từng danh mục","Áp dụng mô hình OLS riêng cho mỗi nhóm sản phẩm",
            tip="Dự báo tách theo danh mục giúp lập kế hoạch nhập hàng chi tiết thay vì chỉ biết tổng doanh thu.")
        _rows=[]
        for _c in sorted(TX["ten_danh_muc"].dropna().unique()):
            _s=TX[TX.ten_danh_muc==_c].set_index("ngay")["doanh_thu"].resample("MS").sum()
            if len(_s)<24: continue
            _fit,_bb,_nn=ols_fc(_s.values,_s.index.month)
            _fut=pd.period_range(_s.index.to_period("M").max()+1,periods=6,freq="M")
            _Mf=pd.get_dummies(pd.Series([p.month for p in _fut]),prefix="m").reindex(columns=[f"m_{i}" for i in range(1,13)],fill_value=0).values.astype(float)
            _fc6=np.column_stack([np.ones(6),np.arange(_nn,_nn+6),_Mf])@_bb
            _mp=float(np.mean(np.abs((_s.values-_fit)/_s.values))*100)
            _rows.append((_c,_s.values[-6:].sum(),_fc6.sum(),_mp))
        if _rows:
            _dfc=pd.DataFrame(_rows,columns=["cat","truoc","du_bao","mape"]).sort_values("du_bao",ascending=False)
            fig=go.Figure()
            fig.add_trace(go.Bar(x=_dfc.cat,y=_dfc.truoc,name="6 tháng gần nhất",marker_color=STONE,
                hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"))
            fig.add_trace(go.Bar(x=_dfc.cat,y=_dfc.du_bao,name="6 tháng dự báo",marker_color=ROSE,
                text=[vnd(v) for v in _dfc.du_bao],textposition="outside",cliponaxis=False,
                textfont=dict(size=10,color=INK),hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"))
            lay(fig,320,legend=True); fig.update_yaxes(tickformat="~s",range=[0,max(_dfc.du_bao.max(),_dfc.truoc.max())*1.25])
            b.plotly_chart(fig,width="stretch")
            _t=_dfc.copy(); _t["Tăng/giảm"]=((_t.du_bao/_t.truoc-1)*100).map(lambda v:f"{v:+.1f}%")
            _t["6 tháng gần nhất"]=_t.truoc.map(vnd); _t["Dự báo 6 tháng"]=_t.du_bao.map(vnd)
            _t["Sai số MAPE"]=_t.mape.map(lambda v:f"{v:.1f}%")
            b.dataframe(_t[["cat","6 tháng gần nhất","Dự báo 6 tháng","Tăng/giảm","Sai số MAPE"]]
                        .rename(columns={"cat":"Danh mục"}),width="stretch",hide_index=True)

    elif sub6==1:
        # ══════════════════════════════════════════════════════════════════
        # TAI CAU TRUC (theo yeu cau nguoi dung): truoc day trang nay hien ca 2 mo hinh ngang hang —
        # mo hinh V1 (nhan suy tu RFM, AUC~1.0 do RO RI DU LIEU) duoc dung de VE TOAN BO cac chart nghiep vu
        # (CLV, ma tran uu tien, danh sach khach nguy co), roi MOI canh bao la no sai o cuoi. Nguoi dung
        # hop ly chi ra: da biet V2 moi dung thi nen DUNG LUON V2 cho moi thu, khong can trung bay V1 day du.
        # Gio: V2 (dung) chay TRUOC va la nguon churn_probability DUY NHAT dung cho moi chart nghiep vu ben duoi;
        # V1 chi con lai duoi dang 1 ghi chu ngan gon canh bao rui ro ro ri du lieu, khong ve lai chart nao.
        @st.cache_data(show_spinner="Đang huấn luyện và so sánh 3 thuật toán...")
        def churn_v2(rfm):
            from sklearn.model_selection import train_test_split
            from sklearn.linear_model import LogisticRegression
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.preprocessing import StandardScaler
            from sklearn.utils.class_weight import compute_sample_weight
            from sklearn.metrics import (roc_auc_score, accuracy_score, precision_score,
                                         recall_score, f1_score, roc_curve, precision_recall_curve, confusion_matrix)
            r=rfm.copy()
            r["churn"]=(r["so_ngay_tu_lan_mua_cuoi"]>90).astype(int)
            F=["tan_suat_mua","tong_chi_tieu","gia_tri_don_hang_tb","tuoi_tho_khach_hang",
               "so_danh_muc_da_mua","tong_so_luong_mua","diem_F","diem_M"]
            X=r[F].fillna(0); y=r["churn"]
            Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
            sc=StandardScaler().fit(Xtr)
            # class_weight='balanced' (LR, RF) / sample_weight balanced (GB) — du lieu churn thuc te mat can bang
            # (da so khach van con hoat dong), neu khong xu ly mo hinh se thien ve du doan "khong roi bo" va bo sot Recall.
            sw=compute_sample_weight("balanced",ytr)
            def _make_mods():
                return {"Hồi quy Logistic":(LogisticRegression(max_iter=2000,random_state=42,class_weight="balanced"),True,None),
                      "Rừng ngẫu nhiên":(RandomForestClassifier(n_estimators=300,max_depth=12,min_samples_leaf=20,
                                          random_state=42,n_jobs=-1,class_weight="balanced"),False,None),
                      "Gradient Boosting":(GradientBoostingClassifier(n_estimators=150,max_depth=4,
                                           learning_rate=.08,random_state=42),False,sw)}
            mods=_make_mods()
            rows=[]; curves={}; cms={}; opt_th={}; best=(None,-1,None,None)
            for nm,(mo,need,sw_) in mods.items():
                a_,b_=(sc.transform(Xtr),sc.transform(Xte)) if need else (Xtr,Xte)
                _=mo.fit(a_,ytr,sample_weight=sw_) if sw_ is not None else mo.fit(a_,ytr)
                p=mo.predict_proba(b_)[:,1]
                # Nguong toi uu theo F1 (thay vi mac dinh 0.5) — phu hop hon voi bai toan mat can bang lop
                pr_,rc_,th_=precision_recall_curve(yte,p)
                f1_=np.where((pr_+rc_)>0,2*pr_*rc_/(pr_+rc_+1e-12),0)
                _bi=int(np.argmax(f1_[:-1])) if len(th_) else 0
                th_opt=float(th_[_bi]) if len(th_) else .5
                pr=(p>=.5).astype(int)
                auc=roc_auc_score(yte,p)
                rows.append([nm,auc,accuracy_score(yte,pr),precision_score(yte,pr,zero_division=0),
                             recall_score(yte,pr,zero_division=0),f1_score(yte,pr,zero_division=0),th_opt])
                fpr,tpr,_=roc_curve(yte,p); curves[nm]=(fpr,tpr,auc)
                cms[nm]=confusion_matrix(yte,pr)
                opt_th[nm]=(th_opt, confusion_matrix(yte,(p>=th_opt).astype(int)),
                            f1_score(yte,(p>=th_opt).astype(int)), recall_score(yte,(p>=th_opt).astype(int)))
                if auc>best[1]: best=(nm,auc,mo,need)
            df=pd.DataFrame(rows,columns=["Thuật toán","ROC-AUC","Accuracy","Precision","Recall","F1","Ngưỡng tối ưu"]).sort_values("ROC-AUC",ascending=False)
            imp=None
            if hasattr(best[2],"feature_importances_"):
                imp=pd.Series(best[2].feature_importances_,index=F).sort_values()

            # Huan luyen LAI thuat toan thang cuoc tren TOAN BO du lieu (khong chi tap train) de co
            # churn_probability cho MOI khach hang — day se la nguon xac suat DUY NHAT dung cho toan bo
            # cac chart nghiep vu ben duoi (CLV, ma tran uu tien, danh sach khach nguy co), thay cho model V1 cu.
            best_nm2=best[0]; need_scale=best[3]
            mo_full=_make_mods()[best_nm2][0]
            Xall_in=sc.fit_transform(X) if need_scale else X.values
            sw_full=compute_sample_weight("balanced",y) if best_nm2=="Gradient Boosting" else None
            _=mo_full.fit(Xall_in,y,sample_weight=sw_full) if sw_full is not None else mo_full.fit(Xall_in,y)
            full_proba=mo_full.predict_proba(Xall_in)[:,1]
            churn_full=pd.DataFrame({"ma_khach_hang":r["ma_khach_hang"].values,"churn_probability":full_proba})

            return df,curves,cms,best[0],float(y.mean()),imp,F,opt_th,churn_full

        cdf,curves,cms,bestnm,crate,imp2,FEATS,opt_th,churn_full=churn_v2(RFM)
        _imb=(1-crate)/crate if crate>0 else float("nan")

        k=st.columns(4)
        k[0].metric("Thuật toán tốt nhất",bestnm)
        k[1].metric("ROC-AUC",f"{cdf['ROC-AUC'].max():.3f}",help="0,5 là đoán ngẫu nhiên; trên 0,8 là phân biệt tốt.")
        k[2].metric("Tỷ lệ churn thực tế",f"{crate*100:.1f}%",help="Tỷ lệ khách không mua quá 90 ngày tính đến 31/12/2025.")
        k[3].metric("Số đặc trưng",f"{len(FEATS)}",help="Đã loại điểm R và số ngày từ lần mua cuối để tránh rò rỉ.")
        st.markdown(f"<div class='warn'>⚠️ <b>Dữ liệu mất cân bằng lớp</b> — cứ 1 khách rời bỏ thì có khoảng "
                    f"<b>{_imb:.1f} khách</b> vẫn đang hoạt động. Cả 3 thuật toán đã được huấn luyện với "
                    f"<code>class_weight='balanced'</code> (Logistic/RF) hoặc <code>sample_weight</code> cân bằng (Gradient Boosting) "
                    f"để tránh mô hình chỉ thiên về dự đoán 'không rời bỏ'. Bảng chỉ số dưới đây dùng ngưỡng mặc định 0,5; cột "
                    f"<b>'Ngưỡng tối ưu'</b> là ngưỡng cho F1 cao nhất — nên cân nhắc dùng ngưỡng này trong triển khai thực tế "
                    f"thay vì mặc định 0,5, vì bài toán churn thường ưu tiên Recall (bắt được khách sắp rời) hơn Accuracy.</div>",
                    unsafe_allow_html=True)

        cc1,cc2=st.columns([1,1])
        with cc1:
            b=card("Đường cong ROC — so sánh 3 thuật toán","Đường càng cong lên góc trên bên trái thì mô hình càng tốt",
                tip="ROC vẽ tỷ lệ bắt đúng khách rời bỏ so với tỷ lệ báo động nhầm. Đường chéo nét đứt là mức đoán ngẫu nhiên. Diện tích dưới đường cong (AUC) là chỉ số tổng hợp.")
            fig=go.Figure()
            for i,(nm,(fpr,tpr,auc)) in enumerate(curves.items()):
                fig.add_trace(go.Scatter(x=fpr,y=tpr,mode="lines",name=f"{nm} ({auc:.3f})",
                    line=dict(width=2.6,color=[ROSE,SAGE,GOLD][i%3]),
                    hovertemplate=nm+"<br>FPR %{x:.2f} · TPR %{y:.2f}<extra></extra>"))
            fig.add_trace(go.Scatter(x=[0,1],y=[0,1],mode="lines",name="Đoán ngẫu nhiên",
                line=dict(width=1.4,color=STONE,dash="dash"),hoverinfo="skip"))
            lay(fig,340,legend=True); fig.update_xaxes(title="Tỷ lệ báo động nhầm (FPR)")
            fig.update_yaxes(title="Tỷ lệ bắt đúng (TPR)")
            fig.update_layout(legend=dict(font=dict(size=9),y=.02,x=.98,xanchor="right",yanchor="bottom"))
            b.plotly_chart(fig,width="stretch")
        with cc2:
            b=card("Bảng chỉ số đánh giá","So sánh 6 chỉ số trên cùng tập kiểm tra (ngưỡng phân loại mặc định 0,5)",
                tip="Accuracy: đoán đúng bao nhiêu phần trăm. Precision: trong số báo rời bỏ, bao nhiêu đúng. Recall: bắt được bao nhiêu phần trăm khách thực sự rời. F1: trung hoà Precision và Recall. Ngưỡng tối ưu: ngưỡng xác suất cho F1 cao nhất, có thể khác 0,5.")
            _d=cdf.copy()
            for c_ in ["ROC-AUC","Accuracy","Precision","Recall","F1"]: _d[c_]=_d[c_].map(lambda v:f"{v:.3f}")
            _d["Ngưỡng tối ưu"]=_d["Ngưỡng tối ưu"].map(lambda v:f"{v:.2f}")
            b.dataframe(_d,width="stretch",hide_index=True,height=dfh(len(_d)))
            b.markdown(f"<div class='read' style='margin-top:6px'><b>{bestnm}</b> cho kết quả tốt nhất với "
                       f"ROC-AUC {cdf['ROC-AUC'].max():.3f} — đây là mô hình <b>duy nhất</b> được dùng cho mọi phân tích "
                       f"nghiệp vụ bên dưới (CLV, ma trận ưu tiên, danh sách khách nguy cơ).</div>",
                       unsafe_allow_html=True)

        # Tang ty le cot cho Ma tran nham lan (cc3) rong hon han Yeu to anh huong (cc4) — truoc day ca 2
        # bang nhau [1,1] khien 2 heatmap con trong cc3 bi bop chat, so lieu dinh vao nhau kho doc (VD "1,569 8,383").
        cc3,cc4=st.columns([1.6,1])
        with cc3:
            _th_opt,_cm_opt,_f1_opt,_rc_opt=opt_th[bestnm]
            b=card(f"Ma trận nhầm lẫn — {bestnm}","Ngưỡng mặc định 0,5 (trái) vs ngưỡng tối ưu theo F1 (phải)",
                tip="Hàng là thực tế, cột là dự đoán. Ngưỡng tối ưu thường thấp hơn 0,5 khi lớp churn hiếm — hạ ngưỡng giúp bắt được nhiều khách rời bỏ hơn (tăng Recall), đánh đổi bằng việc báo động nhầm nhiều hơn.")
            _cm=cms[bestnm]
            _sub1,_sub2=b.columns(2)
            fig=go.Figure(go.Heatmap(z=_cm,x=["Dự đoán: Ở lại","Dự đoán: Rời bỏ"],y=["Thực tế: Ở lại","Thực tế: Rời bỏ"],
                colorscale=[[0,"#F7ECEA"],[1,ROSE]],text=_cm,texttemplate="%{text:,}",
                textfont=dict(size=17),showscale=False))
            lay(fig,320); fig.update_layout(title=dict(text="Ngưỡng 0,50",font=dict(size=12,color=INK),x=.5),
                margin=dict(l=70,r=18,t=26,b=60))
            _sub1.plotly_chart(fig,width="stretch")
            fig2=go.Figure(go.Heatmap(z=_cm_opt,x=["Dự đoán: Ở lại","Dự đoán: Rời bỏ"],y=["Thực tế: Ở lại","Thực tế: Rời bỏ"],
                colorscale=[[0,"#F4F7F5"],[1,SAGE]],text=_cm_opt,texttemplate="%{text:,}",
                textfont=dict(size=17),showscale=False))
            lay(fig2,320); fig2.update_layout(title=dict(text=f"Ngưỡng {_th_opt:.2f}",font=dict(size=12,color=INK),x=.5),
                margin=dict(l=70,r=18,t=26,b=60))
            _sub2.plotly_chart(fig2,width="stretch")
            _tp,_fn=_cm[1,1],_cm[1,0]; _tp2,_fn2=_cm_opt[1,1],_cm_opt[1,0]
            b.markdown(f"<div class='read' style='margin-top:6px'>Ở ngưỡng 0,50: bắt đúng <b>{iint(_tp)}</b>/{iint(_tp+_fn)} khách rời bỏ "
                       f"({_tp/(_tp+_fn)*100:.1f}%). Ở ngưỡng tối ưu {_th_opt:.2f}: bắt đúng <b>{iint(_tp2)}</b>/{iint(_tp2+_fn2)} "
                       f"({_tp2/(_tp2+_fn2)*100:.1f}%) — Recall {'tăng' if _tp2/(_tp2+_fn2)>=_tp/(_tp+_fn) else 'giảm'} nhờ hạ/nâng ngưỡng "
                       f"theo F1 thay vì mặc định.</div>", unsafe_allow_html=True)
        with cc4:
            if imp2 is not None:
                b=card("Yếu tố ảnh hưởng mạnh nhất","Mức đóng góp của từng đặc trưng vào dự đoán",
                    tip="Thanh càng dài nghĩa là mô hình dựa vào yếu tố đó càng nhiều khi quyết định một khách có rời bỏ hay không.")
                _lbl={"tan_suat_mua":"Tần suất mua","tong_chi_tieu":"Tổng chi tiêu","gia_tri_don_hang_tb":"Giá trị đơn TB",
                      "tuoi_tho_khach_hang":"Thâm niên","so_danh_muc_da_mua":"Số danh mục","tong_so_luong_mua":"Tổng số lượng",
                      "diem_F":"Điểm F","diem_M":"Điểm M"}
                fig=go.Figure(go.Bar(x=imp2.values,y=[_lbl.get(i,i) for i in imp2.index],orientation="h",
                    marker_color=GOLD,text=[f"{v:.3f}" for v in imp2.values],textposition="outside",
                    cliponaxis=False,textfont=dict(size=9,color=INK)))
                lay(fig,320); fig.update_xaxes(range=[0,imp2.max()*1.35])
                fig.update_layout(margin=dict(l=95,r=40,t=14,b=30)); b.plotly_chart(fig,width="stretch")
                b.markdown(f"<div class='read' style='margin-top:6px'>Yếu tố quan trọng nhất là "
                           f"<b>{_lbl.get(imp2.index[-1],imp2.index[-1])}</b> — nên theo dõi chỉ số này để phát hiện "
                           f"sớm khách sắp rời bỏ.</div>", unsafe_allow_html=True)

        # ══ Tu day tro di: moi chart nghiep vu deu dung churn_probability tu MO HINH DUNG (V2) ở trên ══
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='read'><b>Từ đây trở xuống dùng churn_probability từ {bestnm} (mô hình đúng ở trên)</b> — "
                    f"không còn model nhãn-rò-rỉ nào tham gia vào các phân tích nghiệp vụ dưới đây.</div>", unsafe_allow_html=True)

        @st.cache_data(show_spinner="Đang tính CLV...")
        def clv_predict(rfm):
            r=rfm.copy(); r["frequency"]=r["tan_suat_mua"]-1; r["T"]=r["tuoi_tho_khach_hang"]; r["recency"]=r["T"]-r["so_ngay_tu_lan_mua_cuoi"]; r["monetary_value"]=r["gia_tri_don_hang_tb"]; method="lifetimes (BG/NBD + Gamma-Gamma)"
            try:
                from lifetimes import BetaGeoFitter,GammaGammaFitter
                rr=r[(r["frequency"]>0)&(r["recency"]>=0)&(r["T"]>0)].copy()
                bgf=BetaGeoFitter(penalizer_coef=.01); _=bgf.fit(rr["frequency"],rr["recency"],rr["T"])
                ggf=GammaGammaFitter(penalizer_coef=.01); _=ggf.fit(rr["frequency"],rr["monetary_value"])
                rr["predicted_clv_90d"]=ggf.customer_lifetime_value(bgf,rr["frequency"],rr["recency"],rr["T"],rr["monetary_value"],time=3,freq="D",discount_rate=.01)
                r=r.merge(rr[["ma_khach_hang","predicted_clv_90d"]],on="ma_khach_hang",how="left")
            except Exception:
                method="Heuristic (thay thế lifetimes)"
                # Nhip mua thuc te giua 2 lan mua; khach chi mua 1 lan -> gia dinh than trong 180 ngay
                _gap=np.where(r["tan_suat_mua"]>1, r["T"]/np.maximum(r["tan_suat_mua"]-1,1), 180)
                _gap=np.clip(_gap,7,365)                    # nhip mua hop ly 7-365 ngay
                _don90=np.clip(90/_gap,0,6)                 # toi da 6 don trong 90 ngay
                _alive=np.exp(-r["so_ngay_tu_lan_mua_cuoi"]/120)   # cang lau khong mua, kha nang quay lai cang thap
                r["predicted_clv_90d"]=(_don90*r["monetary_value"]*_alive).clip(lower=0)
            r["predicted_clv_90d"]=r["predicted_clv_90d"].fillna(0); return r[["ma_khach_hang","predicted_clv_90d"]],method
        clv,cmethod=clv_predict(RFM)
        churn=RFM[["ma_khach_hang","phan_khuc_rfm","tong_chi_tieu","gia_tri_don_hang_tb","tan_suat_mua",
                   "tuoi_tho_khach_hang","so_ngay_tu_lan_mua_cuoi"]].merge(churn_full,on="ma_khach_hang",how="left")
        churn=churn.merge(clv,on="ma_khach_hang",how="left")
        if not cmethod.startswith("life"):
            st.markdown("<div class='warn'>⚠️ <b>CLV đang dùng công thức heuristic thay thế</b> (thư viện <code>lifetimes</code> "
                        "không có sẵn trong môi trường chạy) — công thức ước lượng nhịp mua từ lịch sử rồi áp hệ số suy giảm theo "
                        "recency, <b>không phải</b> mô hình xác suất BG/NBD + Gamma-Gamma đã được kiểm định thống kê. Coi các con số "
                        "CLV 90 ngày dưới đây là <b>ước lượng thô để so sánh tương đối giữa các khách/phân khúc</b>, không dùng làm "
                        "số liệu tài chính chính thức. Cài <code>pip install lifetimes</code> để có kết quả chuẩn hơn.</div>",
                        unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            b=card("Phân phối churn_probability",f"{bestnm} predict_proba (huấn luyện lại trên toàn bộ dữ liệu)")
            cnt,edg=np.histogram(churn["churn_probability"].values,bins=25)
            fig=go.Figure(go.Bar(x=[(edg[i]+edg[i+1])/2 for i in range(len(edg)-1)],y=cnt,marker_color=ROSE)); lay(fig)
            fig.update_xaxes(title="Xác suất churn"); b.plotly_chart(fig,width="stretch")
        with c2:
            b=card(f"CLV 90 ngày theo phân khúc — {cmethod}","predicted_clv_90d")
            samp=churn.sample(min(4000,len(churn)),random_state=1); fig=go.Figure()
            for i,seg in enumerate(sorted(samp.phan_khuc_rfm.unique())):
                dd=samp[samp.phan_khuc_rfm==seg]
                fig.add_trace(go.Scatter(x=[seg]*len(dd),y=dd["predicted_clv_90d"],mode="markers",name=seg,marker=dict(size=5,color=PAL[i%len(PAL)],opacity=.5)))
            lay(fig,320); fig.update_yaxes(tickformat="~s",title="CLV 90 ngày"); fig.update_xaxes(tickangle=-25); fig.update_layout(showlegend=False); b.plotly_chart(fig,width="stretch")

        # ── Ma trận CLV × Churn: chia 4 nhóm hành động
        b=card("Ma trận Giá trị × Nguy cơ rời bỏ","Chia khách thành 4 nhóm để ưu tiên nguồn lực",
            tip="Trục ngang: xác suất rời bỏ (mô hình churn đúng ở trên). Trục dọc: tổng chi tiêu đã mang lại (giá trị lịch sử, độc lập với mô hình). Góc trên bên phải là nhóm đã chi nhiều nhưng đang có nguy cơ rời — cần can thiệp trước tiên.")
        _mc=churn.copy()
        _cth=_mc["tong_chi_tieu"].median(); _pth=opt_th[bestnm][0]
        _mc["nhom"]=np.where((_mc.tong_chi_tieu>=_cth)&(_mc.churn_probability>=_pth),"Giá trị cao · Nguy cơ rời",
                     np.where((_mc.tong_chi_tieu>=_cth)&(_mc.churn_probability<_pth),"Giá trị cao · An toàn",
                     np.where((_mc.tong_chi_tieu<_cth)&(_mc.churn_probability>=_pth),"Giá trị thấp · Nguy cơ rời",
                              "Giá trị thấp · An toàn")))
        _CL={"Giá trị cao · Nguy cơ rời":RED,"Giá trị cao · An toàn":SAGE,
             "Giá trị thấp · Nguy cơ rời":GOLD,"Giá trị thấp · An toàn":STONE}
        _sm=_mc.sample(min(4000,len(_mc)),random_state=3)
        fig=go.Figure()
        for _n,_c in _CL.items():
            _d=_sm[_sm.nhom==_n]
            if len(_d): fig.add_trace(go.Scatter(x=_d.churn_probability,y=_d.tong_chi_tieu,mode="markers",name=_n,
                marker=dict(size=5,color=_c,opacity=.55),hovertemplate=_n+"<br>Churn %{x:.0%}<br>Đã chi %{y:,.0f} đ<extra></extra>"))
        fig.add_hline(y=_cth,line=dict(color=MUTED,dash="dot",width=1))
        fig.add_vline(x=_pth,line=dict(color=MUTED,dash="dot",width=1))
        lay(fig,380,legend=True); fig.update_xaxes(title="Xác suất rời bỏ",tickformat=".0%")
        fig.update_yaxes(title="Tổng chi tiêu đã mang lại (đ)",tickformat="~s")
        fig.update_layout(legend=dict(font=dict(size=9),orientation="h",y=-0.22))
        b.plotly_chart(fig,width="stretch")
        b.markdown(f"<div class='note' style='margin-top:6px'>Ngưỡng phân chia rủi ro rời bỏ dùng <b>{_pth:.2f}</b> "
                   f"(ngưỡng tối ưu theo F1 của {bestnm} ở trên), không dùng mặc định 0,5.</div>", unsafe_allow_html=True)
        _cnt=_mc.nhom.value_counts()
        _val=_mc.groupby("nhom")["tong_chi_tieu"].sum(); _tongdt=_mc["tong_chi_tieu"].sum()
        _order=["Giá trị cao · Nguy cơ rời","Giá trị cao · An toàn","Giá trị thấp · Nguy cơ rời","Giá trị thấp · An toàn"]
        _act={"Giá trị cao · Nguy cơ rời":"Ưu tiên số 1 — win-back cá nhân hoá ngay",
              "Giá trị cao · An toàn":"Duy trì — VIP, tri ân, early-access",
              "Giá trị thấp · Nguy cơ rời":"Chiến dịch tự động chi phí thấp",
              "Giá trị thấp · An toàn":"Nuôi dưỡng dần, tăng tần suất"}
        _tb=pd.DataFrame({"Nhóm":_order,
            "Số khách":[iint(_cnt.get(k,0)) for k in _order],
            "Giá trị đã mang lại":[vnd(_val.get(k,0)) for k in _order],
            "% doanh thu":[f"{_val.get(k,0)/_tongdt*100:.1f}%" for k in _order],
            "Hành động":[_act[k] for k in _order]})
        b.dataframe(_tb,width="stretch",hide_index=True)
        _n1=_cnt.get("Giá trị cao · Nguy cơ rời",0)
        b.markdown(f"<div class='risk' style='margin-top:6px'>Có <b>{iint(_n1)} khách giá trị cao đang có nguy cơ rời bỏ</b> "
                   f"({_n1/len(_mc)*100:.1f}% tập khách), nắm {vnd(_val.get('Giá trị cao · Nguy cơ rời',0))} "
                   f"tương đương {_val.get('Giá trị cao · Nguy cơ rời',0)/_tongdt*100:.1f}% doanh thu. Đây là danh sách cần "
                   f"can thiệp trước tiên — hiệu quả hơn nhiều so với chăm sóc dàn trải.</div>", unsafe_allow_html=True)

        b=card("Top khách nguy cơ churn cao (kèm CLV)",f"churn_probability giảm dần — theo {bestnm}")
        tb=churn.sort_values("churn_probability",ascending=False).head(20)[["ma_khach_hang","phan_khuc_rfm","churn_probability","predicted_clv_90d","tong_chi_tieu"]].copy()
        tb["churn_probability"]=(tb["churn_probability"]*100).round(0).astype(int).astype(str)+"%"; tb["predicted_clv_90d"]=tb["predicted_clv_90d"].map(vnd); tb["tong_chi_tieu"]=tb["tong_chi_tieu"].map(vnd)
        tb.columns=["Mã KH","Phân khúc","Xác suất churn","CLV 90 ngày","Tổng chi tiêu"]; b.dataframe(tb,width="stretch",hide_index=True,height=dfh(len(tb)))

    elif sub6==2:
        st.markdown("<div class='read'><b>Phân cụm K-Means</b> là cách chia khách hàng thành các nhóm mà "
                    "<b>không cần đặt luật trước</b>. Thuật toán tự tìm ra các nhóm dựa trên mức độ giống nhau về hành vi. "
                    "Đây là kiểm chứng độc lập cho cách phân khúc RFM theo luật ở Dashboard 3: nếu hai cách cho kết quả "
                    "tương đồng thì kết luận càng đáng tin.</div>", unsafe_allow_html=True)

        @st.cache_data(show_spinner="Đang phân cụm khách hàng...")
        def phan_cum(rfm,k=4):
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
            from sklearn.metrics import silhouette_score
            X=rfm[["so_ngay_tu_lan_mua_cuoi","tan_suat_mua","tong_chi_tieu"]].copy()
            X["tan_suat_mua"]=np.log1p(X["tan_suat_mua"]); X["tong_chi_tieu"]=np.log1p(X["tong_chi_tieu"])
            Xs=StandardScaler().fit_transform(X)
            rng=np.random.default_rng(0); idx=rng.choice(len(Xs),min(8000,len(Xs)),replace=False)
            elbow=[]
            for kk in range(2,8):
                km=KMeans(n_clusters=kk,random_state=42,n_init=10).fit(Xs)
                elbow.append((kk,km.inertia_,float(silhouette_score(Xs[idx],km.labels_[idx]))))
            km=KMeans(n_clusters=k,random_state=42,n_init=10).fit(Xs)
            out=rfm[["ma_khach_hang","so_ngay_tu_lan_mua_cuoi","tan_suat_mua","tong_chi_tieu","phan_khuc_rfm"]].copy()
            out["cum"]=km.labels_
            return out,pd.DataFrame(elbow,columns=["k","inertia","silhouette"])

        cl,eb=phan_cum(RFM,4)
        # Dat ten cum theo dac diem (gia tri cao/thap, moi/cu)
        _st=cl.groupby("cum").agg(n=("ma_khach_hang","count"),R=("so_ngay_tu_lan_mua_cuoi","mean"),
                                  F=("tan_suat_mua","mean"),M=("tong_chi_tieu","mean"))
        _st["diem"]=_st.M.rank()+_st.F.rank()-_st.R.rank()
        _ten={}
        for i,cid in enumerate(_st.sort_values("diem",ascending=False).index):
            _ten[cid]=["Nhóm giá trị cao","Nhóm ổn định","Nhóm nguội dần","Nhóm rời bỏ"][i]
        cl["ten_cum"]=cl.cum.map(_ten)

        k=st.columns(4)
        k[0].metric("Số cụm",f"{cl.cum.nunique()}",help="Chọn k=4 dựa trên chỉ số Silhouette và tính diễn giải được.")
        k[1].metric("Silhouette (k=4)",f"{eb[eb.k==4].silhouette.iloc[0]:.3f}",
                    help="Đo mức tách bạch giữa các cụm, từ −1 đến 1. Trên 0,3 là chấp nhận được với dữ liệu hành vi thực tế.")
        k[2].metric("Số khách phân cụm",iint(len(cl)))
        k[3].metric("Biến dùng để phân cụm","3",help="Recency, Frequency, Monetary — đã lấy log và chuẩn hoá.")

        cc1,cc2=st.columns([1,1])
        with cc1:
            b=card("Chọn số cụm — phương pháp khuỷu tay và Silhouette","Thử k từ 2 đến 7 để tìm số cụm phù hợp",
                tip="Đường Inertia (hồng) đo mức độ chặt của cụm — càng thấp càng chặt nhưng luôn giảm khi tăng k, nên tìm điểm gãy khuỷu tay. Silhouette (xanh) đo mức tách bạch — càng cao càng tốt.")
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=eb.k,y=eb.inertia,mode="lines+markers",name="Inertia",
                line=dict(color=ROSE,width=2.6),marker=dict(size=8),yaxis="y"))
            fig.add_trace(go.Scatter(x=eb.k,y=eb.silhouette,mode="lines+markers",name="Silhouette",
                line=dict(color=SAGE,width=2.6),marker=dict(size=8),yaxis="y2"))
            lay(fig,320,legend=True)
            fig.update_layout(yaxis=dict(title="Inertia",tickformat="~s"),
                yaxis2=dict(title="Silhouette",overlaying="y",side="right",showgrid=False),
                xaxis=dict(title="Số cụm (k)",dtick=1),
                legend=dict(orientation="h",y=-.22,font=dict(size=10)))
            b.plotly_chart(fig,width="stretch")
            b.markdown("<div class='read' style='margin-top:6px'>Chọn <b>k = 4</b>: đường Inertia bắt đầu gãy, "
                       "và 4 cụm cho kết quả diễn giải được rõ ràng theo nghiệp vụ (giá trị cao, ổn định, nguội dần, rời bỏ).</div>",
                       unsafe_allow_html=True)
        with cc2:
            b=card("Bản đồ cụm khách hàng","Trục ngang: số ngày chưa quay lại · Trục dọc: tổng chi tiêu",
                tip="Mỗi chấm là một khách. Chấm càng sang phải là càng lâu chưa mua; càng lên cao là càng chi nhiều. Bốn màu là bốn cụm do thuật toán tự tìm ra.")
            _sm=cl.sample(min(4000,len(cl)),random_state=5)
            _CM={"Nhóm giá trị cao":ROSE,"Nhóm ổn định":SAGE,"Nhóm nguội dần":GOLD,"Nhóm rời bỏ":STONE}
            fig=go.Figure()
            for _n,_c in _CM.items():
                _d=_sm[_sm.ten_cum==_n]
                if len(_d): fig.add_trace(go.Scatter(x=_d.so_ngay_tu_lan_mua_cuoi,y=_d.tong_chi_tieu,
                    mode="markers",name=_n,marker=dict(size=4.5,color=_c,opacity=.55),
                    hovertemplate=_n+"<br>%{x:.0f} ngày · %{y:,.0f} đ<extra></extra>"))
            lay(fig,320,legend=True); fig.update_yaxes(type="log",title="Tổng chi tiêu (thang log)",tickformat="~s")
            fig.update_xaxes(title="Số ngày từ lần mua cuối")
            fig.update_layout(legend=dict(orientation="h",y=-.22,font=dict(size=9)))
            b.plotly_chart(fig,width="stretch")

        b=card("Đặc điểm từng cụm","Giá trị trung bình của mỗi nhóm do thuật toán tìm ra")
        _tb=cl.groupby("ten_cum").agg(n=("ma_khach_hang","count"),R=("so_ngay_tu_lan_mua_cuoi","mean"),
            F=("tan_suat_mua","mean"),M=("tong_chi_tieu","mean")).reset_index()
        _tb["Tổng chi tiêu nhóm"]=cl.groupby("ten_cum").tong_chi_tieu.sum().values
        _tb=_tb.sort_values("Tổng chi tiêu nhóm",ascending=False)
        _tot=_tb["Tổng chi tiêu nhóm"].sum()
        _disp=pd.DataFrame({"Cụm":_tb.ten_cum,"Số khách":_tb.n.map(iint),
            "% khách":(_tb.n/_tb.n.sum()*100).map(lambda v:f"{v:.1f}%"),
            "Ngày chưa quay lại (TB)":_tb.R.map(lambda v:f"{v:.0f}"),
            "Số lần mua (TB)":_tb.F.map(lambda v:f"{v:.1f}"),
            "Chi tiêu/khách (TB)":_tb.M.map(vnd),
            "Tổng chi tiêu":_tb["Tổng chi tiêu nhóm"].map(vnd),
            "% doanh thu":(_tb["Tổng chi tiêu nhóm"]/_tot*100).map(lambda v:f"{v:.1f}%")})
        b.dataframe(_disp,width="stretch",hide_index=True)

        b=card("Đối chiếu K-Means với phân khúc RFM","Kiểm chứng chéo giữa hai phương pháp",
            tip="Bảng đếm số khách theo từng cặp (cụm K-Means, phân khúc RFM). Nếu mỗi cụm tập trung vào một vài phân khúc RFM nhất định thì hai phương pháp nhất quán với nhau.")
        _ct=pd.crosstab(cl.ten_cum,cl.phan_khuc_rfm)
        _ctp=(_ct.T/_ct.sum(axis=1)).T*100
        fig=go.Figure(go.Heatmap(z=_ctp.values,x=list(_ctp.columns),y=list(_ctp.index),
            colorscale=[[0,"#FBF6F1"],[1,ROSE]],text=_ct.values,texttemplate="%{text:,}",
            textfont=dict(size=9),colorbar=dict(title="% trong cụm",thickness=10),
            hovertemplate="Cụm %{y}<br>Phân khúc %{x}<br>%{text:,} khách<extra></extra>"))
        lay(fig,300); fig.update_xaxes(tickangle=-25,tickfont=dict(size=9))
        fig.update_layout(margin=dict(l=110,r=18,t=14,b=70))
        b.plotly_chart(fig,width="stretch")
        _match={r:_ct.loc[r].idxmax() for r in _ct.index}
        _txt=" · ".join(f"<b>{k_}</b> ↔ {v_}" for k_,v_ in _match.items())
        b.markdown(f"<div class='read' style='margin-top:6px'>Mỗi cụm K-Means tương ứng khá rõ với một phân khúc RFM: "
                   f"{_txt}. Hai phương pháp độc lập cho kết quả tương đồng — điều này củng cố độ tin cậy của cách "
                   f"phân khúc đã dùng.</div>", unsafe_allow_html=True)

    elif sub6==3:
        tot_c=RFM.ma_khach_hang.nunique(); tot_m=RFM["tong_chi_tieu"].sum()
        def sstat(nm):
            s=RFM[RFM.phan_khuc_rfm==nm]; return s.ma_khach_hang.nunique()/tot_c*100, s["tong_chi_tieu"].sum()/tot_m*100, s["tong_chi_tieu"].sum()
        ch_kh,ch_dt,ch_rev=sstat("Champions"); na_kh,na_dt,na_rev=sstat("Need Attention"); ar_kh,ar_dt,ar_rev=sstat("At Risk")
        cl_kh,cl_dt,cl_rev=sstat("Cant Lose Them"); lost_kh,lost_dt,lost_rev=sstat("Lost"); hib_kh,hib_dt,hib_rev=sstat("Hibernating")
        low3_kh,low3_dt=ar_kh+lost_kh+hib_kh, ar_dt+lost_dt+hib_dt
        anom_rate=ANOM["co_bat_thuong"].mean()*100
        anom_val=ANOM.loc[ANOM.co_bat_thuong==1,"gia_tri_sau_giam"].sum(); anom_val_pct=anom_val/TX["doanh_thu"].sum()*100
        # Nguyên nhân bất thường chiếm nhiều nhất (dùng lại quy tắc IQR 3 chiều ở Dashboard 5)
        @st.cache_data(show_spinner=False)
        def ly_do_bat_thuong(anom_,tx_):
            AF=anom_.merge(tx_[["ma_giao_dich","so_luong","so_tien_giam_gia","don_gia"]],on="ma_giao_dich",how="left")
            AF["ov"]=AF["don_gia"]*AF["so_luong"]-AF["so_tien_giam_gia"]
            fence=lambda s: s.quantile(.75)+1.5*(s.quantile(.75)-s.quantile(.25))
            TH={c:fence(AF[c]) for c in ["so_luong","so_tien_giam_gia","ov"]}
            AA=AF[AF.co_bat_thuong==1].copy()
            for c in TH: AA[c+"_r"]=AA[c]/(TH[c] if TH[c] else 1)
            NM={"so_luong_r":"Số lượng lớn","so_tien_giam_gia_r":"Giảm giá cao","ov_r":"Giá trị đơn cao"}
            AA["ly_do"]=AA[list(NM)].idxmax(axis=1).map(NM)
            AA.loc[AA[list(NM)].max(axis=1)<1,"ly_do"]="Hỗn hợp"
            return AA["ly_do"].value_counts(normalize=True)*100
        _lydo=ly_do_bat_thuong(ANOM,TX); _lydo_top=_lydo.idxmax(); _lydo_pct=_lydo.max()
        # Kênh AOV thấp nhất (ứng viên đóng combo/bundle) và tỷ trọng COD
        _chan_aov=TX.groupby("ten_kenh_tiep_thi",observed=True)["doanh_thu"].sum()/TX.groupby("ten_kenh_tiep_thi",observed=True)["ma_giao_dich"].nunique()
        _chan_low=_chan_aov.sort_values().head(2)
        _cod_pct=(TX["phuong_thuc_thanh_toan"]=="COD").mean()*100
        # Hiệu quả giảm giá: AOV theo từng mức giảm (đọc lại Dashboard 2)
        @st.cache_data(show_spinner=False)
        def hieu_qua_giam_gia(tx_):
            gg=tx_["don_gia"]*tx_["so_luong"]; tl=np.where(gg>0,tx_["so_tien_giam_gia"]/gg,0)
            bk=pd.cut(tl,bins=[-.001,.0001,.05,.10,.20,1.],labels=["0%","0-5%","5-10%","10-20%",">20%"])
            de=tx_.assign(bk=bk).groupby("bk",observed=True)["doanh_thu"].mean().reindex(["0%","0-5%","5-10%","10-20%",">20%"]).dropna()
            cor=tx_.assign(ty_le_giam=tl)[["ty_le_giam","doanh_thu"]].corr().iloc[0,1]
            return de,cor
        _de,_cor_disc=hieu_qua_giam_gia(TX)
        _disc_drop=(1-_de.iloc[-1]/_de.iloc[0])*100 if len(_de)>=2 else 0
        _disc_cost=TX["so_tien_giam_gia"].sum()
        # Giữ chân sau 3 tháng theo kênh (đọc lại Dashboard 4) — đối chiếu với doanh thu/kênh
        @st.cache_data(show_spinner=False)
        def giu_chan_theo_kenh(tx_):
            c=tx_[["ma_khach_hang","ngay","ten_kenh_tiep_thi"]].copy(); c["thg"]=c["ngay"].dt.to_period("M")
            fm=c.groupby("ma_khach_hang")["thg"].min().rename("cohort"); c=c.join(fm,on="ma_khach_hang")
            c["ky"]=(c["thg"]-c["cohort"]).apply(lambda x:x.n); rows_=[]
            for k_,g_ in c.groupby("ten_kenh_tiep_thi",observed=True):
                sz=g_[g_.ky==0].ma_khach_hang.nunique()
                if sz>=200: rows_.append((k_,g_[g_.ky==3].ma_khach_hang.nunique()/sz*100,sz))
            return pd.DataFrame(rows_,columns=["kenh","ret3","sz"]).sort_values("ret3",ascending=False)
        _retc=giu_chan_theo_kenh(TX)
        _rev_by_chan=TX.groupby("ten_kenh_tiep_thi",observed=True)["doanh_thu"].sum()
        _retc["dt"]=_retc["kenh"].map(_rev_by_chan); _retc["rank_dt"]=_retc["dt"].rank(ascending=False).astype(int)
        _retc["rank_ret"]=_retc["ret3"].rank(ascending=False).astype(int)
        _best_ret=_retc.iloc[0]; _worst_ret=_retc.iloc[-1]
        # Pareto: % khách tạo 80% doanh thu (đọc lại Dashboard 3)
        _cr=RFM.set_index("ma_khach_hang")["tong_chi_tieu"].sort_values(ascending=False)
        _cum=_cr.cumsum()/_cr.sum()*100; _xp=np.arange(1,len(_cr)+1)/len(_cr)*100
        _i80=int(np.searchsorted(_cum.values,80)); _p80=_xp[min(_i80,len(_xp)-1)]
        loyal_n=RFM[RFM.phan_khuc_rfm.isin(["Loyal Customers","Potential Loyalists"])].ma_khach_hang.nunique()
        aov_all=RFM["gia_tri_don_hang_tb"].mean()
        winback=ar_rev*0.20; subs=loyal_n*aov_all; personalize=na_rev*0.15
        st.markdown(f"<div class='risk'>⚠️ <b>Insight kinh doanh trọng yếu:</b> doanh nghiệp phụ thuộc lớn vào nhóm Champions "
                    f"({ch_kh:.1f}% khách → {ch_dt:.1f}% doanh thu; xét rộng hơn theo Pareto thì chỉ <b>{_p80:.1f}% khách đã tạo ra 80% doanh thu</b>). "
                    f"Chiến lược nên đi theo hai hướng song song: <b>bảo vệ</b> nhóm lõi "
                    f"(VIP, cá nhân hoá) và <b>đa dạng hoá</b> nguồn doanh thu (nuôi Loyal/Potential, subscription) để giảm rủi ro tập trung.</div>", unsafe_allow_html=True)
        cards=[("💎 Champions",f"{ch_kh:.1f}% khách → {ch_dt:.1f}% doanh thu"),
               ("🌱 Need Attention",f"{na_kh:.1f}% khách nhưng chỉ {na_dt:.1f}% doanh thu"),
               ("⚠️ At Risk",f"{ar_dt:.1f}% doanh thu đang có nguy cơ rời bỏ"),
               ("🔍 Bất thường",f"~{anom_rate:.1f}% tổng giao dịch")]
        cc=st.columns(4)
        for col,(t,txt) in zip(cc,cards):
            with col:
                bb=st.container(border=True); bb.markdown(f"<div class='card-title' style='font-size:15px'>{t}</div><div style='color:{INK};font-size:13px'>{txt}</div>",unsafe_allow_html=True)
        b=card("Bảng Action Plan — Insight → Hành động → Ước tính lợi ích","Theo hướng skincare; lợi ích là ước tính tiềm năng dựa trên dữ liệu")
        rows=[
            (f"Champions {ch_kh:.1f}% khách tạo {ch_dt:.1f}% DT","VIP Membership + quà tri ân độc quyền, early-access sản phẩm mới",f"Bảo vệ ~{vnd(ch_rev)} giá trị khách trọn đời (giảm rủi ro mất doanh thu lõi)"),
            (f"Need Attention {na_kh:.1f}% khách, chỉ {na_dt:.1f}% DT","Routine cá nhân hoá theo loại da/độ tuổi; email nhắc tái mua",f"Nâng ~15% nhóm này ≈ {vnd(personalize)} doanh thu tăng thêm"),
            (f"At Risk giữ {ar_dt:.1f}% DT, nguy cơ rời","Win-back: voucher cá nhân hoá theo churn_probability trong 7–14 ngày",f"Thu hồi ~20% ≈ {vnd(winback)} doanh thu cứu lại"),
            ("Skincare dùng lặp lại theo chu kỳ sản phẩm","Subscription Box (serum 1–2 tháng, kem 2–3 tháng)",f"+1 đơn/khách Loyal ≈ {vnd(subs)} doanh thu/chu kỳ"),
            (f"Giao dịch bất thường ~{anom_rate:.1f}% ({anom_val_pct:.1f}% doanh thu)","Quy trình rà soát định kỳ đơn co_bat_thuong = 1 (reseller/fraud)","Giảm thất thoát & rủi ro gian lận"),
            ("Dự báo cho thấy xu hướng doanh thu kỳ tới","Điều chỉnh marketing & tồn kho theo dự báo","Tối ưu chi phí tồn kho, tránh hết/ứ hàng"),
            (f"Cant Lose Them {cl_kh:.1f}% khách, AOV cao nhất hệ thống, im lặng lâu ngày",
             "Winback cá nhân hoá riêng biệt: gọi/Zalo OA + voucher độc quyền 20% + mini set dùng thử dòng cao cấp họ từng mua (không dùng mã giảm giá đại trà)",
             f"Chuyển đổi 15% nhóm này ≈ {vnd(cl_rev*0.15)} doanh thu phục hồi"),
            (f"At Risk + Lost + Hibernating {low3_kh:.1f}% khách nhưng chỉ {low3_dt:.1f}% doanh thu",
             "Ngừng chạy ngân sách marketing đại trà cho nhóm này; chỉ dùng email/app-push tự động chi phí thấp; dồn ngân sách sang Potential Loyalists",
             "Tiết kiệm 15-20% ngân sách retention, tái phân bổ sang phân khúc ROI cao hơn"),
            (f"Nguyên nhân bất thường hàng đầu: {_lydo_top} ({_lydo_pct:.1f}% số GD bất thường)",
             "Đặt ngưỡng duyệt thủ công cho đơn vượt IQR fence trước khi xác nhận vận đơn; xác minh khách sỉ hợp lệ (áp giá sỉ riêng) hay lạm dụng mã giảm giá",
             f"Kiểm soát rủi ro trong {vnd(anom_val)} giá trị giao dịch bất thường"),
            (f"COD chiếm {_cod_pct:.1f}% giao dịch (mọi độ tuổi/vùng)",
             "Ưu đãi thêm 3-5% khi thanh toán ShopeePay/chuyển khoản để giảm rủi ro bùng hàng & tăng tốc dòng tiền",
             "Giảm tỷ lệ hoàn/huỷ đơn COD, cải thiện dòng tiền"),
            (f"Kênh AOV thấp nhất: {' và '.join(_chan_low.index)} (~{vnd(_chan_low.min())}-{vnd(_chan_low.max())})",
             "Ưu tiên bán combo/bundle giá trị thấp (sample set, mini size) trên 2 kênh này thay vì sản phẩm đơn lẻ",
             "Kỳ vọng tăng AOV kênh thêm 10-15%"),
            (f"Giảm giá sâu không tăng giỏ hàng: AOV rơi {_disc_drop:.1f}% từ mức 0% xuống >20% giảm giá (tương quan chỉ {_cor_disc:+.2f})",
             f"Đặt trần giảm giá hợp lý (VD ≤10%); chuyển {vnd(_disc_cost)} ngân sách khuyến mãi (đang chiếm {_disc_cost/TX['doanh_thu'].sum()*100:.1f}% doanh thu) sang chương trình tích điểm/VIP có ROI rõ ràng hơn",
             "Bảo toàn biên lợi nhuận mà không giảm sức mua"),
            (f"{_best_ret.kenh} giữ chân M3 tốt nhất ({_best_ret.ret3:.1f}%) dù chỉ hạng {int(_best_ret.rank_dt)} về doanh thu; {_worst_ret.kenh} giữ chân kém nhất ({_worst_ret.ret3:.1f}%)",
             "Tăng ngân sách cho kênh giữ chân tốt (xây LTV dài hạn) song song với kênh doanh thu cao (Shopee Search); giảm ưu tiên kênh vừa yếu doanh thu vừa yếu giữ chân",
             "Cân bằng giữa tăng trưởng doanh thu ngắn hạn và giá trị khách hàng dài hạn"),
        ]
        _rows_df=pd.DataFrame(rows,columns=["Insight (từ dữ liệu)","Hành động đề xuất","Ước tính lợi ích (tiềm năng)"])
        b.dataframe(_rows_df,width="stretch",hide_index=True,height=dfh(len(_rows_df)))
        b.markdown(f"<div style='{_cap_css}'>Lưu ý: các con số lợi ích là ước tính minh hoạ dựa trên giá trị khách trong dữ liệu, "
                   f"dùng để so sánh mức ưu tiên — không phải cam kết tài chính.</div>", unsafe_allow_html=True)

        # ── Đối chiếu Doanh thu vs Giữ chân theo kênh (tổng hợp Dashboard 1 + 4) ──
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        b=card("Doanh thu vs Giữ chân theo kênh — chọn kênh nào để đầu tư dài hạn?",
               "Trục ngang: tỷ lệ giữ chân sau 3 tháng · Kích thước bong bóng: doanh thu kênh",
               tip="Kênh ở góc trên-phải (giữ chân cao) là nơi xây dựng khách trung thành; kênh doanh thu lớn nhưng giữ chân thấp (như Shopee Search) vẫn cần vì mang volume, nhưng không nên là kênh duy nhất cho tăng trưởng dài hạn.")
        fig=go.Figure()
        for _,rr in _retc.iterrows():
            fig.add_trace(go.Scatter(x=[rr["ret3"]],y=[rr["dt"]],mode="markers+text",name=rr["kenh"],
                text=[rr["kenh"]],textposition="top center",textfont=dict(size=10,color=INK),
                marker=dict(size=np.clip(rr["dt"]/3e8,14,46),color=PAL[list(_retc.kenh).index(rr["kenh"])%len(PAL)],opacity=.7),
                hovertemplate=rr["kenh"]+"<br>Giữ chân M3 %{x:.1f}%<br>Doanh thu %{y:,.0f}<extra></extra>"))
        lay(fig,380); fig.update_xaxes(title="% giữ chân sau 3 tháng"); fig.update_yaxes(title="Doanh thu kênh",tickformat="~s")
        fig.update_layout(showlegend=False); b.plotly_chart(fig,width="stretch")
        b.markdown(f"<div class='read' style='margin-top:6px'><b>{_best_ret.kenh}</b> có tỷ lệ giữ chân cao nhất "
                   f"({_best_ret.ret3:.1f}%) — phù hợp đẩy mạnh để xây khách trung thành dài hạn, dù doanh thu hiện tại "
                   f"({vnd(_best_ret['dt'])}) chưa phải lớn nhất. <b>Shopee Search</b> vẫn nên giữ vai trò trụ cột doanh thu "
                   f"vì AOV và tổng doanh thu cao nhất, nhưng nên phối hợp thêm kênh giữ chân tốt để giảm phụ thuộc.</div>",
                   unsafe_allow_html=True)

        # ── Đề xuất sản phẩm theo nhóm tuổi ──────────────────────────────
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        b=card("Đề xuất sản phẩm theo nhóm tuổi","Kết hợp dữ liệu mua thực tế (thương hiệu, tỷ trọng Premium) với nguyên tắc chăm sóc da phổ thông theo độ tuổi",
            tip="Cột Danh mục/Hoạt chất là khuyến nghị chuyên môn phổ thông; cột Thương hiệu và %DT Premium tính trực tiếp từ dữ liệu giao dịch thật (không lọc theo bộ lọc trang, dùng toàn bộ TX). Không thay thế tư vấn da liễu cho vấn đề da cá nhân.")
        _abins=[18,25,30,35,40,45,120]; _alabs=["18-24","25-29","30-34","35-39","40-44","45+"]
        _T=TX.copy(); _T["nhom_tuoi"]=pd.cut(_T["tuoi"],bins=_abins,labels=_alabs,right=False)
        _CURATED={
            "18-24":("Cleanser + Sunscreen + Serum nhẹ","Niacinamide · AHA/BHA nhẹ · SPF","Kiểm soát dầu/mụn, tập thói quen chống nắng"),
            "25-29":("Serum Vitamin C + Toner cấp nước","Vitamin C · Hyaluronic Acid · Niacinamide","Dự phòng lão hoá sớm, chống oxy hoá"),
            "30-34":("Serum AHA/BHA + Moisturizer đậm hơn","AHA/BHA · Hyaluronic Acid · Retinol nồng độ thấp","Tẩy TB chết nhẹ, phục hồi hàng rào da"),
            "35-39":("Serum Retinol + Moisturizer phục hồi/mắt","Retinol · Peptide","Chống lão hoá rõ nét, nếp nhăn"),
            "40-44":("Serum Retinol/Peptide cao cấp + Eye cream + Sunscreen cao cấp","Retinol nồng độ cao · Peptide · SPF 50+ PA++++","Chống lão hoá chuyên sâu, chăm sóc mắt"),
            "45+":("Bộ full-routine cao cấp: Cleanser dịu nhẹ → Serum Peptide/Retinol → Moisturizer đậm → Sunscreen","Peptide · Retinol · Chất chống oxy hoá","Phục hồi/tái tạo, chống lão hoá toàn diện"),
        }
        _tong_kh=_T.ma_khach_hang.nunique(); _rows2=[]
        for g in _alabs:
            sub=_T[_T.nhom_tuoi==g]
            if sub.empty: continue
            n_cus=sub.ma_khach_hang.nunique(); pct_cus=n_cus/_tong_kh*100
            topb=sub.groupby("ten_thuong_hieu",observed=True)["doanh_thu"].sum().sort_values(ascending=False).head(2)
            top_str=" · ".join(topb.index.tolist()) if len(topb) else "—"
            _dt=sub["doanh_thu"].sum()
            prem=sub.loc[sub.phan_cap_thuong_hieu=="premium","doanh_thu"].sum()/_dt*100 if _dt else 0
            cat_,act_,lydo_=_CURATED[g]
            _rows2.append((g,f"{pct_cus:.1f}%",cat_,act_,lydo_,top_str,f"{prem:.1f}%"))
        _dfa=pd.DataFrame(_rows2,columns=["Nhóm tuổi","% khách","Danh mục ưu tiên","Hoạt chất chính","Ưu tiên da liễu","Thương hiệu mua nhiều nhất (thực tế)","%DT Premium"])
        b.dataframe(_dfa,width="stretch",hide_index=True)
        _n45=_T[_T.nhom_tuoi=="45+"].ma_khach_hang.nunique()
        b.markdown(f"<div class='note' style='margin-top:6px'>Nhóm <b>45+</b> chỉ có <b>{iint(_n45)} khách</b> trong dữ liệu hiện tại — dùng để định hướng thử nghiệm (pilot), "
                   f"chưa nên rót ngân sách quảng cáo lớn cho tới khi cỡ mẫu đủ lớn. Nhóm 18-34 nên ưu tiên combo giá mềm để giải quyết retention tháng 1 chỉ 30,9% "
                   f"(xem Dashboard 4); nhóm 35+ có thể mời thẳng vào dòng Retinol/Peptide cao cấp vì %DT Premium đã cao sẵn.</div>", unsafe_allow_html=True)

st.markdown(f"<div style='color:{MUTED};font-size:12px;margin-top:20px;border-top:1px solid {LINE};padding-top:12px'>"
            "SKINCARE ANALYTICS · 6 Dashboard · DW_SCHEMA_VI · Streamlit + Plotly + scikit-learn · Soft Feminine + Luxury</div>", unsafe_allow_html=True)