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

CHAY:  pip install -r requirements.txt  ->  streamlit run app.py
Dat thu muc DW_SCHEMA_VI canh app.py (hoac dat bien DW_DIR).
"""

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── DESIGN TOKENS — Soft Feminine + Luxury ───────────────────────────────
INK="#2B2420"; MUTED="#8A7B6C"; CREAM="#FBF6F1"; PANEL="#FFFFFF"; LINE="#EDE2D8"
ROSE="#C97E8C"; ROSE_SOFT="#F3DEE1"; SAGE="#8FAE96"; SAGE_SOFT="#DCE7DE"
GOLD="#B0873F"; GOLD_SOFT="#EFE1C4"; SKY="#9FBFC9"; MAUVE="#A9829A"; STONE="#B7ACA0"
PAL=[ROSE, SAGE, GOLD, SKY, MAUVE, STONE]
DATA_DIR=os.environ.get("DW_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "DW_SCHEMA_VI"))
# If DW_SCHEMA_VI folder is not present, but the expected CSVs are colocated
# with this script (or in the current working directory), fall back to that
# location so the app runs without requiring the DW_SCHEMA_VI folder.
_script_dir = os.path.dirname(os.path.abspath(__file__))
_expected_files = [
    "fact_transaction.csv","dim_customer.csv","dim_product.csv","dim_date.csv",
    "dim_geography.csv","dim_channel.csv","dim_payment.csv","dim_brand.csv",
    "dim_category.csv","mart_customer_rfm.csv","mart_cohort_retention.csv","mart_anomaly_flag.csv",
]
if not os.path.isdir(DATA_DIR):
    # prefer script dir when all expected files exist there
    if all(os.path.exists(os.path.join(_script_dir, f)) for f in _expected_files):
        DATA_DIR = _script_dir
    else:
        # try current working directory as a last resort
        _cwd = os.getcwd()
        if all(os.path.exists(os.path.join(_cwd, f)) for f in _expected_files):
            DATA_DIR = _cwd

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

  /* Hop "Doc nhanh" tu dong sinh tu du lieu */
  .insight {{ background:linear-gradient(90deg,{GOLD_SOFT}55,#fff); border:1px solid {LINE}; border-left:3px solid {GOLD};
      border-radius:10px; padding:9px 13px; color:{INK}; font-size:12.8px; line-height:1.55; margin:8px 0 2px; }}
  .insight b {{ color:{GOLD}; }}
  .insight .lbl {{ font-size:9.5px; letter-spacing:.12em; text-transform:uppercase; color:{GOLD}; font-weight:800; margin-right:6px; }}
  /* Chu thich nho duoi bieu do */
  .foot {{ color:{MUTED}; font-size:11px; margin:4px 0 0; }}
  .foot code {{ background:{CREAM}; padding:1px 5px; border-radius:5px; color:{MUTED}; font-size:10.5px; }}
  /* Nut tai CSV gon */
  div[data-testid="stDownloadButton"] > button {{ border:1px solid {LINE}; background:transparent; color:{MUTED};
      font-size:11px; font-weight:600; padding:2px 10px; border-radius:8px; min-height:0; }}
  div[data-testid="stDownloadButton"] > button:hover {{ border-color:{SAGE}; color:{SAGE}; }}
  /* Expander giai thich */
  div[data-testid="stExpander"] details {{ border:1px dashed {LINE} !important; border-radius:10px; background:#FFFDFB; }}
  div[data-testid="stExpander"] summary {{ font-size:12px; color:{MUTED}; font-weight:600; }}
  /* Chu giai KPI */
  .kpi-legend {{ background:{PANEL}; border:1px solid {LINE}; border-radius:12px; padding:10px 14px; font-size:12px; color:{INK}; margin:4px 0 12px; }}
  .kpi-legend span.k {{ display:inline-block; margin:2px 14px 2px 0; }}
  .kpi-legend b {{ color:{ROSE}; }}

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
@st.cache_data(show_spinner="Đang tải DW_SCHEMA_VI...")
def load(dir_):
    r=lambda n: pd.read_csv(os.path.join(dir_,n))
    d=dict(ft=r("fact_transaction.csv"),cus=r("dim_customer.csv"),prod=r("dim_product.csv"),
        date=r("dim_date.csv"),geo=r("dim_geography.csv"),chan=r("dim_channel.csv"),
        pay=r("dim_payment.csv"),brand=r("dim_brand.csv"),cat=r("dim_category.csv"),
        rfm=r("mart_customer_rfm.csv"),cohort=r("mart_cohort_retention.csv"),anom=r("mart_anomaly_flag.csv"))
    m=(d["ft"].merge(d["cus"],on="ma_khach_hang",how="left")
       .merge(d["prod"][["ma_san_pham","ten_san_pham","ma_thuong_hieu","ma_danh_muc"]],on="ma_san_pham",how="left")
       .merge(d["brand"],on="ma_thuong_hieu",how="left").merge(d["cat"][["ma_danh_muc","ten_danh_muc"]],on="ma_danh_muc",how="left")
       .merge(d["geo"],on="ma_dia_ly",how="left").merge(d["chan"],on="ma_kenh",how="left").merge(d["pay"],on="ma_thanh_toan",how="left")
       .merge(d["date"][["khoa_ngay","ngay_day_du","nam","quy","thang","ten_thu"]],on="khoa_ngay",how="left"))
    m["ngay"]=pd.to_datetime(m["ngay_day_du"]); m["doanh_thu"]=m["so_luong"]*m["don_gia"]-m["so_tien_giam_gia"]
    m["thang_ky"]=m["ngay"].dt.to_period("M").astype(str); d["tx"]=m
    d["rfm"]["ngay_mua_dau_tien"]=pd.to_datetime(d["rfm"]["ngay_mua_dau_tien"])
    d["anom"]["ngay_giao_dich"]=pd.to_datetime(d["anom"]["ngay_giao_dich"])
    return d

if not os.path.isdir(DATA_DIR):
    st.error(f"Không tìm thấy thư mục dữ liệu: {DATA_DIR}. Đặt DW_SCHEMA_VI cạnh app.py hoặc set DW_DIR."); st.stop()
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

# ── Bo cong cu chu thich / insight / tai du lieu ─────────────────────────
_DL=[0]
def _pct(a,b_): return (a/b_*100) if b_ else 0
def show(b,fig,data=None,fname=None,ins=None,how=None,tech=None,foot=None):
    """Ve bieu do + (1) cau doc nhanh tu du lieu that, (2) huong dan doc & ky thuat, (3) nut tai CSV."""
    b.plotly_chart(fig,width="stretch")
    if ins: b.markdown(f"<div class='insight'><span class='lbl'>Đọc nhanh</span>{ins}</div>",unsafe_allow_html=True)
    if foot: b.markdown(f"<div class='foot'>{foot}</div>",unsafe_allow_html=True)
    if EXPLAIN and (how or tech):
        with b.expander("Cách đọc biểu đồ này & chi tiết kỹ thuật"):
            if how:  st.markdown(f"**Đọc thế nào**  \n{how}")
            if tech: st.markdown(f"**Chi tiết kỹ thuật**  \n{tech}")
    if data is not None and fname is not None and SHOW_DL:
        _DL[0]+=1
        try: csv=data.to_csv(index=False).encode("utf-8-sig")
        except Exception: csv=pd.DataFrame(data).to_csv(index=False).encode("utf-8-sig")
        b.download_button("Tải dữ liệu biểu đồ (.csv)",csv,fname,"text/csv",key=f"dl{_DL[0]}")

def ser_df(s,c1,c2):
    """Series -> DataFrame 2 cot de tai ve."""
    return pd.DataFrame({c1:list(s.index),c2:list(s.values)})

def top_ins(s,unit="doanh thu",money=True):
    """Sinh cau nhan xet cho 1 series hang muc: dan dau bao nhieu %, gap may lan hang 2."""
    if s is None or len(s)==0: return ""
    ss=s.sort_values(ascending=False); tot=ss.sum(); f=vnd if money else (lambda v:iint(v))
    txt=f"<b>{ss.index[0]}</b> dẫn đầu với {f(ss.iloc[0])} ({_pct(ss.iloc[0],tot):.1f}% {unit})"
    if len(ss)>1 and ss.iloc[1]>0:
        r=ss.iloc[0]/ss.iloc[1]
        txt+=(f", chỉ nhỉnh hơn {ss.index[1]} khoảng {(r-1)*100:.0f}%" if r<1.15 else f", gấp {r:.1f} lần {ss.index[1]}")
    if len(ss)>3: txt+=f". Top 3 chiếm {_pct(ss.iloc[:3].sum(),tot):.1f}% tổng."
    else: txt+="."
    return txt

def trend_ins(s,unit="Doanh thu",money=True):
    """Sinh cau nhan xet cho chuoi thoi gian: dinh/day, thay doi ky cuoi."""
    if s is None or len(s)<2: return ""
    f=vnd if money else (lambda v:iint(v))
    hi,lo=s.idxmax(),s.idxmin(); last,prev=s.iloc[-1],s.iloc[-2]
    ch=_pct(last-prev,prev) if prev else 0
    aro="tăng" if ch>=0 else "giảm"
    return (f"{unit} cao nhất tại <b>{hi}</b> ({f(s.max())}), thấp nhất tại <b>{lo}</b> ({f(s.min())}). "
            f"Kỳ gần nhất ({s.index[-1]}) {aro} <b>{abs(ch):.1f}%</b> so với kỳ trước.")
def hero(u,c): st.markdown(f"<div class='hero-wrap'><img src='{u}'/><div class='hero-overlay'></div><div class='hero-caption'>{c}</div></div>",unsafe_allow_html=True)
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
st.sidebar.caption("Data Warehouse · 2022–2025")

st.sidebar.markdown("<div class='slicer-group'>Chế độ xem</div>", unsafe_allow_html=True)
EXPLAIN=st.sidebar.toggle("Giải thích chi tiết",value=True,
    help="BẬT: hiện thêm ô 'Cách đọc biểu đồ này & chi tiết kỹ thuật' dưới mỗi biểu đồ — dành cho người xem lần đầu. "
         "TẮT: giao diện gọn, chỉ còn biểu đồ và câu Đọc nhanh.")
SHOW_DL=st.sidebar.toggle("Nút tải dữ liệu (.csv)",value=True,
    help="Hiện nút tải bảng số liệu đứng sau mỗi biểu đồ, để kiểm chứng hoặc đưa vào báo cáo Excel/Word.")
st.sidebar.caption("💡 Ô vàng “Đọc nhanh” dưới mỗi biểu đồ là nhận xét tự động tính từ đúng dữ liệu đang lọc.")

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
st.sidebar.caption("Áp dụng cho trang 1, 2, 5. Trang 3, 4, 6 là snapshot RFM/cohort nên không lọc theo thời gian.")
dmin,dmax=TX["ngay"].min().date(),TX["ngay"].max().date()
dr=st.sidebar.date_input("Khoảng thời gian",(dmin,dmax),min_value=dmin,max_value=dmax,help="Chọn ngày bắt đầu và kết thúc.")
d0,d1=dr if isinstance(dr,(list,tuple)) and len(dr)==2 else (dmin,dmax)
ALL="— Tất cả —"
def ddown(lb,col,h):
    o=sorted(TX[col].dropna().unique().tolist()); return st.sidebar.selectbox(lb,[ALL]+o,index=0,help=h)
f_chan=ddown("Kênh tiếp thị","ten_kenh_tiep_thi","Kênh tiếp thị/nguồn kéo khách (Shopee Search, TikTok, Facebook Ads, Google Ads, Referral…). Việc bán hàng thực hiện trên sàn Shopee.")
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
st.sidebar.caption("Soft Feminine · Luxury — hồng đất, sage, vàng đồng trên nền kem.")


# ── Report header + Navigation bar (6 nut) ───────────────────────────────
st.markdown(f"""<div class='report-hero'>
  <div class='logo'>🌿</div>
  <div><div class='rtitle'>SKINCARE ANALYTICS</div>
  <div class='rsub'>Báo cáo phân tích hành vi &amp; phân khúc khách hàng · TMĐT Việt Nam 2022–2025</div></div>
  <div class='rbadge'>DP-01<br>DATN 2026</div>
