import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="MegaElan Portalı", page_icon="🚗", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(-45deg, #1e3c72, #2a5298, #0f2027, #203a43);
        background-size: 400% 400%;
        animation: gradientBG 12s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #ffffff !important;
    }
    @keyframes hereket {
        0% { transform: scale(1); color: #00d2ff; }
        50% { transform: scale(1.03); color: #ff4b4b; }
        100% { transform: scale(1); color: #00d2ff; }
    }
    .animasiyali-basliq {
        animation: hereket 3s infinite;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }
    </style>
    <h2 class="animasiyali-basliq">✨ MegaElan - Ən Müasir Elan Platforması ✨</h2>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "elanlar_baza.csv"
ADMIN_FILE = "adminler_baza.csv"
UPLOAD_DIR = "sekiller"

if not os.path.exists(UPLOAD_DIR):
  os.makedirs(UPLOAD_DIR)


def bazani_yukle():
  if os.path.exists(DATA_FILE):
    return pd.read_csv(DATA_FILE)
  else:
    df_init = pd.DataFrame({
        "ID": [1],
        "Kateqoriya": ["Avtomobil"],
        "Basliq": ["Kia Rio, 2020"],
        "Qiymet": ["24500 AZN"],
        "Seher": ["Bakı"],
        "Melumat": ["İdeal vəziyyətdə."],
        "Sekil": [""],
    })
    df_init.to_csv(DATA_FILE, index=False)
    return df_init


def adminleri_yukle():
  if os.path.exists(ADMIN_FILE):
    return pd.read_csv(ADMIN_FILE)
  else:
    df_admin = pd.DataFrame({"IstifadeciAdi": ["admin"], "Parol": ["1234"]})
    df_admin.to_csv(ADMIN_FILE, index=False)
    return df_admin


df = bazani_yukle()
admin_df = adminleri_yukle()

if "admin_giris" not in st.session_state:
  st.session_state.admin_giris = False

menu_secimleri = ["Elanlara Bax", "Yeni Elan Yerləşdir", "Admin Girişi"]
if st.session_state.admin_giris:
  menu_secimleri = [
      "Elanlara Bax",
      "Yeni Elan Yerləşdir",
      "Admin Paneli",
      "Çıxış et",
  ]

menu = st.sidebar.selectbox("Menyu", menu_secimleri)

# 1. ELANLARA BAX
if menu == "Elanlara Bax":
  st.header("📋 Mövcud Elanlar")
  if df.empty:
    st.info("Hələ elan yoxdur.")
  else:
    for index, row in df.iterrows():
      with st.container():
        st.markdown(f"### 🚗 {row['Basliq']}")
        if (
            "Sekil" in df.columns
            and pd.notna(row["Sekil"])
            and row["Sekil"] != ""
        ):
          if os.path.exists(row["Sekil"]):
            st.image(row["Sekil"], width=350)

        st.write(
            f"📁 **Kateqoriya:** {row['Kateqoriya']} | 📍 **Şəhər:**"
            f" {row['Seher']} | 💰 **Qiymət:** {row['Qiymet']}"
        )
        st.write(f"📝 {row['Melumat']}")
        st.markdown("---")

# 2. YENİ ELAN YERLƏŞDİR (Şəkil yükləmə ilə)
elif menu == "Yeni Elan Yerləşdir":
  st.header("➕ Yeni Elan Yerləşdir (Turbo/Tap üslubu)")
  with st.form("elan_formu"):
    kategoriya = st.selectbox(
        "Kateqoriya", ["Avtomobil", "Daşınmaz Əmlak", "Elektronika"]
    )
    basliq = st.text_input("Başlıq")
    qiymet = st.text_input("Qiymət")
    seher = st.text_input("Şəhər")
    melumat = st.text_area("Məlumat / Təsvir")

    yuklenen_sekil = st.file_uploader