</div>""", unsafe_allow_html=True)

if "pidx" not in st.session_state: st.session_state.pidx=0
ncols=st.columns(6)
for i,lbl in enumerate(NAV):
    if ncols[i].button(lbl,key=f"nav{i}",use_container_width=True,
                       type=("primary" if st.session_state.pidx==i else "secondary")):
        st.session_state.pidx=i; st.rerun()
page=PAGES[st.session_state.pidx]

# Thanh ngu canh: cho biet dang xem du lieu nao (rat quan trong khi trinh bay)
_ctx=[f"🗓 {d0.strftime('%d/%m/%Y')} → {d1.strftime('%d/%m/%Y')}"]
for lb,v in [("Kênh",f_chan),("Thương hiệu",f_brand),("Danh mục",f_cat),("Vùng",f_reg),("Giới tính",f_gender)]:
    if v!=ALL: _ctx.append(f"{lb}: <b>{v}</b>")
if f_age!=(amin,amax): _ctx.append(f"Tuổi: <b>{f_age[0]}–{f_age[1]}</b>")
st.markdown(
    f"<div style='display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:8px 0 2px;font-size:11.5px;color:{MUTED}'>"
    f"<span style='font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:{GOLD};font-weight:800'>Đang xem</span>"
    + "".join(f"<span style='background:#fff;border:1px solid {LINE};border-radius:20px;padding:3px 11px'>{c}</span>" for c in _ctx)
    + (f"<span style='color:{MUTED}'>· {iint(len(FT))} dòng giao dịch</span>" if len(FT) else "")
    + "</div>", unsafe_allow_html=True)
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
    new_cust=RFM[(RFM.ngay_mua_dau_tien.dt.date>=d0)&(RFM.ngay_mua_dau_tien.dt.date<=d1)].ma_khach_hang.nunique()
    # Repeat Rate ĐÚNG: tỷ lệ khách có >= 2 đơn trong tập đã lọc
    opc=FT.groupby("ma_khach_hang")["ma_giao_dich"].nunique()
    repeat_rate=(opc>=2).mean() if len(opc) else 0
    k=st.columns(6)
    k[0].metric("Doanh thu thuần",vnd(rev),help="Tổng (số lượng × đơn giá) − giảm giá.")
    k[1].metric("Tổng đơn hàng",iint(orders),help="Số mã giao dịch duy nhất.")
    k[2].metric("Tổng khách hàng",iint(custs),help="Số khách duy nhất đã mua.")
    k[3].metric("AOV",vnd(aov),help="Doanh thu ÷ số đơn.")
    k[4].metric("Khách mới",iint(new_cust),help="Khách có ngày mua đầu tiên nằm trong khoảng đã chọn.")
    k[5].metric("Repeat Rate",f"{repeat_rate*100:.1f}%",help="Tỷ lệ khách có từ 2 đơn trở lên trong tập dữ liệu đã lọc (định nghĩa chuẩn).")

    st.markdown(f"""<div class='kpi-legend'>
      <b>Giải nghĩa 6 chỉ số trên</b> ·
      <span class='k'>💰 <b>Doanh thu thuần</b> = số lượng × đơn giá − giảm giá (chưa gồm phí vận chuyển)</span>
      <span class='k'>🧾 <b>Đơn hàng</b> = số mã giao dịch khác nhau</span>
      <span class='k'>👤 <b>Khách hàng</b> = số người đã mua (không đếm trùng)</span>
      <span class='k'>🛍 <b>AOV</b> = giá trị trung bình mỗi đơn (Doanh thu ÷ Đơn)</span>
      <span class='k'>✨ <b>Khách mới</b> = lần mua đầu tiên rơi vào khoảng thời gian đang lọc</span>
      <span class='k'>🔁 <b>Repeat Rate</b> = % khách quay lại mua từ 2 đơn trở lên — càng cao càng ít phụ thuộc quảng cáo</span>
    </div>""", unsafe_allow_html=True)

    b=card("Doanh thu thuần theo tháng","Đường xu hướng — nhìn nhịp tăng/giảm và mùa cao điểm",
        tip="Mỗi điểm là tổng doanh thu thuần của 1 tháng. Vùng hồng nhạt bên dưới chỉ để nhấn khối lượng, không mang giá trị riêng.")
    mon=FT.groupby("thang_ky")["doanh_thu"].sum().sort_index()
    fig=go.Figure(go.Scatter(x=mon.index,y=mon.values,mode="lines+markers",line=dict(color=ROSE,width=3),
        fill="tozeroy",fillcolor="rgba(201,126,140,.10)",hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"))
    lay(fig,320); fig.update_yaxes(tickformat="~s",title="Doanh thu thuần (VNĐ)"); fig.update_xaxes(title="Tháng")
    show(b,fig,ser_df(mon,"Tháng","Doanh thu thuần"),"01_doanh_thu_theo_thang.csv",
        ins=trend_ins(mon,"Doanh thu"),
        how="Trục ngang là tháng, trục dọc là tiền. Đường đi lên = tháng đó bán tốt hơn. Chú ý các đỉnh trùng mùa sale (T7, T11) và các đáy sau Tết.",
        tech="`FT.groupby('thang_ky')['doanh_thu'].sum()` · doanh_thu = so_luong × don_gia − so_tien_giam_gia · trục Y rút gọn dạng ~s (K/M/B).")

    c1,c2=st.columns(2)
    with c1:
        b=card("Tổng đơn hàng theo tháng","Số lượng đơn — đi kèm biểu đồ doanh thu để biết tăng do giá hay do lượng",
            tip="So sánh với biểu đồ doanh thu ở trên: nếu doanh thu tăng mà số đơn không tăng, nghĩa là mỗi đơn có giá trị cao hơn.")
        s=FT.groupby("thang_ky")["ma_giao_dich"].nunique().sort_index()
        fig=go.Figure(go.Bar(x=s.index,y=s.values,marker_color=SAGE,hovertemplate="%{x}<br>%{y} đơn<extra></extra>")); lay(fig)
        fig.update_yaxes(title="Số đơn"); fig.update_xaxes(title="Tháng")
        show(b,fig,ser_df(s,"Tháng","Số đơn"),"01_don_hang_theo_thang.csv",
            ins=trend_ins(s,"Số đơn",money=False),
            how="Cột càng cao = tháng đó có càng nhiều đơn. Đặt cạnh biểu đồ doanh thu: hai đường cùng lên là tăng trưởng lành mạnh.",
            tech="`nunique()` trên ma_giao_dich để không đếm trùng các dòng cùng một đơn.")
    with c2:
        b=card("Tăng trưởng doanh thu %MoM","So với tháng liền trước — xanh là tăng, đỏ là giảm",
            tip="MoM = Month over Month. Công thức: (tháng này − tháng trước) ÷ tháng trước × 100%.")
        g=mon.pct_change()*100; col=[SAGE if v>=0 else "#B5555A" for v in g.fillna(0)]
        fig=go.Figure(go.Bar(x=g.index,y=g.values,marker_color=col,text=[f"{v:.0f}%" if pd.notna(v) else "" for v in g],
            textposition="outside",cliponaxis=False,hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>")); lay(fig)
        fig.update_yaxes(title="% thay đổi"); fig.update_xaxes(title="Tháng")
        gv=g.dropna()
        ins_g=(f"Có <b>{int((gv>=0).sum())}/{len(gv)}</b> tháng tăng trưởng dương. "
               f"Tháng bứt phá nhất: <b>{gv.idxmax()}</b> ({gv.max():+.1f}%); giảm sâu nhất: <b>{gv.idxmin()}</b> ({gv.min():+.1f}%).") if len(gv) else ""
        show(b,fig,ser_df(g.round(2),"Tháng","%MoM"),"01_tang_truong_mom.csv",ins=ins_g,
            how="Cột xanh vượt lên trên vạch 0 = tháng đó tăng so với tháng trước; cột đỏ chúc xuống = giảm. Nhìn xu hướng chung quan trọng hơn một tháng đơn lẻ.",
            tech="`mon.pct_change()*100`. Tháng đầu tiên không có giá trị vì không có tháng trước để so.")

    c3,c4=st.columns(2)
    with c3:
        b=card("Doanh thu theo thương hiệu (Top 10)","Nguồn: dim_brand — hãng nào đang gánh doanh thu",
            tip="Chỉ hiện 10 thương hiệu doanh thu cao nhất. Tải CSV bên dưới để xem đầy đủ danh sách.")
        s_all=FT.groupby("ten_thuong_hieu")["doanh_thu"].sum().sort_values(ascending=False)
        s=s_all.head(10).iloc[::-1]
        f=barh(s.index,s.values,MAUVE); f.update_layout(margin=dict(l=140,r=50,t=14,b=40)); f.update_xaxes(title="Doanh thu (VNĐ)")
        show(b,f,ser_df(s_all,"Thương hiệu","Doanh thu"),"01_doanh_thu_thuong_hieu.csv",
            ins=top_ins(s_all,"doanh thu"),
            how="Thanh dài nhất nằm trên cùng. Nếu 2–3 thương hiệu chiếm phần lớn thanh, danh mục hàng đang phụ thuộc vào ít nhà cung cấp.",
            tech=f"Tổng cộng {len(s_all)} thương hiệu trong dữ liệu đã lọc; biểu đồ hiển thị Top 10.")
    with c4:
        b=card("Doanh thu theo danh mục","Nguồn: dim_category — Cleanser, Serum, Moisturizer, Sunscreen…",
            tip="Danh mục là loại sản phẩm skincare. Con số trên đầu cột là doanh thu đã rút gọn (tr = triệu, tỷ = tỷ đồng).")
        s=FT.groupby("ten_danh_muc")["doanh_thu"].sum().sort_values(ascending=False)
        fig=barv(s.index,s.values,ROSE); fig.update_yaxes(title="Doanh thu (VNĐ)")
        show(b,fig,ser_df(s,"Danh mục","Doanh thu"),"01_doanh_thu_danh_muc.csv",
            ins=top_ins(s,"doanh thu"),
            how="Mỗi cột là một loại sản phẩm. Cột thấp bất thường là cơ hội mở rộng, hoặc dấu hiệu thiếu hàng/thiếu quảng bá.",
            tech="`groupby('ten_danh_muc')['doanh_thu'].sum()` — nối từ dim_product → dim_category qua ma_danh_muc.")

    c5,c6=st.columns(2)
    with c5:
        b=card("Top 10 sản phẩm theo doanh thu","Nguồn: dim_product — mã hàng cần luôn còn tồn kho",
            tip="Đây là những SKU sinh tiền nhiều nhất; nên ưu tiên giữ tồn kho và không để hết hàng.")
        s_all=FT.groupby("ten_san_pham")["doanh_thu"].sum().sort_values(ascending=False)
        s=s_all.head(10).iloc[::-1]
        f=barh(s.index,s.values,SAGE); f.update_layout(margin=dict(l=175,r=55,t=14,b=40)); f.update_xaxes(title="Doanh thu (VNĐ)")
        show(b,f,ser_df(s_all.head(200),"Sản phẩm","Doanh thu"),"01_top_san_pham.csv",
            ins=(top_ins(s_all,"doanh thu")+f" Top 10 sản phẩm chiếm <b>{_pct(s_all.head(10).sum(),s_all.sum()):.1f}%</b> tổng doanh thu.") if len(s_all) else "",
            how="Đọc từ trên xuống: sản phẩm bán chạy nhất ở trên cùng. Nếu Top 10 chiếm tỷ trọng quá lớn, rủi ro đứt hàng sẽ ảnh hưởng mạnh tới doanh thu.",
            tech=f"Có {iint(len(s_all))} sản phẩm phát sinh doanh thu; file CSV xuất Top 200.")
    with c6:
        b=card("Doanh thu theo vùng miền","Thay cho bản đồ (schema không lưu toạ độ) — vùng nào mạnh nhất",
            tip="Vùng miền lấy từ dim_geography (Miền Bắc / Trung / Nam / Tây), suy ra từ tỉnh–thành của khách hàng.")
        s=FT.groupby("vung_mien")["doanh_thu"].sum().sort_values(ascending=False)
        fig=barv(s.index,s.values,GOLD); fig.update_yaxes(title="Doanh thu (VNĐ)")
        show(b,fig,ser_df(s,"Vùng miền","Doanh thu"),"01_doanh_thu_vung_mien.csv",
            ins=top_ins(s,"doanh thu"),
            how="Cột cao = vùng đang bán tốt, ưu tiên giữ nhịp giao hàng và quảng cáo. Cột thấp = thị trường còn trống, có thể là cơ hội mở rộng.",
            tech="Nối fact_transaction → dim_customer → dim_geography qua ma_dia_ly.")

    # ── So sanh theo Kenh tiep thi ───────────────────────────────────────
    b=card("So sánh theo Kênh tiếp thị","Doanh thu · Đơn · AOV · %DT theo từng kênh tiếp thị (bán hàng trên Shopee)",
        tip="Đây là các kênh tiếp thị/nguồn kéo khách (Shopee Search, TikTok, Facebook Ads, Google Ads…), không phải sàn bán. Việc bán hàng diễn ra trên Shopee.")
    g=FT.groupby("ten_kenh_tiep_thi").agg(dt=("doanh_thu","sum"),od=("ma_giao_dich","nunique"))
    g["aov"]=g.dt/g.od; g["pct"]=g.dt/g.dt.sum()*100; g=g.sort_values("dt",ascending=False)
    cc1,cc2=b.columns([1.15,1])
    fig=go.Figure(go.Bar(x=g.index,y=g.dt,marker_color=ROSE,text=[vnd(v) for v in g.dt],textposition="outside",
        cliponaxis=False,textfont=dict(size=10,color=INK),hovertemplate="%{x}<br>%{y:,.0f}<extra></extra>"))
    lay(fig,320); fig.update_yaxes(tickformat="~s",range=[0,g.dt.max()*1.2],title="Doanh thu (VNĐ)")
    fig.update_xaxes(tickangle=-20,title="Kênh tiếp thị")
    cc1.plotly_chart(fig,width="stretch")
    tb=g.reset_index().rename(columns={"ten_kenh_tiep_thi":"Kênh"})
    tb["Doanh thu"]=tb.dt.map(vnd); tb["Đơn"]=tb.od.map(iint); tb["AOV"]=tb.aov.map(vnd); tb["% DT"]=tb.pct.map(lambda v:f"{v:.1f}%")
    cc2.markdown("<div class='foot' style='margin-bottom:4px'><b>Bảng số liệu</b> · AOV = doanh thu ÷ số đơn của riêng kênh đó. "
                 "Kênh có AOV cao mà ít đơn thường là nhóm khách chất lượng, đáng tăng ngân sách.</div>", unsafe_allow_html=True)
    cc2.dataframe(tb[["Kênh","Doanh thu","Đơn","AOV","% DT"]],width="stretch",hide_index=True)
    _best_aov=g["aov"].idxmax() if len(g) else ""
    b.markdown(f"<div class='insight'><span class='lbl'>Đọc nhanh</span>{top_ins(g['dt'],'doanh thu')} "
               f"Kênh có giá trị đơn trung bình cao nhất là <b>{_best_aov}</b> ({vnd(g['aov'].max()) if len(g) else ''}/đơn).</div>",
               unsafe_allow_html=True)
    if EXPLAIN:
        with b.expander("Cách đọc biểu đồ này & chi tiết kỹ thuật"):
            st.markdown("**Đọc thế nào**  \nCột cao = kênh mang về nhiều tiền nhất. Nhưng hãy đọc kèm cột AOV trong bảng: "
                        "một kênh nhiều đơn nhưng AOV thấp (ví dụ săn khuyến mãi) có thể kém lời hơn kênh ít đơn mà AOV cao.")
            st.markdown("**Chi tiết kỹ thuật**  \n`groupby('ten_kenh_tiep_thi')` với dt = SUM(doanh_thu), od = COUNT DISTINCT(ma_giao_dich), "
                        "aov = dt/od, pct = dt/tổng dt. Đây là **kênh tiếp thị** (nguồn kéo khách), không phải sàn bán — toàn bộ đơn đều bán trên Shopee.")
    if SHOW_DL:
        _DL[0]+=1
        b.download_button("Tải dữ liệu biểu đồ (.csv)",
            g.reset_index().rename(columns={"ten_kenh_tiep_thi":"Kênh","dt":"Doanh thu","od":"Số đơn","aov":"AOV","pct":"% doanh thu"}
            ).to_csv(index=False).encode("utf-8-sig"),"01_kenh_tiep_thi.csv","text/csv",key=f"dl{_DL[0]}")


# ═══ DASHBOARD 2 — HANH VI KHACH HANG ═══════════════════════════════════
elif page==PAGES[1]:
    st.title("Hành vi Khách hàng"); st.caption(PAGE_TAGS[1]); hero(*HERO_IMG[1])
    st.markdown("<div class='read'>Khách mua như thế nào: bao nhiêu lần, mỗi đơn bao nhiêu sản phẩm, chi bao nhiêu, mua ngày nào, "
                "và xu hướng theo tháng của từng danh mục skincare.</div>", unsafe_allow_html=True)
    st.markdown("<div class='note'><b>Nguồn:</b> fact_transaction + dim_date + mart_customer_rfm. <b>Đo lường:</b> Purchase Frequency, "
                "Avg Basket Size, Average Discount, Avg Revenue/Customer, Days Between Purchases.</div>", unsafe_allow_html=True)
    if FT.empty: st.warning("Không có dữ liệu."); st.stop()
    freq=RFM["tan_suat_mua"].mean(); basket=FT["so_luong"].sum()/FT.ma_giao_dich.nunique()
    disc=FT["so_tien_giam_gia"].mean(); arpc=RFM["tong_chi_tieu"].mean()
    days=RFM["tuoi_tho_khach_hang"].mean()/max(RFM["tan_suat_mua"].mean()-1,1e-9)
    k=st.columns(5)
    k[0].metric("Tần suất mua (TB)",f"{freq:.2f}",help="Số lần mua TB mỗi khách (Purchase Frequency).")
    k[1].metric("SP mỗi đơn (TB)",f"{basket:.2f}",help="Số sản phẩm TB mỗi đơn (Avg Basket Size).")
    k[2].metric("Giảm giá TB",vnd(disc),help="Giảm giá TB mỗi dòng giao dịch (Average Discount).")
    k[3].metric("Doanh thu/Khách",vnd(arpc),help="Chi tiêu TB mỗi khách, cả vòng đời (Avg Revenue/Customer).")
    k[4].metric("Ngày giữa 2 đơn",f"{days:.0f} ngày",help="Số ngày TB giữa 2 lần mua (Days Between Purchases).")
    st.markdown(f"""<div class='kpi-legend'>
      <b>Giải nghĩa 5 chỉ số trên (bằng tiếng Việt)</b> ·
      <span class='k'>🔁 <b>Purchase Frequency</b> = trung bình mỗi khách mua bao nhiêu lần</span>
      <span class='k'>🧺 <b>Avg Basket Size</b> = mỗi đơn có trung bình bao nhiêu sản phẩm</span>
      <span class='k'>🏷 <b>Average Discount</b> = tiền giảm giá trung bình trên mỗi dòng đơn hàng</span>
      <span class='k'>💳 <b>Avg Revenue/Customer</b> = mỗi khách chi trung bình bao nhiêu trong cả vòng đời</span>
      <span class='k'>⏱ <b>Days Between Purchases</b> = trung bình bao lâu khách quay lại mua tiếp — dùng để canh thời điểm nhắc mua lại</span>
    </div>""", unsafe_allow_html=True)

    b=card("Xu hướng danh mục theo tháng (tính mùa vụ)","Gộp cả 4 năm về 12 tháng — danh mục nào tăng theo mùa",
        tip="Trục ngang là tháng trong năm (T1…T12), gộp dữ liệu tất cả các năm lại để nhìn rõ quy luật mùa vụ, không phải chuỗi thời gian liên tục.")
    piv=FT.groupby(["thang","ten_danh_muc"])["doanh_thu"].sum().reset_index()
    fig=go.Figure()
    for i,catn in enumerate(sorted(piv.ten_danh_muc.unique())):
        dd=piv[piv.ten_danh_muc==catn].set_index("thang").reindex(range(1,13)).fillna(0)
        fig.add_trace(go.Scatter(x=[f"T{i}" for i in range(1,13)],y=dd["doanh_thu"],mode="lines+markers",name=catn,
            line=dict(width=2.4,color=PAL[i%len(PAL)]),hovertemplate=catn+" · %{x}<br>%{y:,.0f}<extra></extra>"))
    lay(fig,330,legend=True); fig.update_yaxes(tickformat="~s",title="Doanh thu (VNĐ)"); fig.update_xaxes(title="Tháng trong năm")
    _mtot=FT.groupby("thang")["doanh_thu"].sum()
    _pk=piv.loc[piv["doanh_thu"].idxmax()] if len(piv) else None
    show(b,fig,piv.rename(columns={"thang":"Tháng","ten_danh_muc":"Danh mục","doanh_thu":"Doanh thu"}),"02_mua_vu_danh_muc.csv",
        ins=(f"Tháng bán tốt nhất trong năm là <b>T{int(_mtot.idxmax())}</b> ({vnd(_mtot.max())}), thấp nhất là <b>T{int(_mtot.idxmin())}</b> ({vnd(_mtot.min())}). "
             f"Đỉnh cao nhất thuộc về <b>{_pk['ten_danh_muc']}</b> vào T{int(_pk['thang'])}." if len(piv) else ""),
        how="Mỗi màu là một danh mục. Đường nào nhô cao ở một vài tháng nhất định = danh mục đó có tính mùa vụ, nên chuẩn bị tồn kho và quảng cáo trước 1 tháng.",
        tech="`groupby(['thang','ten_danh_muc'])` rồi reindex đủ 12 tháng, thiếu thì điền 0. Trục X là số tháng (1–12) gộp toàn bộ 2022–2025.")

    c1,c2=st.columns(2)
    with c1:
        b=card("Phân bố giá trị đơn hàng","Histogram — phần lớn đơn nằm ở mức giá nào",
            tip="Trục ngang chia giá trị đơn thành 30 khoảng; cột càng cao nghĩa là càng nhiều đơn rơi vào khoảng giá đó.")
        ov=FT.groupby("ma_giao_dich")["doanh_thu"].sum(); cnt,edg=np.histogram(ov.values,bins=30)
        fig=go.Figure(go.Bar(x=[(edg[i]+edg[i+1])/2 for i in range(len(edg)-1)],y=cnt,marker_color=SKY,
            hovertemplate="Quanh mức %{x:,.0f}<br>%{y} đơn<extra></extra>"))
        lay(fig); fig.update_xaxes(tickformat="~s",title="Giá trị đơn (VNĐ)"); fig.update_yaxes(title="Số đơn")
        _md=ov.median() if len(ov) else 0
        show(b,fig,pd.DataFrame({"Khoảng giá trị":[(edg[i]+edg[i+1])/2 for i in range(len(edg)-1)],"Số đơn":cnt}),"02_phan_bo_gia_tri_don.csv",
            ins=(f"Một nửa số đơn có giá trị dưới <b>{vnd(_md)}</b>; đơn trung bình <b>{vnd(ov.mean())}</b>, đơn lớn nhất <b>{vnd(ov.max())}</b>. "
                 f"Trung bình cao hơn trung vị cho thấy có một nhóm nhỏ đơn giá trị rất lớn kéo con số lên." if ov.mean()>_md else
                 f"Một nửa số đơn có giá trị dưới <b>{vnd(_md)}</b>; đơn trung bình <b>{vnd(ov.mean())}</b>.") if len(ov) else "",
            how="Đỉnh của biểu đồ cho biết 'mức giá quen thuộc' của khách. Cái đuôi dài bên phải là các đơn giá trị lớn — thường là combo hoặc reseller gom hàng.",
            tech="Cộng doanh thu theo từng ma_giao_dich rồi `np.histogram(bins=30)`. Trung vị (median) ít bị méo bởi giá trị ngoại lai hơn trung bình.")
    with c2:
        b=card("Số đơn theo ngày trong tuần","Nguồn: dim_date[ten_thu] — nên đẩy quảng cáo vào ngày nào",
            tip="Đếm số đơn duy nhất theo thứ trong tuần, cộng dồn toàn bộ khoảng thời gian đang lọc.")
        s=FT.groupby("ten_thu")["ma_giao_dich"].nunique().reindex(WD_ORDER).fillna(0)
        fig=go.Figure(go.Bar(x=[WD_VN[w] for w in WD_ORDER],y=s.values,marker_color=MAUVE,text=[iint(v) for v in s.values],
            textposition="outside",cliponaxis=False,hovertemplate="%{x}<br>%{y} đơn<extra></extra>")); lay(fig)
        fig.update_yaxes(title="Số đơn"); fig.update_xaxes(title="Thứ trong tuần")
        sv=pd.Series(s.values,index=[WD_VN[w] for w in WD_ORDER])
        show(b,fig,ser_df(sv,"Thứ","Số đơn"),"02_don_theo_thu.csv",
            ins=(f"<b>{sv.idxmax()}</b> là ngày mua nhiều nhất ({iint(sv.max())} đơn), <b>{sv.idxmin()}</b> ít nhất ({iint(sv.min())} đơn) — "
                 f"chênh lệch {(_pct(sv.max()-sv.min(),sv.min()) if sv.min() else 0):.0f}%." if sv.sum() else ""),
            how="Cột cao = ngày khách mua nhiều. Nên dồn ngân sách quảng cáo và nhân sự chăm sóc vào 2–3 ngày cao nhất.",
            tech="dim_date[ten_thu] là tên thứ tiếng Anh, đã đổi sang tiếng Việt và sắp lại đúng thứ tự Thứ 2 → Chủ nhật.")

    c3,c4=st.columns(2)
    with c3:
        b=card("Doanh thu theo giới tính","Nguồn: dim_customer[gioi_tinh]",
            tip="Giới tính khai báo trong hồ sơ khách hàng. Dùng để chọn giọng điệu và hình ảnh cho chiến dịch quảng cáo.")
        s=FT.groupby("gioi_tinh")["doanh_thu"].sum().sort_values(ascending=False)
        fig=barv(s.index,s.values,ROSE); fig.update_yaxes(title="Doanh thu (VNĐ)")
        show(b,fig,ser_df(s,"Giới tính","Doanh thu"),"02_doanh_thu_gioi_tinh.csv",
            ins=top_ins(s,"doanh thu"),
            how="Nếu một giới chiếm áp đảo, nội dung quảng cáo nên tập trung vào nhóm đó; nhóm còn lại là dư địa chưa khai thác.",
            tech="Doanh thu gán theo khách hàng đứng tên đơn (dim_customer.gioi_tinh).")
    with c4:
        b=card("Tần suất mua TB theo phân khúc RFM","Nguồn: mart_customer_rfm — nhóm nào mua đi mua lại nhiều nhất",
            tip="Số lần mua trung bình của mỗi phân khúc. Champions và Loyal thường cao nhất; Lost/Hibernating thấp nhất.")
        s=RFM.groupby("phan_khuc_rfm")["tan_suat_mua"].mean().sort_values(ascending=False)
        fig=go.Figure(go.Bar(x=s.index,y=s.values,marker_color=SAGE,text=[f"{v:.1f}" for v in s.values],
            textposition="outside",cliponaxis=False,hovertemplate="%{x}<br>%{y:.2f} lần/khách<extra></extra>")); lay(fig)
        fig.update_xaxes(tickangle=-25,title="Phân khúc RFM"); fig.update_yaxes(title="Số lần mua TB")
        show(b,fig,ser_df(s.round(2),"Phân khúc","Tần suất mua TB"),"02_tan_suat_theo_phan_khuc.csv",
            ins=(f"<b>{s.index[0]}</b> mua nhiều nhất ({s.iloc[0]:.2f} lần/khách), gấp <b>{s.iloc[0]/s.iloc[-1]:.1f} lần</b> nhóm {s.index[-1]} ({s.iloc[-1]:.2f} lần)."
                 if len(s)>1 and s.iloc[-1]>0 else ""),
            how="Cột cao = nhóm khách trung thành, đáng đầu tư giữ chân. Cột thấp = nhóm mua một lần rồi thôi, cần chiến dịch kích hoạt lại.",
            tech="Bảng mart_customer_rfm là ảnh chụp (snapshot) ngày 31/12/2025 nên **không** thay đổi theo bộ lọc thời gian bên trái.")

    b=card("Doanh thu theo nhóm tuổi","Nguồn: dim_customer[tuoi], chia nhóm 5 năm — chân dung khách theo độ tuổi",
        tip="Tuổi được chia thành các khoảng 5 năm (15-19, 20-24, …) để dễ đọc và dễ nhắm quảng cáo.")
    bins=list(range(15,65,5)); labs=[f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins)-1)]
    FTa=FT.copy(); FTa["nhom_tuoi"]=pd.cut(FTa["tuoi"],bins=bins,labels=labs,right=False)
    s=FTa.groupby("nhom_tuoi",observed=True)["doanh_thu"].sum()
    fig=barv(s.index.astype(str),s.values,GOLD); fig.update_yaxes(title="Doanh thu (VNĐ)"); fig.update_xaxes(title="Nhóm tuổi")
    _sa=pd.Series(s.values,index=s.index.astype(str))
    show(b,fig,ser_df(_sa,"Nhóm tuổi","Doanh thu"),"02_doanh_thu_nhom_tuoi.csv",
        ins=(top_ins(_sa,"doanh thu")+f" Nhóm 20–34 tuổi đóng góp <b>{_pct(_sa[[i for i in _sa.index if i in ['20-24','25-29','30-34']]].sum(),_sa.sum()):.1f}%</b> tổng doanh thu.") if len(_sa) else "",
        how="Cột cao nhất là nhóm tuổi khách hàng cốt lõi — nên chọn KOL, kênh và thông điệp phù hợp lứa tuổi này.",
        tech="`pd.cut(tuoi, bins=range(15,65,5), right=False)` — mỗi nhóm gồm 5 tuổi, khoảng đóng bên trái.")
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
    with st.expander("ℹ️ Giải thích 9 phân khúc RFM — di chuột vào biểu tượng (i) để xem nhanh, hoặc mở bảng bên dưới"):
        st.caption("RFM chấm điểm mỗi khách theo Recency (R – mua gần đây), Frequency (F – thường xuyên), Monetary (M – chi nhiều); mỗi chiều 1–5 điểm. Tổ hợp điểm quyết định phân khúc.")
        rows=[[k, v[0], v[1], v[2]] for k,v in SEG_DESC.items()]
        st.dataframe(pd.DataFrame(rows,columns=["Phân khúc","Ý nghĩa","Đặc điểm R-F-M","Gợi ý hành động"]),width="stretch",hide_index=True)
    # Chips co tooltip (title=) cho tung phan khuc
    chips="".join(
        f"<span title=\"{v[0]} · {v[1]} · {v[2]}\" style='display:inline-block;background:#fff;border:1px solid {LINE};"
        f"border-left:4px solid {ROSE};border-radius:9px;padding:4px 9px;margin:3px 6px 3px 0;font-size:12px;color:{INK};cursor:help'>"
        f"<b>{k}</b> <span style='color:{MUTED};font-size:10.5px'>{v[1]}</span></span>"
        for k,v in SEG_DESC.items())
    st.markdown(f"<div style='margin:2px 0 12px'>{chips}</div>", unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1:
        b=card("Treemap: phân khúc theo tổng chi tiêu","Ô càng lớn = nhóm đó mang về càng nhiều tiền",
            tip="RFM = Recency (mua gần đây), Frequency (mua thường xuyên), Monetary (chi nhiều). Diện tích mỗi ô tỷ lệ với doanh thu nhóm đó tạo ra.")
        fig=go.Figure(go.Treemap(labels=agg.index,parents=[""]*len(agg),values=agg["m"],marker=dict(colors=PAL*3),
            texttemplate="%{label}<br>%{value:,.0f}<br>%{percentRoot}",
            hovertemplate="%{label}<br>Doanh thu: %{value:,.0f}<br>Tỷ trọng: %{percentRoot}<extra></extra>")); lay(fig,360)
        show(b,fig,agg.reset_index().rename(columns={"phan_khuc_rfm":"Phân khúc","n":"Số khách","m":"Doanh thu","pct_kh":"% khách","pct_dt":"% doanh thu"}),
            "03_treemap_phan_khuc.csv",ins=top_ins(agg["m"],"doanh thu"),
            how="Nhìn ô lớn nhất trước — đó là nhóm khách đang nuôi doanh nghiệp. Nếu một ô chiếm quá nửa diện tích, doanh thu đang bị phụ thuộc rủi ro vào nhóm đó.",
            tech="`groupby('phan_khuc_rfm')` với m = SUM(tong_chi_tieu). %percentRoot là tỷ trọng trên tổng toàn bộ.")
    with c2:
        b=card("Doanh thu theo phân khúc (giảm dần)","Xếp hạng 9 nhóm theo tiền mang về",
            tip="Cùng dữ liệu với treemap bên trái nhưng dạng cột, dễ so sánh chính xác hai nhóm liền kề.")
        fig=barv(agg.index,agg["m"].values,ROSE); fig.update_xaxes(tickangle=-25,title="Phân khúc RFM"); fig.update_yaxes(title="Doanh thu (VNĐ)")
        show(b,fig,ser_df(agg["m"],"Phân khúc","Doanh thu"),"03_doanh_thu_phan_khuc.csv",
            ins=(f"3 nhóm dẫn đầu tạo <b>{_pct(agg['m'].iloc[:3].sum(),agg['m'].sum()):.1f}%</b> doanh thu nhưng chỉ chiếm "
                 f"<b>{_pct(agg['n'].iloc[:3].sum(),agg['n'].sum()):.1f}%</b> số khách." if len(agg)>=3 else ""),
            how="So hai cột: một nhóm ít người nhưng cột cao = khách chất lượng; nhóm đông người mà cột thấp = còn nhiều dư địa nâng giá trị.",
            tech="Sắp xếp giảm dần theo SUM(tong_chi_tieu) trong mart_customer_rfm.")

    c3,c4=st.columns(2)
    with c3:
        b=card("Donut: tỷ trọng khách theo phân khúc","Cơ cấu SỐ NGƯỜI (khác với biểu đồ tiền ở trên)",
            tip="Biểu đồ này đếm ĐẦU NGƯỜI, không phải tiền. So sánh với treemap để thấy chênh lệch: nhóm đông người chưa chắc đã tạo nhiều doanh thu.")
        fig=go.Figure(go.Pie(labels=agg.index,values=agg["n"],hole=.55,marker=dict(colors=PAL*3),textinfo="label+percent",textfont=dict(size=10),
            hovertemplate="%{label}<br>%{value:,.0f} khách (%{percent})<extra></extra>"))
        lay(fig,360)
        _bign=agg["n"].idxmax(); _kh=agg.loc[_bign,'pct_kh']; _dt=agg.loc[_bign,'pct_dt']
        _cmp=("và tạo tới" if _dt>_kh*1.2 else ("nhưng chỉ tạo" if _dt<_kh*0.8 else "và tạo"))
        _tail=(" — nhóm này vừa đông vừa sinh lời, cần giữ bằng mọi giá." if _dt>_kh*1.2
               else " — đông người nhưng giá trị thấp, cần chiến dịch nâng hạng." if _dt<_kh*0.8 else ".")
        show(b,fig,ser_df(agg["n"],"Phân khúc","Số khách"),"03_ty_trong_khach.csv",
            ins=(f"Nhóm đông nhất là <b>{_bign}</b> với {iint(agg.loc[_bign,'n'])} khách "
                 f"({_kh:.1f}% số khách) {_cmp} <b>{_dt:.1f}%</b> doanh thu{_tail}"),
            how="Đặt cạnh treemap: nếu vòng tròn này bị chiếm bởi nhóm mà treemap lại nhỏ, nghĩa là rất nhiều khách giá trị thấp — cần chiến dịch nâng hạng.",
            tech="Đếm distinct ma_khach_hang theo phân khúc, vẽ dạng donut (hole=0.55).")
    with c4:
        b=card("Scatter: điểm R × tổng chi tiêu","Mỗi chấm là 1 khách · chấm to = mua nhiều lần",
            tip="Trục ngang: điểm R (1 = mua đã rất lâu, 5 = vừa mua gần đây). Trục dọc: tổng tiền khách đã chi. Kích thước chấm theo số lần mua.")
        samp=RFM.sample(min(4000,len(RFM)),random_state=1); fig=go.Figure()
        for i,seg in enumerate(sorted(samp.phan_khuc_rfm.unique())):
            dd=samp[samp.phan_khuc_rfm==seg]
            fig.add_trace(go.Scatter(x=dd["diem_R"],y=dd["tong_chi_tieu"],mode="markers",name=seg,
                marker=dict(size=np.clip(dd["tan_suat_mua"]*2,4,18),color=PAL[i%len(PAL)],opacity=.6),
                hovertemplate=f"{seg}<br>Điểm R=%{{x}}<br>Đã chi %{{y:,.0f}}<extra></extra>"))
        lay(fig,360,legend=True); fig.update_xaxes(title="Điểm R — 1: lâu rồi chưa mua → 5: vừa mua gần đây")
        fig.update_yaxes(title="Tổng chi tiêu (VNĐ)",tickformat="~s")
        fig.update_layout(legend=dict(font=dict(size=8)))
        _hv=RFM[(RFM["diem_R"]<=2)&(RFM["tong_chi_tieu"]>=RFM["tong_chi_tieu"].quantile(.8))]
        show(b,fig,samp[["ma_khach_hang","phan_khuc_rfm","diem_R","diem_F","diem_M","tan_suat_mua","tong_chi_tieu"]],"03_scatter_R_chi_tieu.csv",
            ins=(f"Góc trên bên trái là vùng báo động: <b>{iint(len(_hv))} khách</b> từng chi nhiều (top 20%) nhưng điểm R chỉ 1–2 — "
                 f"tương đương <b>{vnd(_hv['tong_chi_tieu'].sum())}</b> giá trị đang có nguy cơ mất. Đây là nhóm cần win-back trước tiên."),
            how="Đọc theo 4 góc: **trên–phải** = khách VIP đang hoạt động (giữ chân); **trên–trái** = khách giá trị cao đã nguội (cần kéo lại gấp); "
                 "**dưới–phải** = khách mới, chi ít (nuôi lên); **dưới–trái** = đã rời bỏ (chi phí thấp thôi).",
            tech="Lấy mẫu ngẫu nhiên tối đa 4.000 khách (random_state=1) cho biểu đồ chạy nhẹ; câu Đọc nhanh tính trên **toàn bộ** dữ liệu RFM.")

    b=card("Matrix Heatmap: điểm R × điểm F = số khách","Bảng đếm khách theo tổ hợp điểm — ô đậm là nơi tập trung đông khách",
        tip="Điểm R và F đều từ 1 đến 5 (5 là tốt nhất). Ví dụ ô R5–F1 là khách vừa mua lần đầu; ô R1–F5 là khách từng mua rất nhiều nhưng đã bỏ đi.")
    mat=RFM.pivot_table(index="diem_R",columns="diem_F",values="ma_khach_hang",aggfunc="count").sort_index(ascending=False)
    fig=go.Figure(go.Heatmap(z=mat.values,x=[f"F{c}" for c in mat.columns],y=[f"R{r}" for r in mat.index],
        colorscale=[[0,"#F7ECEA"],[1,ROSE]],text=mat.values,texttemplate="%{text}",colorbar=dict(title="Số KH",thickness=10),
        hovertemplate="Điểm R=%{y}, F=%{x}<br>%{z:,.0f} khách<extra></extra>"))
    lay(fig,340); fig.update_xaxes(title="Điểm F — mua thường xuyên (1 thấp → 5 cao)")
    fig.update_yaxes(title="Điểm R — mua gần đây")
    _flat=mat.stack(); _mx=_flat.idxmax() if len(_flat) else None
    show(b,fig,mat.reset_index(),"03_matrix_R_F.csv",
        ins=(f"Ô đông nhất là <b>R{_mx[0]}–F{_mx[1]}</b> với {iint(_flat.max())} khách "
             f"({_pct(_flat.max(),_flat.sum()):.1f}% tổng). Cột F1 chiếm <b>{_pct(mat.get(1,pd.Series(dtype=float)).sum(),_flat.sum()):.1f}%</b> — "
             f"đây là khách chỉ mới mua 1 lần, dư địa lớn nhất để tăng tần suất." if _mx is not None else ""),
        how="Càng về góc trên–phải (R5, F5) càng là khách tốt. Đám đông dồn ở cột F1 nghĩa là đa số khách mua một lần rồi thôi — ưu tiên chiến dịch mua lần 2.",
        tech="`pivot_table(index='diem_R', columns='diem_F', aggfunc='count')`. Điểm R/F chia theo ngũ phân vị (quintile) trong mart_customer_rfm.")

    b=card("Bảng 9 phân khúc RFM","Số khách · % khách · Doanh thu · % doanh thu — bảng tổng hợp để đối chiếu",
        tip="So sánh cột '% khách' với '% doanh thu': chênh lệch càng lớn thì nhóm đó càng đặc biệt (rất giá trị hoặc rất kém giá trị).")
    disp=agg.reset_index().rename(columns={"phan_khuc_rfm":"Phân khúc","n":"Số khách"})
    disp["% khách"]=disp["pct_kh"].map(lambda v:f"{v:.1f}%"); disp["% doanh thu"]=disp["pct_dt"].map(lambda v:f"{v:.1f}%"); disp["Doanh thu"]=disp["m"].map(vnd)
    disp["Ý nghĩa"]=disp["Phân khúc"].map(lambda x: SEG_DESC.get(x,("",""," "))[0])
    disp["Nên làm gì"]=disp["Phân khúc"].map(lambda x: SEG_DESC.get(x,("","",""))[2])
    b.dataframe(disp[["Phân khúc","Số khách","% khách","Doanh thu","% doanh thu","Ý nghĩa","Nên làm gì"]],width="stretch",hide_index=True)
    b.markdown("<div class='foot'>Cột <b>Ý nghĩa</b> và <b>Nên làm gì</b> được ghép tự động từ bảng định nghĩa 9 phân khúc RFM ở phần đầu trang.</div>",unsafe_allow_html=True)
    if SHOW_DL:
        _DL[0]+=1
        b.download_button("Tải dữ liệu biểu đồ (.csv)",
            disp[["Phân khúc","Số khách","% khách","Doanh thu","% doanh thu","Ý nghĩa","Nên làm gì"]].to_csv(index=False).encode("utf-8-sig"),
            "03_bang_9_phan_khuc.csv","text/csv",key=f"dl{_DL[0]}")


# ═══ DASHBOARD 4 — COHORT ═══════════════════════════════════════════════
elif page==PAGES[3]:
    st.title("Phân tích Giữ chân Khách hàng"); st.caption(PAGE_TAGS[3]); hero(*HERO_IMG[3])
    st.markdown("<div class='read'>Nhóm khách mua lần đầu ở mỗi tháng, sau đó bao nhiêu % còn quay lại. Với skincare, retention thường "
                "giảm mạnh sau ~3 tháng khi hết chu kỳ dùng sản phẩm đầu tiên.</div>", unsafe_allow_html=True)
    st.markdown("<div class='note'><b>Nguồn:</b> mart_cohort_retention (48 cohort). Matrix retention + Retention Curve.</div>", unsafe_allow_html=True)
    k=st.columns(3)
    k[0].metric("Retention Rate (TB)",f"{COH['ty_le_giu_chan'].mean()*100:.1f}%",
        help="Tỷ lệ giữ chân trung bình trên tất cả cohort và tất cả kỳ. Càng cao càng tốt.")
    k[1].metric("Cohort Size (TB)",f"{COH['quy_mo_cohort'].mean():.0f}",
        help="Mỗi tháng trung bình có bao nhiêu khách mua lần đầu.")
    k[2].metric("Số cohort",iint(COH['thang_cohort'].nunique()),
        help="Số nhóm khách theo tháng mua đầu tiên đang được theo dõi.")
    st.markdown(f"""<div class='kpi-legend'>
      <b>Cohort là gì?</b> Là một nhóm khách có cùng <b>tháng mua hàng đầu tiên</b>. Ví dụ cohort “2024-03” gồm tất cả khách lần đầu mua vào tháng 3/2024.
      <br><b>Kỳ (M0, M1, M2…)</b> là số tháng tính từ lần mua đầu: M0 = ngay tháng đó (luôn 100%), M1 = tháng kế tiếp, M2 = 2 tháng sau…
      <br><b>% giữ chân</b> = trong nhóm đó, bao nhiêu % khách còn quay lại mua ở kỳ tương ứng.
    </div>""", unsafe_allow_html=True)
    COH2=COH.copy(); COH2["nam_cohort"]=COH2["thang_cohort"].astype(str).str[:4]; years=sorted(COH2["nam_cohort"].unique())
    yc=st.container(border=True)
    yc.markdown("<div class='slicer-group' style='margin-top:0'>Lọc theo năm cohort</div>", unsafe_allow_html=True)
    sel_years=yc.multiselect("Năm cohort",years,default=years,help="Chọn năm để chỉ xem cohort bắt đầu mua trong năm đó.")
    COH_y=COH2[COH2["nam_cohort"].isin(sel_years)] if sel_years else COH2
    cohorts=sorted(COH_y["thang_cohort"].unique())
    if not cohorts: st.warning("Không có cohort theo năm đã chọn."); st.stop()
    # Hien thi mac dinh: 12 cohort gan nhat, toi da 12 ky (bo slider cho gon)
    n_show=min(12,len(cohorts)); kmax=int(COH_y["ky_cohort"].max()); max_k=min(12,kmax)
    sel=cohorts[-n_show:]; sub=COH_y[(COH_y["thang_cohort"].isin(sel))&(COH_y["ky_cohort"]<=max_k)]
    mat=sub.pivot(index="thang_cohort",columns="ky_cohort",values="ty_le_giu_chan")*100

    b=card("Matrix Retention (Heatmap)","Hàng = nhóm khách theo tháng đầu mua · Cột = số tháng sau đó · Số trong ô = % còn quay lại",
        tip="Đọc theo HÀNG NGANG để xem một nhóm khách rơi rụng dần theo thời gian; đọc theo CỘT DỌC để so các nhóm với nhau ở cùng một mốc tháng.")
    fig=go.Figure(go.Heatmap(z=mat.values,x=[f"M{c}" for c in mat.columns],y=[str(i) for i in mat.index],
        colorscale=[[0,"#F4F7F5"],[1,SAGE]],text=mat.values,texttemplate="%{text:.0f}",textfont=dict(size=9),colorbar=dict(title="%",thickness=10),
        hovertemplate="Cohort %{y} · kỳ %{x}<br>Còn %{z:.1f}% khách quay lại<extra></extra>"))
    lay(fig,420); fig.update_yaxes(autorange="reversed",title="Cohort (tháng mua đầu tiên)")
    fig.update_xaxes(title="Kỳ — số tháng kể từ lần mua đầu (M0 = tháng đầu tiên)")
    _m1=sub[sub["ky_cohort"]==1]["ty_le_giu_chan"].mean()*100 if (sub["ky_cohort"]==1).any() else 0
    _m3=sub[sub["ky_cohort"]==3]["ty_le_giu_chan"].mean()*100 if (sub["ky_cohort"]==3).any() else 0
    show(b,fig,mat.round(2).reset_index(),"04_matrix_retention.csv",
        ins=(f"Sau 1 tháng còn <b>{_m1:.1f}%</b> khách quay lại; sau 3 tháng còn <b>{_m3:.1f}%</b> — "
             f"tức khoảng <b>{100-_m1:.0f}%</b> khách rời đi ngay sau tháng đầu tiên. Đây là điểm rò rỉ lớn nhất cần bịt."),
        how="Ô càng xanh đậm = càng nhiều khách quay lại. Nếu cả một cột dọc đột nhiên nhạt đi, tháng đó có sự cố (hết hàng, đổi giá, dừng quảng cáo). "
            "Nếu một hàng ngang nhạt nhanh hơn các hàng khác, nhóm khách tháng đó chất lượng thấp.",
        tech="Nguồn mart_cohort_retention · ty_le_giu_chan = khach_hoat_dong / quy_mo_cohort. Hiển thị 12 cohort gần nhất × tối đa 12 kỳ cho dễ đọc; tải CSV để xem đầy đủ.")

    b=card("Retention Curve","Đường hồng đậm = trung bình các cohort · đường xám mảnh = từng cohort riêng lẻ",
        tip="Cùng dữ liệu với heatmap ở trên nhưng vẽ dạng đường, để thấy rõ tốc độ rơi của tỷ lệ giữ chân theo thời gian.")
    fig=go.Figure()
    for ch in sel:
        dd=sub[sub["thang_cohort"]==ch].sort_values("ky_cohort")
        fig.add_trace(go.Scatter(x=dd["ky_cohort"],y=dd["ty_le_giu_chan"]*100,mode="lines",showlegend=False,
            line=dict(width=1,color="rgba(138,123,108,.28)"),hovertemplate=ch+" · M%{x}<br>%{y:.1f}%<extra></extra>"))
    avg=sub.groupby("ky_cohort")["ty_le_giu_chan"].mean().sort_index()*100
    fig.add_trace(go.Scatter(x=avg.index,y=avg.values,mode="lines+markers+text",name="Trung bình cohort",line=dict(width=4,color=ROSE),
        marker=dict(size=7,color=ROSE),text=[f"{v:.0f}%" for v in avg.values],textposition="top center",textfont=dict(size=11,color=INK),
        cliponaxis=False,hovertemplate="Kỳ M%{x}<br>TB %{y:.1f}%<extra></extra>"))
    lay(fig,380,legend=True); fig.update_xaxes(title="Kỳ — số tháng kể từ lần mua đầu")
    fig.update_yaxes(title="% khách còn quay lại",range=[0,max(100,avg.max()*1.15 if len(avg) else 100)])
    _ins4=""
    if len(avg)>1:
        _drop=avg.iloc[0]-avg.iloc[1]
        _ins4=(f"Trung bình {len(sel)} cohort: từ 100% ở kỳ đầu rơi xuống <b>{avg.iloc[1]:.1f}%</b> ngay kỳ M1 "
               f"(mất {_drop:.0f} điểm %), và còn <b>{avg.iloc[-1]:.1f}%</b> ở kỳ M{int(avg.index[-1])}. "
               f"Với skincare, đây là lúc khách dùng hết lọ đầu tiên — nếu không nhắc mua lại đúng thời điểm này thì rất khó kéo về sau.")
    show(b,fig,sub[["thang_cohort","ky_cohort","khach_hoat_dong","quy_mo_cohort","ty_le_giu_chan"]].rename(
            columns={"thang_cohort":"Cohort","ky_cohort":"Kỳ","khach_hoat_dong":"Khách hoạt động","quy_mo_cohort":"Quy mô cohort","ty_le_giu_chan":"Tỷ lệ giữ chân"}),
        "04_retention_curve.csv",ins=_ins4,
        how="Đường hồng đậm là mức trung bình — nhìn nó để biết bức tranh chung. Các đường xám là từng nhóm khách; đường nào nằm cao hơn hẳn đường hồng "
            "là nhóm khách chất lượng, đáng tìm hiểu tháng đó đã làm gì đúng.",
        tech="Đường trung bình = `sub.groupby('ky_cohort')['ty_le_giu_chan'].mean()`. Kỳ M0 luôn bằng 100% theo định nghĩa cohort.")


# ═══ DASHBOARD 5 — ANOMALY ══════════════════════════════════════════════
elif page==PAGES[4]:
    st.title("Phát hiện Bất thường"); st.caption(PAGE_TAGS[4]); hero(*HERO_IMG[4])
    st.markdown("<div class='read'>Khoanh vùng những đơn có giá trị lệch xa mức thông thường <b>của chính sản phẩm đó</b> (ví dụ gom số lượng lớn, "
                "hoặc giá thấp bất thường), để đội vận hành rà soát reseller / gian lận / lỗi nhập liệu. Đây là danh sách <i>cần kiểm tra</i>, "
                "không phải danh sách <i>kết luận sai phạm</i>.</div>", unsafe_allow_html=True)
    st.markdown("<div class='note'><b>Nguồn:</b> mart_anomaly_flag (tương ứng 1–1 với fact_transaction). <b>Phương pháp:</b> quy tắc IQR "
                "tính riêng cho từng mã sản phẩm; ngưỡng đã được tính sẵn trong các cột phan_vi_25 / phan_vi_75 / khoang_tu_phan_vi.</div>", unsafe_allow_html=True)
    A=ANOM[(ANOM["ngay_giao_dich"].dt.date>=d0)&(ANOM["ngay_giao_dich"].dt.date<=d1)]
    if ANY_FILTER: A=A[A["ma_giao_dich"].isin(FT["ma_giao_dich"])]
    if A.empty: st.warning("Không có dữ liệu."); st.stop()
    RED="#B5555A"
    n_an=int(A["co_bat_thuong"].sum()); rate=A["co_bat_thuong"].mean() if len(A) else 0
    val_an=A.loc[A.co_bat_thuong==1,"gia_tri_sau_giam"].sum(); cust_an=A.loc[A.co_bat_thuong==1,"ma_khach_hang"].nunique()
    k=st.columns(4)
    k[0].metric("Giao dịch bất thường",iint(n_an),help="Số đơn bị đánh dấu co_bat_thuong = 1 theo ngưỡng IQR.")
    k[1].metric("Tỷ lệ bất thường",f"{rate*100:.1f}%",help="Số đơn bất thường ÷ tổng đơn trong khoảng đang lọc.")
    k[2].metric("Giá trị bất thường",vnd(val_an),help="Tổng tiền của riêng các đơn bất thường.")
    k[3].metric("Số khách bất thường",iint(cust_an),help="Bao nhiêu khách hàng khác nhau có ít nhất 1 đơn bất thường.")
    # Nguong IQR duoc tinh RIENG cho TUNG SAN PHAM (moi dong co phan_vi_25/75 rieng)
    A=A.copy()
    A["_hi"]=A["phan_vi_75"]+1.5*A["khoang_tu_phan_vi"]; A["_lo"]=A["phan_vi_25"]-1.5*A["khoang_tu_phan_vi"]
    A["_loai"]=np.where(A["co_bat_thuong"]==0,"Bình thường",
                np.where(A["gia_tri_sau_giam"]>A["_hi"],"Cao bất thường","Thấp bất thường"))
    n_hi=int((A["_loai"]=="Cao bất thường").sum()); n_lo=int((A["_loai"]=="Thấp bất thường").sum())
    v_hi=A.loc[A["_loai"]=="Cao bất thường","gia_tri_sau_giam"].sum()
    st.markdown(f"""<div class='kpi-legend'>
      <b>“Bất thường” ở đây nghĩa là gì?</b> Không phải kết luận gian lận — chỉ là <i>đơn có giá trị lệch xa mức thông thường <u>của chính sản phẩm đó</u></i>, cần người rà lại.<br>
      <b>Cách xác định</b> (quy tắc IQR – khoảng tứ phân vị, chuẩn thống kê phổ biến): với <u>từng mã sản phẩm</u>, sắp mọi đơn của nó theo giá trị rồi lấy
      mốc 25% (Q1) và mốc 75% (Q3); khoảng giữa hai mốc là IQR. Đơn bị gắn cờ khi vượt <b>Q3 + 1,5×IQR</b> (cao bất thường) hoặc thấp hơn <b>Q1 − 1,5×IQR</b> (thấp bất thường).
      Vì mỗi sản phẩm có mức giá riêng nên ngưỡng cũng khác nhau — không có một con số chung cho toàn bộ shop.<br>
      <b>Kết quả hiện tại:</b> <b>{iint(n_hi)}</b> đơn cao bất thường (trị giá {vnd(v_hi)}) và <b>{iint(n_lo)}</b> đơn thấp bất thường.<br>
      <b>Nguyên nhân thường gặp:</b> cao — reseller gom hàng, đơn quà tặng/doanh nghiệp, nhập sai số lượng; thấp — giảm giá sâu bất thường, sai giá, hoặc lỗi nhập liệu.
    </div>""", unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1:
        b=card("Box & Whisker: giá trị đơn theo 3 nhóm","Hộp = 50% số đơn ở giữa · vạch trong hộp = giá trị trung vị",
            tip="Hộp bao 50% đơn ở giữa (từ mốc 25% đến 75%). Vì ngưỡng tính riêng cho từng sản phẩm nên hộp 'Cao bất thường' không nhất thiết nằm hẳn trên hộp 'Bình thường'.")
        fig=go.Figure()
        for nm,cl in [("Bình thường",SAGE),("Cao bất thường",RED),("Thấp bất thường",GOLD)]:
            dd=A.loc[A["_loai"]==nm,"gia_tri_sau_giam"]
            if len(dd): fig.add_trace(go.Box(y=dd,name=nm,marker_color=cl))
        lay(fig,340,legend=True); fig.update_yaxes(tickformat="~s",title="Giá trị đơn sau giảm giá (VNĐ)")
        _n0=A.loc[A["_loai"]=="Bình thường","gia_tri_sau_giam"]; _nh=A.loc[A["_loai"]=="Cao bất thường","gia_tri_sau_giam"]
        show(b,fig,A[["ma_giao_dich","ma_san_pham","gia_tri_sau_giam","co_bat_thuong","_loai"]].rename(columns={"_loai":"Phân loại"}),
            "05_box_gia_tri.csv",
            ins=(f"Đơn bình thường có trung vị <b>{vnd(_n0.median())}</b>; nhóm cao bất thường trung vị <b>{vnd(_nh.median())}</b> "
                 f"và có đơn lớn nhất tới <b>{vnd(_nh.max())}</b>. Tuy chỉ chiếm {rate*100:.1f}% số đơn, toàn bộ nhóm bất thường nắm "
                 f"<b>{_pct(A.loc[A.co_bat_thuong==1,'gia_tri_sau_giam'].sum(),A['gia_tri_sau_giam'].sum()):.1f}%</b> tổng giá trị."
                 if len(_n0) and len(_nh) else ""),
            how="Hộp xanh là mặt bằng chung. Hộp đỏ trải dài lên rất cao = có những đơn lớn gấp nhiều lần bình thường, đó là các đơn cần rà tay. "
                "Hộp vàng (thấp bất thường) thường là lỗi giá hoặc giảm giá quá sâu, nên kiểm tra chính sách khuyến mãi.",
            tech="Box plot chuẩn Tukey: đáy hộp = phân vị 25, đỉnh hộp = phân vị 75, vạch giữa = trung vị, râu = 1,5 × IQR. "
                 "Lưu ý: hộp ở đây vẽ trên **toàn bộ đơn gộp chung**, còn việc gắn cờ lại tính riêng theo từng mã sản phẩm — nên hai hộp có thể chồng lấn nhau.")
    with c2:
        b=card("Histogram: phân bố giá trị đơn","Đa số đơn tập trung ở đâu, và cái đuôi kéo dài tới đâu",
            tip="Chia giá trị đơn thành 40 khoảng và đếm số đơn trong mỗi khoảng. Đuôi dài bên phải là các đơn giá trị rất lớn — phần lớn nằm trong nhóm bị gắn cờ.")
        cnt,edg=np.histogram(A["gia_tri_sau_giam"].values,bins=40)
        fig=go.Figure(go.Bar(x=[(edg[i]+edg[i+1])/2 for i in range(len(edg)-1)],y=cnt,marker_color=SKY,
            hovertemplate="Quanh mức %{x:,.0f}<br>%{y} đơn<extra></extra>")); lay(fig,340)
        fig.update_xaxes(tickformat="~s",title="Giá trị đơn sau giảm giá (VNĐ)"); fig.update_yaxes(title="Số đơn")
        _md=A["gia_tri_sau_giam"].median()
        show(b,fig,pd.DataFrame({"Khoảng giá trị":[(edg[i]+edg[i+1])/2 for i in range(len(edg)-1)],"Số đơn":cnt}),"05_histogram_gia_tri.csv",
            ins=(f"Một nửa số đơn có giá trị dưới <b>{vnd(_md)}</b>, nhưng đuôi bên phải kéo tới <b>{vnd(A['gia_tri_sau_giam'].max())}</b>. "
                 f"Tổng cộng <b>{iint(n_an)} đơn</b> bị gắn cờ, trị giá <b>{vnd(val_an)}</b> — mỗi đơn được so với ngưỡng riêng của sản phẩm nó thuộc về."),
            how="Cột cao ở bên trái là mức mua phổ biến của khách lẻ. Càng sang phải đơn càng lớn và càng hiếm — đó là vùng cần rà soát thủ công.",
            tech="`np.histogram(bins=40)` trên gia_tri_sau_giam của toàn bộ đơn trong khoảng lọc (cả bình thường lẫn bất thường).")

    b=card("Scatter: giá trị từng đơn theo ngày","Mỗi chấm là 1 đơn · chấm đỏ = bị gắn cờ bất thường",
        tip="Dùng để phát hiện các cụm bất thường dồn vào một vài ngày — thường trùng đợt sale lớn hoặc một reseller gom hàng liên tục.")
    samp=A.sample(min(6000,len(A)),random_state=1); fig=go.Figure()
    for lab,cl,nm in [(0,SAGE,"Bình thường"),(1,RED,"Bất thường")]:
        dd=samp[samp.co_bat_thuong==lab]
        fig.add_trace(go.Scatter(x=dd["ngay_giao_dich"],y=dd["gia_tri_sau_giam"],mode="markers",name=nm,
            marker=dict(size=5,color=cl,opacity=.5),hovertemplate="%{x|%d/%m/%Y}<br>%{y:,.0f}<extra></extra>"))
    lay(fig,340,legend=True); fig.update_yaxes(tickformat="~s",title="Giá trị đơn (VNĐ)"); fig.update_xaxes(title="Ngày giao dịch")
    _byday=A[A.co_bat_thuong==1].groupby(A[A.co_bat_thuong==1]["ngay_giao_dich"].dt.date).size()
    show(b,fig,samp[["ma_giao_dich","ma_khach_hang","ngay_giao_dich","gia_tri_sau_giam","co_bat_thuong"]],"05_scatter_theo_ngay.csv",
        ins=(f"Ngày có nhiều đơn bất thường nhất là <b>{_byday.idxmax().strftime('%d/%m/%Y')}</b> với {iint(_byday.max())} đơn. "
             f"Các chấm đỏ rải đều theo thời gian nghĩa là hiện tượng mang tính thường xuyên, không phải sự cố một lần." if len(_byday) else ""),
        how="Nếu chấm đỏ dồn cục vào vài ngày → nhiều khả năng là đợt sale hoặc một khách gom hàng, kiểm tra riêng ngày đó. "
            "Nếu rải đều quanh năm → nên lập quy trình rà soát định kỳ thay vì xử lý vụ việc.",
        tech="Lấy mẫu ngẫu nhiên tối đa 6.000 đơn để biểu đồ nhẹ; câu Đọc nhanh tính trên toàn bộ dữ liệu đã lọc.")

    b=card("Số giao dịch bất thường theo tháng","Xu hướng — hiện tượng đang tăng hay giảm dần",
        tip="Đếm số đơn bị gắn cờ trong mỗi tháng. Đường đi lên liên tục là dấu hiệu cần siết quy trình kiểm soát.")
    A2=A.copy(); A2["ym"]=A2["ngay_giao_dich"].dt.to_period("M").astype(str); s=A2.groupby("ym")["co_bat_thuong"].sum().sort_index()
    fig=go.Figure(go.Scatter(x=s.index,y=s.values,mode="lines+markers",line=dict(color=RED,width=3),fill="tozeroy",fillcolor="rgba(181,85,90,.10)",
        hovertemplate="%{x}<br>%{y} đơn bất thường<extra></extra>"))
    lay(fig,300); fig.update_yaxes(title="Số đơn bất thường"); fig.update_xaxes(title="Tháng")
    show(b,fig,ser_df(s,"Tháng","Số đơn bất thường"),"05_bat_thuong_theo_thang.csv",
        ins=trend_ins(s,"Số đơn bất thường",money=False),
        how="Đường đi lên = ngày càng nhiều đơn cần rà. Nếu trùng với tháng có doanh thu tăng mạnh thì phần lớn là do bán nhiều, không đáng lo; "
            "nếu tăng trong tháng doanh thu bình thường thì cần kiểm tra kỹ.",
        tech="`groupby(tháng)['co_bat_thuong'].sum()` — cột co_bat_thuong nhận giá trị 0/1 nên tổng chính là số đơn bị gắn cờ.")

    b=card("Top 20 giao dịch bất thường","Danh sách cụ thể để đội vận hành rà tay — có thể là reseller / gom hàng / gian lận",
        tip="Sắp xếp theo giá trị giảm dần. Nên đối chiếu mã khách hàng: nếu một mã xuất hiện nhiều lần thì nhiều khả năng là reseller.")
    tb=(A[A.co_bat_thuong==1].sort_values("gia_tri_sau_giam",ascending=False).head(20)
        [["ma_giao_dich","ma_khach_hang","ma_san_pham","ngay_giao_dich","gia_tri_sau_giam"]].copy())
    tb["ngay_giao_dich"]=tb["ngay_giao_dich"].dt.strftime("%d/%m/%Y"); tb["gia_tri_sau_giam"]=tb["gia_tri_sau_giam"].map(lambda v:f"{int(v):,}".replace(",","."))
    tb.columns=["Mã giao dịch","Mã khách hàng","Mã sản phẩm","Ngày","Giá trị sau giảm (VNĐ)"]
    b.dataframe(tb,width="stretch",hide_index=True)
    _rep=A[A.co_bat_thuong==1]["ma_khach_hang"].value_counts()
    _repn=int((_rep>=2).sum())
    b.markdown(f"<div class='insight'><span class='lbl'>Đọc nhanh</span>Có <b>{iint(_repn)} khách</b> xuất hiện từ 2 đơn bất thường trở lên"
               + (f", nhiều nhất là <b>{_rep.index[0]}</b> với {iint(_rep.iloc[0])} đơn" if len(_rep) else "")
               + ". Nhóm lặp lại này nên được xem là reseller tiềm năng — có thể chuyển sang chính sách bán sỉ thay vì chặn.</div>", unsafe_allow_html=True)
    if SHOW_DL:
        _DL[0]+=1
        b.download_button("Tải toàn bộ đơn bất thường (.csv)",
            A[A.co_bat_thuong==1][["ma_giao_dich","ma_khach_hang","ma_san_pham","ngay_giao_dich","gia_tri_sau_giam"]].to_csv(index=False).encode("utf-8-sig"),
            "05_toan_bo_don_bat_thuong.csv","text/csv",key=f"dl{_DL[0]}")


# ═══ DASHBOARD 6 — PREDICTIVE + PRESCRIPTIVE ════════════════════════════
elif page==PAGES[5]:
    st.title("Dự báo & Khuyến nghị"); st.caption(PAGE_TAGS[5]); hero(*HERO_IMG[5])
    st.markdown("<div class='read'>Dự đoán tương lai (doanh thu · churn · CLV) rồi đề xuất hành động theo phong cách skincare: "
                "VIP Membership · Routine cá nhân hoá · Subscription Box · Win-back.</div>", unsafe_allow_html=True)
    st.markdown("<div class='note'>Tính bằng Python: Forecast (Prophet), Churn (RandomForest), CLV (lifetimes). Thiếu thư viện thì tự fallback.</div>", unsafe_allow_html=True)
    if "sub6" not in st.session_state: st.session_state.sub6=0
    SUB6=["Dự báo doanh thu","Churn & CLV","Khuyến nghị hành động"]
    scols=st.columns(3)
    for i,lbl in enumerate(SUB6):
        if scols[i].button(lbl,key=f"sub6_{i}",use_container_width=True,
                           type=("primary" if st.session_state.sub6==i else "secondary")):
            st.session_state.sub6=i; st.rerun()
    sub6=st.session_state.sub6
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if sub6==0:
        @st.cache_data(show_spinner="Đang dự báo...")
        def forecast(txser):
            m=txser.copy(); monthly=m.set_index("ngay")["doanh_thu"].resample("MS").sum().reset_index(); monthly.columns=["ds","y"]; method="OLS mùa vụ (thay thế)"
            try:
                from prophet import Prophet
                mo=Prophet(yearly_seasonality=True); mo.fit(monthly)
                out=mo.predict(mo.make_future_dataframe(periods=6,freq="MS"))[["ds","yhat","yhat_lower","yhat_upper"]]; method="Prophet"
            except Exception:
                y=monthly["y"].values.astype(float);n=len(y);t=np.arange(n)
                M=pd.get_dummies(monthly["ds"].dt.month,prefix="m").reindex(columns=[f"m_{i}" for i in range(1,13)],fill_value=0).values.astype(float)
                X=np.column_stack([np.ones(n),t,M]);b,*_=np.linalg.lstsq(X,y,rcond=None);fit=X@b;sd=np.std(y-fit)
                fut=pd.period_range(monthly["ds"].dt.to_period("M").max()+1,periods=6,freq="M");tf=np.arange(n,n+6)
                Mf=pd.get_dummies(pd.Series([p.month for p in fut]),prefix="m").reindex(columns=[f"m_{i}" for i in range(1,13)],fill_value=0).values.astype(float)
                fcv=np.column_stack([np.ones(6),tf,Mf])@b; ds=list(monthly["ds"])+[p.to_timestamp() for p in fut]; yh=np.concatenate([fit,fcv])
                out=pd.DataFrame({"ds":ds,"yhat":yh,"yhat_lower":yh-1.96*sd,"yhat_upper":yh+1.96*sd})
            return monthly,out,method
        monthly,fc,fmethod=forecast(TX[["ngay","doanh_thu"]])
        b=card(f"Dự báo doanh thu 6 tháng tới — phương pháp: {fmethod}",
            "Đường hồng = số liệu thật đã bán · Đường vàng nét đứt = dự báo · Vùng hồng nhạt = khoảng dao động có thể xảy ra",
            tip="Dải tin cậy 95%: mô hình cho rằng doanh thu thực tế sẽ nằm trong vùng hồng nhạt này với xác suất khoảng 95%. Dải càng rộng thì độ chắc chắn càng thấp.")
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=fc["ds"],y=fc["yhat_upper"],mode="lines",line=dict(width=0),showlegend=False,hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=fc["ds"],y=fc["yhat_lower"],mode="lines",fill="tonexty",fillcolor="rgba(201,126,140,.14)",line=dict(width=0),
            name="Khoảng tin cậy 95%",showlegend=True,hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=monthly["ds"],y=monthly["y"],name="Thực tế đã bán",mode="lines+markers",line=dict(color=ROSE,width=3),
            hovertemplate="%{x|%m/%Y}<br>%{y:,.0f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=fc["ds"],y=fc["yhat"],name="Dự báo",mode="lines",line=dict(color=GOLD,width=2.5,dash="dash"),
            hovertemplate="%{x|%m/%Y}<br>Dự báo %{y:,.0f}<extra></extra>"))
        lay(fig,360,legend=True); fig.update_yaxes(tickformat="~s",title="Doanh thu (VNĐ)"); fig.update_xaxes(title="Tháng")
        _f6=fc.tail(6); _last12=monthly.tail(6)["y"].sum()
        _chg=_pct(_f6["yhat"].sum()-_last12,_last12) if _last12 else 0
        show(b,fig,fc.rename(columns={"ds":"Tháng","yhat":"Dự báo","yhat_lower":"Cận dưới","yhat_upper":"Cận trên"}),"06_du_bao_doanh_thu.csv",
            ins=(f"6 tháng tới dự báo đạt <b>{vnd(_f6['yhat'].sum())}</b>, {'tăng' if _chg>=0 else 'giảm'} <b>{abs(_chg):.1f}%</b> so với 6 tháng gần nhất "
                 f"({vnd(_last12)}). Kịch bản thấp nhất {vnd(_f6['yhat_lower'].sum())} — kịch bản cao nhất {vnd(_f6['yhat_upper'].sum())}."),
            how="Chỉ đọc phần đường vàng nét đứt (tương lai) kèm vùng hồng: đừng chốt kế hoạch theo đúng con số giữa, hãy lập kế hoạch tồn kho theo "
                "kịch bản cao và kế hoạch dòng tiền theo kịch bản thấp.",
            tech=(f"Phương pháp đang chạy: **{fmethod}**. Nếu máy có thư viện `prophet` thì dùng Prophet (bắt xu hướng + mùa vụ năm); "
                  "nếu không có, tự động chuyển sang hồi quy OLS với biến giả 12 tháng — cùng ý tưởng (xu hướng + mùa vụ) nhưng đơn giản hơn. "
                  "Dải tin cậy = ±1,96 × độ lệch chuẩn phần dư. Biểu đồ này dùng **toàn bộ** dữ liệu, không theo bộ lọc thời gian."))
        _k=st.columns(3)
        _k[0].metric("Doanh thu dự báo 6 tháng tới",vnd(_f6["yhat"].sum()),f"{_chg:+.1f}% so với 6 tháng gần nhất",
            help="Tổng giá trị giữa của dự báo cho 6 tháng kế tiếp.")
        _k[1].metric("Kịch bản thấp (cận dưới)",vnd(_f6["yhat_lower"].sum()),help="Dùng con số này để lập kế hoạch dòng tiền thận trọng.")
        _k[2].metric("Kịch bản cao (cận trên)",vnd(_f6["yhat_upper"].sum()),help="Dùng con số này để chuẩn bị tồn kho, tránh hết hàng.")

    elif sub6==1:
        @st.cache_data(show_spinner="Đang huấn luyện churn...")
        def churn_predict(rfm):
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import roc_auc_score
            r=rfm.copy(); r["churn_label"]=r["phan_khuc_rfm"].isin(["Lost","Hibernating","At Risk"]).astype(int)
            feats=["so_ngay_tu_lan_mua_cuoi","tan_suat_mua","tuoi_tho_khach_hang",
                   "tong_chi_tieu","gia_tri_don_hang_tb","tong_so_luong_mua","so_danh_muc_da_mua"]
            X=r[feats].fillna(0);y=r["churn_label"]
            Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
            clf=RandomForestClassifier(n_estimators=200,random_state=42,n_jobs=-1).fit(Xtr,ytr)
            auc=roc_auc_score(yte,clf.predict_proba(Xte)[:,1]); r["churn_probability"]=clf.predict_proba(X)[:,1]
            imp=pd.Series(clf.feature_importances_,index=feats).sort_values()
            return r[["ma_khach_hang","phan_khuc_rfm","churn_probability","tong_chi_tieu","gia_tri_don_hang_tb","tan_suat_mua","tuoi_tho_khach_hang","so_ngay_tu_lan_mua_cuoi"]],auc,imp,y.mean()
        churn,auc,imp,rate=churn_predict(RFM)
        @st.cache_data(show_spinner="Đang tính CLV...")
        def clv_predict(rfm):
            r=rfm.copy(); r["frequency"]=r["tan_suat_mua"]-1; r["T"]=r["tuoi_tho_khach_hang"]; r["recency"]=r["T"]-r["so_ngay_tu_lan_mua_cuoi"]; r["monetary_value"]=r["gia_tri_don_hang_tb"]; method="lifetimes (BG/NBD + Gamma-Gamma)"
            try:
                from lifetimes import BetaGeoFitter,GammaGammaFitter
                rr=r[(r["frequency"]>0)&(r["recency"]>=0)&(r["T"]>0)].copy()
                bgf=BetaGeoFitter(penalizer_coef=.01); bgf.fit(rr["frequency"],rr["recency"],rr["T"])
                ggf=GammaGammaFitter(penalizer_coef=.01); ggf.fit(rr["frequency"],rr["monetary_value"])
                rr["predicted_clv_90d"]=ggf.customer_lifetime_value(bgf,rr["frequency"],rr["recency"],rr["T"],rr["monetary_value"],time=3,freq="D",discount_rate=.01)
                r=r.merge(rr[["ma_khach_hang","predicted_clv_90d"]],on="ma_khach_hang",how="left")
            except Exception:
                method="Heuristic (thay thế lifetimes)"; r["predicted_clv_90d"]=(r["tan_suat_mua"]/r["T"].clip(lower=1)*90*r["monetary_value"]).clip(lower=0)
            r["predicted_clv_90d"]=r["predicted_clv_90d"].fillna(0); return r[["ma_khach_hang","predicted_clv_90d"]],method
        clv,cmethod=clv_predict(RFM); churn=churn.merge(clv,on="ma_khach_hang",how="left")
        k=st.columns(3)
        k[0].metric("ROC-AUC (churn RF)",f"{auc:.3f}",help="Thang 0,5–1,0. Từ 0,8 trở lên là mô hình phân biệt tốt khách sắp rời bỏ và khách sẽ ở lại.")
        k[1].metric("Tỷ lệ churn (nhãn)",f"{rate*100:.1f}%",help="Tỷ lệ khách được gán nhãn 'sẽ rời bỏ' theo định nghĩa phân khúc RFM.")
        k[2].metric("Cách tính CLV","lifetimes" if cmethod.startswith("life") else "heuristic",
            help="lifetimes = mô hình xác suất BG/NBD + Gamma-Gamma. heuristic = công thức xấp xỉ khi máy chưa cài thư viện.")
        st.markdown(f"""<div class='kpi-legend'>
          <b>Ba khái niệm cần biết trước khi đọc trang này</b><br>
          <b>Churn</b> (rời bỏ): khách ngừng mua. Mô hình chấm cho mỗi khách một <b>xác suất rời bỏ</b> từ 0 đến 1 — càng gần 1 càng dễ mất.<br>
          <b>CLV 90 ngày</b> (Customer Lifetime Value): ước tính khách đó sẽ chi thêm bao nhiêu tiền trong 3 tháng tới.<br>
          <b>ROC-AUC</b>: điểm chấm độ chính xác của mô hình. 0,5 = đoán bừa · 0,8 = tốt · 1,0 = hoàn hảo. Hiện tại: <b>{auc:.3f}</b>.<br>
          👉 Ghép hai con số lại: <i>khách vừa có xác suất rời bỏ cao vừa có CLV cao</i> chính là nhóm phải chăm sóc trước tiên.
        </div>""", unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            b=card("Phân phối xác suất rời bỏ (churn)","Có bao nhiêu khách rơi vào từng mức rủi ro",
                tip="Trục ngang: xác suất rời bỏ từ 0 (chắc chắn ở lại) tới 1 (gần như đã mất). Trục dọc: số khách trong mỗi mức.")
            cnt,edg=np.histogram(churn["churn_probability"].values,bins=25)
            fig=go.Figure(go.Bar(x=[(edg[i]+edg[i+1])/2 for i in range(len(edg)-1)],y=cnt,marker_color=ROSE,
                hovertemplate="Xác suất ~%{x:.2f}<br>%{y} khách<extra></extra>")); lay(fig)
            fig.update_xaxes(title="Xác suất rời bỏ (0 = an toàn → 1 = nguy cơ cao)"); fig.update_yaxes(title="Số khách")
            _hi=int((churn["churn_probability"]>=.7).sum()); _lo=int((churn["churn_probability"]<=.3).sum())
            show(b,fig,pd.DataFrame({"Mức xác suất":[(edg[i]+edg[i+1])/2 for i in range(len(edg)-1)],"Số khách":cnt}),"06_phan_bo_churn.csv",
                ins=(f"<b>{iint(_hi)} khách</b> ({_pct(_hi,len(churn)):.1f}%) có nguy cơ rời bỏ cao (≥ 0,7) — cần chiến dịch win-back ngay. "
                     f"Ngược lại <b>{iint(_lo)} khách</b> ({_pct(_lo,len(churn)):.1f}%) đang an toàn (≤ 0,3), phù hợp để upsell."),
                how="Biểu đồ dồn về bên trái = phần lớn khách đang khỏe mạnh. Dồn về bên phải = báo động, cần hành động ở quy mô lớn. "
                    "Hai cụm tách rời ở hai đầu nghĩa là mô hình phân biệt rất rõ hai nhóm.",
                tech="`RandomForestClassifier(n_estimators=200).predict_proba()[:,1]` chạy trên toàn bộ 48.809 khách trong mart_customer_rfm.")
        with c2:
            b=card("Yếu tố nào quyết định khách rời bỏ?","Thanh càng dài, yếu tố đó càng ảnh hưởng tới dự đoán",
                tip="Đây là feature importance của mô hình Random Forest — cho biết mô hình dựa nhiều nhất vào thông tin nào để đưa ra dự đoán.")
            _vn={"so_ngay_tu_lan_mua_cuoi":"Số ngày kể từ lần mua cuối","tan_suat_mua":"Số lần đã mua",
                 "tuoi_tho_khach_hang":"Số ngày gắn bó","tong_chi_tieu":"Tổng chi tiêu",
                 "gia_tri_don_hang_tb":"Giá trị đơn hàng TB","tong_so_luong_mua":"Tổng số lượng đã mua",
                 "so_danh_muc_da_mua":"Số danh mục đã mua"}
            fig=go.Figure(go.Bar(x=imp.values,y=[_vn.get(i,i) for i in imp.index],orientation="h",marker_color=GOLD,
                text=[f"{v:.2f}" for v in imp.values],textposition="outside",cliponaxis=False,
                hovertemplate="%{y}<br>Mức ảnh hưởng %{x:.3f}<extra></extra>"))
            lay(fig); fig.update_layout(margin=dict(l=180,r=50,t=14,b=30)); fig.update_xaxes(title="Mức độ ảnh hưởng (tổng = 1)")
            show(b,fig,pd.DataFrame({"Yếu tố":[_vn.get(i,i) for i in imp.index],"Mức ảnh hưởng":imp.values}),"06_yeu_to_churn.csv",
                ins=(f"Yếu tố quan trọng nhất là <b>{_vn.get(imp.index[-1],imp.index[-1])}</b> (chiếm {imp.iloc[-1]*100:.0f}% mức ảnh hưởng). "
                     f"Nghĩa là: muốn biết khách có sắp rời bỏ không, hãy nhìn vào chỉ số này đầu tiên."),
                how="Đọc từ dưới lên: thanh dài nhất ở dưới cùng là yếu tố mô hình dựa vào nhiều nhất. Đây cũng chính là 'đòn bẩy' để can thiệp — "
                    "ví dụ nếu 'số ngày kể từ lần mua cuối' quan trọng nhất thì việc nhắc mua lại đúng hạn sẽ có tác động lớn nhất.",
                tech=("`clf.feature_importances_` — tổng bằng 1, đo mức giảm impurity trung bình do mỗi biến mang lại trong rừng 200 cây. "
                      "Lưu ý: các biến điểm R/F/M (đã ngũ phân vị hoá) được **loại khỏi** tập feature vì chúng là đầu vào trực tiếp dùng để "
                      "gán `phan_khuc_rfm` — nếu giữ lại sẽ gây rò rỉ dữ liệu (mô hình học thuộc quy tắc gán nhãn thay vì dự đoán thật, AUC ảo cao gần 1.0). "
                      "Model hiện chỉ dùng các biến hành vi thô; do khung dữ liệu là snapshot RFM (không có tách theo mốc thời gian huấn luyện/tương lai), "
                      "biến số ngày kể từ lần mua cuối vẫn tương quan tự nhiên với nhãn — muốn triệt để hơn cần tách nhãn theo cửa sổ thời gian riêng."))
        b=card(f"CLV 90 ngày theo phân khúc — cách tính: {cmethod}","Mỗi chấm là 1 khách · trục dọc = số tiền dự kiến khách chi thêm trong 3 tháng tới",
            tip="CLV = Customer Lifetime Value. Nhóm nào có nhiều chấm nằm cao thì đáng đầu tư ngân sách chăm sóc hơn.")
        samp=churn.sample(min(4000,len(churn)),random_state=1); fig=go.Figure()
        for i,seg in enumerate(sorted(samp.phan_khuc_rfm.unique())):
            dd=samp[samp.phan_khuc_rfm==seg]
            fig.add_trace(go.Scatter(x=[seg]*len(dd),y=dd["predicted_clv_90d"],mode="markers",name=seg,marker=dict(size=5,color=PAL[i%len(PAL)],opacity=.5),
                hovertemplate=f"{seg}<br>CLV 90 ngày: %{{y:,.0f}}<extra></extra>"))
        lay(fig,340); fig.update_yaxes(tickformat="~s",title="CLV 90 ngày dự kiến (VNĐ)"); fig.update_xaxes(tickangle=-25,title="Phân khúc RFM")
        fig.update_layout(showlegend=False)
        _cm=churn.groupby("phan_khuc_rfm")["predicted_clv_90d"].mean().sort_values(ascending=False)
        show(b,fig,churn[["ma_khach_hang","phan_khuc_rfm","churn_probability","predicted_clv_90d","tong_chi_tieu"]],"06_clv_theo_phan_khuc.csv",
            ins=(f"<b>{_cm.index[0]}</b> có CLV 90 ngày trung bình cao nhất ({vnd(_cm.iloc[0])}/khách), gấp "
                 f"<b>{(_cm.iloc[0]/_cm.iloc[-1] if _cm.iloc[-1] else 0):.1f} lần</b> nhóm {_cm.index[-1]} ({vnd(_cm.iloc[-1])}). "
                 f"Ngân sách khuyến mãi nên phân bổ theo đúng tỷ lệ này." if len(_cm)>1 else ""),
            how="Cột chấm nào có nhiều điểm nằm cao = nhóm khách sẽ còn chi nhiều. Đây là căn cứ để quyết định chi bao nhiêu tiền voucher cho mỗi nhóm: "
                "không bao giờ chi vượt quá CLV dự kiến của nhóm đó.",
            tech=f"Cách tính hiện tại: **{cmethod}**. Nếu có thư viện `lifetimes`: BG/NBD dự đoán số lần mua tiếp theo, Gamma-Gamma dự đoán giá trị mỗi lần, "
                 "chiết khấu 1%/kỳ, time=3 (90 ngày). Nếu không có: xấp xỉ = (tần suất ÷ tuổi thọ) × 90 × giá trị đơn trung bình.")
        b=card("Top 20 khách cần cứu ngay","Sắp theo xác suất rời bỏ giảm dần — kèm CLV để biết cứu ai trước",
            tip="Ưu tiên gọi/gửi voucher cho khách vừa có xác suất rời bỏ cao VỪA có CLV cao. Khách xác suất cao nhưng CLV thấp thì không đáng chi nhiều.")
        tb=churn.sort_values("churn_probability",ascending=False).head(20)[["ma_khach_hang","phan_khuc_rfm","churn_probability","predicted_clv_90d","tong_chi_tieu"]].copy()
        tb["churn_probability"]=(tb["churn_probability"]*100).round(0).astype(int).astype(str)+"%"; tb["predicted_clv_90d"]=tb["predicted_clv_90d"].map(vnd); tb["tong_chi_tieu"]=tb["tong_chi_tieu"].map(vnd)
        tb.columns=["Mã KH","Phân khúc","Xác suất rời bỏ","CLV 90 ngày","Tổng đã chi"]; b.dataframe(tb,width="stretch",hide_index=True)
        _risk=churn[(churn["churn_probability"]>=.7)]
        b.markdown(f"<div class='insight'><span class='lbl'>Đọc nhanh</span>Toàn bộ nhóm nguy cơ cao (xác suất ≥ 0,7) gồm <b>{iint(len(_risk))} khách</b>, "
                   f"đang nắm <b>{vnd(_risk['tong_chi_tieu'].sum())}</b> giá trị đã chi và <b>{vnd(_risk['predicted_clv_90d'].sum())}</b> CLV 90 ngày dự kiến. "
                   f"Đây chính là số tiền có thể mất nếu không hành động.</div>", unsafe_allow_html=True)
        if SHOW_DL:
            _DL[0]+=1
            b.download_button("Tải danh sách khách nguy cơ cao (.csv)",
                _risk[["ma_khach_hang","phan_khuc_rfm","churn_probability","predicted_clv_90d","tong_chi_tieu"]].to_csv(index=False).encode("utf-8-sig"),
                "06_khach_nguy_co_cao.csv","text/csv",key=f"dl{_DL[0]}")
        st.markdown("<div class='warn'>Ghi chú: cài <code>pip install prophet lifetimes</code> để chạy đúng như tài liệu; thiếu thì tự fallback. "
                    "Nhãn churn định nghĩa từ phân khúc RFM nên AUC cao do trùng đặc trưng R/F/M.</div>", unsafe_allow_html=True)

    elif sub6==2:
        tot_c=RFM.ma_khach_hang.nunique(); tot_m=RFM["tong_chi_tieu"].sum()
        def sstat(nm):
            s=RFM[RFM.phan_khuc_rfm==nm]; return s.ma_khach_hang.nunique()/tot_c*100, s["tong_chi_tieu"].sum()/tot_m*100, s["tong_chi_tieu"].sum()
        ch_kh,ch_dt,ch_rev=sstat("Champions"); na_kh,na_dt,na_rev=sstat("Need Attention"); ar_kh,ar_dt,ar_rev=sstat("At Risk")
        anom_rate=ANOM["co_bat_thuong"].mean()*100
        loyal_n=RFM[RFM.phan_khuc_rfm.isin(["Loyal Customers","Potential Loyalists"])].ma_khach_hang.nunique()
        aov_all=RFM["gia_tri_don_hang_tb"].mean()
        winback=ar_rev*0.20; subs=loyal_n*aov_all; personalize=na_rev*0.15
        st.markdown(f"<div class='risk'>⚠️ <b>Insight kinh doanh trọng yếu:</b> doanh nghiệp phụ thuộc lớn vào nhóm Champions "
                    f"({ch_kh:.1f}% khách → {ch_dt:.1f}% doanh thu). Chiến lược nên đi theo hai hướng song song: <b>bảo vệ</b> nhóm lõi "
                    f"(VIP, cá nhân hoá) và <b>đa dạng hoá</b> nguồn doanh thu (nuôi Loyal/Potential, subscription) để giảm rủi ro tập trung.</div>", unsafe_allow_html=True)
        cards=[("💎 Champions",f"{ch_kh:.1f}% khách → {ch_dt:.1f}% doanh thu"),
               ("🌱 Need Attention",f"{na_kh:.1f}% khách nhưng chỉ {na_dt:.1f}% doanh thu"),
               ("⚠️ At Risk",f"{ar_dt:.1f}% doanh thu đang có nguy cơ rời bỏ"),
               ("🔍 Bất thường",f"~{anom_rate:.1f}% tổng giao dịch")]
        cc=st.columns(4)
        for col,(t,txt) in zip(cc,cards):
            with col:
                bb=st.container(border=True); bb.markdown(f"<div class='card-title' style='font-size:15px'>{t}</div><div style='color:{INK};font-size:13px'>{txt}</div>",unsafe_allow_html=True)
        st.markdown(f"""<div class='kpi-legend'>
          <b>Cách đọc 4 thẻ trên & bảng bên dưới</b> · Mỗi thẻ là một phát hiện rút ra từ dữ liệu thật ở 5 trang trước, không phải giả định.
          Bảng Action Plan gồm 3 cột: <b>Insight</b> (dữ liệu nói gì) → <b>Hành động</b> (làm gì) → <b>Ước tính lợi ích</b> (được gì).
          Con số lợi ích tính bằng cách nhân giá trị nhóm khách với một tỷ lệ chuyển đổi thận trọng (15–20%), dùng để <i>xếp thứ tự ưu tiên</i> —
          không phải cam kết doanh thu.
        </div>""", unsafe_allow_html=True)
        b=card("Bảng Action Plan — Insight → Hành động → Ước tính lợi ích","Sáu việc nên làm, xếp theo mức tác động — đọc từ trên xuống",
            tip="Ba cột: dữ liệu phát hiện gì → nên làm gì → kỳ vọng thu được bao nhiêu. Ưu tiên làm 2–3 dòng đầu trước.")
        rows=[
            (f"Champions {ch_kh:.1f}% khách tạo {ch_dt:.1f}% DT","VIP Membership + quà tri ân độc quyền, early-access sản phẩm mới",f"Bảo vệ ~{vnd(ch_rev)} giá trị khách trọn đời (giảm rủi ro mất doanh thu lõi)"),
            (f"Need Attention {na_kh:.1f}% khách, chỉ {na_dt:.1f}% DT","Routine cá nhân hoá theo loại da/độ tuổi; email nhắc tái mua",f"Nâng ~15% nhóm này ≈ {vnd(personalize)} doanh thu tăng thêm"),
            (f"At Risk giữ {ar_dt:.1f}% DT, nguy cơ rời","Win-back: voucher cá nhân hoá theo churn_probability trong 7–14 ngày",f"Thu hồi ~20% ≈ {vnd(winback)} doanh thu cứu lại"),
            ("Skincare dùng lặp lại theo chu kỳ sản phẩm","Subscription Box (serum 1–2 tháng, kem 2–3 tháng)",f"+1 đơn/khách Loyal ≈ {vnd(subs)} doanh thu/chu kỳ"),
            (f"Giao dịch bất thường ~{anom_rate:.1f}%","Quy trình rà soát định kỳ đơn co_bat_thuong = 1 (reseller/fraud)","Giảm thất thoát & rủi ro gian lận"),
            ("Dự báo cho thấy xu hướng doanh thu kỳ tới","Điều chỉnh marketing & tồn kho theo dự báo","Tối ưu chi phí tồn kho, tránh hết/ứ hàng"),
        ]
        _ap=pd.DataFrame(rows,columns=["Insight (từ dữ liệu)","Hành động đề xuất","Ước tính lợi ích (tiềm năng)"])
        _ap.insert(0,"Ưu tiên",[f"#{i+1}" for i in range(len(_ap))])
        b.dataframe(_ap,width="stretch",hide_index=True)
        b.caption("Lưu ý: các con số lợi ích là ước tính minh hoạ dựa trên giá trị khách trong dữ liệu, dùng để so sánh mức ưu tiên — không phải cam kết tài chính.")
        b.markdown(f"<div class='insight'><span class='lbl'>Đọc nhanh</span>Nếu làm được cả 3 việc đầu tiên, tổng giá trị tác động ước tính khoảng "
                   f"<b>{vnd(winback+personalize+subs)}</b> — trong đó riêng win-back nhóm At Risk đã là <b>{vnd(winback)}</b> và là việc "
                   f"dễ triển khai nhất vì đã có sẵn danh sách khách kèm xác suất rời bỏ ở tab “Churn &amp; CLV”.</div>", unsafe_allow_html=True)
        if EXPLAIN:
            with b.expander("Cách các con số lợi ích được tính ra"):
                st.markdown(f"""
- **Win-back At Risk ≈ {vnd(winback)}** = tổng chi tiêu nhóm At Risk ({vnd(ar_rev)}) × 20% tỷ lệ kéo lại được.
- **Cá nhân hoá Need Attention ≈ {vnd(personalize)}** = tổng chi tiêu nhóm Need Attention ({vnd(na_rev)}) × 15% mức tăng kỳ vọng.
- **Subscription Box ≈ {vnd(subs)}** = số khách Loyal + Potential ({iint(loyal_n)}) × giá trị đơn trung bình ({vnd(aov_all)}), tương ứng mỗi khách mua thêm 1 đơn/chu kỳ.
- **Bảo vệ Champions ≈ {vnd(ch_rev)}** không phải doanh thu tăng thêm mà là giá trị đang có, sẽ mất nếu nhóm này rời bỏ.

Các tỷ lệ 15–20% là mức thận trọng thường thấy của chiến dịch email/voucher trong ngành TMĐT; thay đổi tỷ lệ này sẽ thay đổi con số nhưng **không đổi thứ tự ưu tiên**.""")
        if SHOW_DL:
            _DL[0]+=1
            b.download_button("Tải bảng Action Plan (.csv)",_ap.to_csv(index=False).encode("utf-8-sig"),
                "06_action_plan.csv","text/csv",key=f"dl{_DL[0]}")

st.markdown(f"<div style='color:{MUTED};font-size:12px;margin-top:20px;border-top:1px solid {LINE};padding-top:12px'>"
            "SKINCARE ANALYTICS · 6 Dashboard · DW_SCHEMA_VI · Streamlit + Plotly + scikit-learn · Soft Feminine + Luxury</div>", unsafe_allow_html=True)
