import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="Pipe DO — Dixionline", page_icon="🎯", layout="wide")

# ── Règles métier ────────────────────────────────────────────────────────────
OFFRES = {
    "Site Vitrine Standard":       {"prix": 2500, "fms": 290,  "cat": "Sites"},
    "Site Vitrine Premium":        {"prix": 3240, "fms": 390,  "cat": "Sites"},
    "Site E-Commerce":             {"prix": 4500, "fms": 490,  "cat": "Sites"},
    "Google Ads (Accompagnement)": {"prix": 1500, "fms": 0,    "cat": "Digital"},
    "Pack Local (Vitrine + Ads)":  {"prix": 3500, "fms": 290,  "cat": "Packs"},
    "Logo simple":                 {"prix": 560,  "fms": 0,    "cat": "Image"},
    "Identité visuelle complète":  {"prix": 1700, "fms": 0,    "cat": "Image"},
    "Optimisation fiche GMB":      {"prix": 250,  "fms": 0,    "cat": "Digital"},
    "SEO — lot de 4 articles":     {"prix": 740,  "fms": 0,    "cat": "Digital"},
    "Crédit temps 5h":             {"prix": 325,  "fms": 0,    "cat": "Service"},
}

TYPE_CONTACT = ["Prospect", "Client"]
STATUTS      = ["Premier contact", "Devis présenté", "Relance", "Gagné", "Perdu"]
PROBA        = {"Chaud": 0.80, "Tiède": 0.40, "Froid": 0.10}
COULEURS     = {"Chaud": "red", "Tiède": "orange", "Froid": "blue"}

VILLES = {
    # ── Hérault (34) ────────────────────────────────────────────────────────
    "Montpellier": [43.6108, 3.8767], "Béziers": [43.3444, 3.2158],
    "Sète": [43.4027, 3.6958], "Agde": [43.3108, 3.4752],
    "Lunel": [43.6745, 4.1353], "Frontignan": [43.4472, 3.7558],
    "Pézenas": [43.4614, 3.4236], "Clermont-l'Hérault": [43.6290, 3.4355],
    "Mauguio": [43.6167, 4.0046], "Lattes": [43.5667, 3.8978],
    "Palavas-les-Flots": [43.5274, 3.9278], "Lodève": [43.7318, 3.3196],
    "Balaruc-les-Bains": [43.4556, 3.6788], "Gigean": [43.4871, 3.7118],
    "Marseillan": [43.3654, 3.5375], "Ganges": [43.9339, 3.7077],
    # ── Gard (30) ───────────────────────────────────────────────────────────
    "Nîmes": [43.8367, 4.3601], "Alès": [44.1258, 4.0822],
    "Uzès": [44.0122, 4.4191], "Beaucaire": [43.8050, 4.6442],
    "Bagnols-sur-Cèze": [44.1614, 4.6193], "Vauvert": [43.6933, 4.2750],
    "Saint-Gilles": [43.6771, 4.4313], "Anduze": [44.0511, 3.9856],
    "Le Grau-du-Roi": [43.5367, 4.1372], "Pont-Saint-Esprit": [44.2556, 4.6500],
    "La Grande-Motte": [43.5612, 4.0837], "Sommières": [43.7831, 4.0901],
    # ── Aude (11) ───────────────────────────────────────────────────────────
    "Carcassonne": [43.2130, 2.3491], "Narbonne": [43.1848, 3.0042],
    "Castelnaudary": [43.3183, 1.9536], "Limoux": [43.0575, 2.2197],
    "Lézignan-Corbières": [43.2010, 2.7591], "Port-la-Nouvelle": [43.0178, 3.0536],
    "Quillan": [42.8742, 2.1800], "Leucate": [42.9139, 3.0291],
    "Sigean": [43.0767, 2.9750],
    # ── Bouches-du-Rhône (13) ───────────────────────────────────────────────
    "Marseille": [43.2965, 5.3698], "Aix-en-Provence": [43.5298, 5.4474],
    "Arles": [43.6767, 4.6278], "Salon-de-Provence": [43.6400, 5.0972],
    "Aubagne": [43.2947, 5.5664], "Istres": [43.5139, 4.9872],
    "Martigues": [43.4047, 5.0517], "La Ciotat": [43.1742, 5.6075],
    "Cassis": [43.2146, 5.5375], "Vitrolles": [43.4611, 5.2486],
    "Miramas": [43.5847, 5.0003], "Fos-sur-Mer": [43.4375, 4.9472],
    "Port-de-Bouc": [43.4022, 4.9847], "Gardanne": [43.4558, 5.4703],
    "Saintes-Maries-de-la-Mer": [43.4519, 4.4284],
    # ── Vaucluse (84) ───────────────────────────────────────────────────────
    "Avignon": [43.9493, 4.8055], "Carpentras": [44.0556, 5.0483],
    "Apt": [43.8764, 5.3961], "Orange": [44.1361, 4.8086],
    "Cavaillon": [43.8347, 5.0378], "L'Isle-sur-la-Sorgue": [43.9183, 5.0492],
    "Pertuis": [43.6950, 5.5028], "Vaison-la-Romaine": [44.2428, 5.0703],
    "Bollène": [44.2819, 4.7472], "Sorgues": [44.0058, 4.8719],
    "Pernes-les-Fontaines": [43.9983, 5.0597],
    # ── Autres grandes villes FR ─────────────────────────────────────────────
    "Paris": [48.8566, 2.3522], "Lyon": [45.7640, 4.8357],
    "Toulouse": [43.6047, 1.4442], "Nice": [43.7102, 7.2620],
    "Bordeaux": [44.8378, -0.5792], "Strasbourg": [48.5734, 7.7521],
    "Grenoble": [45.1885, 5.7245], "Toulon": [43.1242, 5.9280],
    "Perpignan": [42.6887, 2.8948], "Valence": [44.9334, 4.8924],
    "Montélimar": [44.5578, 4.7514], "Albi": [43.9296, 2.1481],
    "Cannes": [43.5528, 7.0174], "Antibes": [43.5808, 7.1278],
}

# ── Colonnes CSV (fallback local) ────────────────────────────────────────────
COLUMNS = [
    "id", "client", "ville", "type_contact", "offre", "statut", "temperature",
    "montant_brut", "fms_inclus", "fms_montant", "montant_total",
    "probabilite", "montant_pondere", "date_creation",
]
DATA_FILE = os.path.join(os.path.dirname(__file__), "pipe_do.csv")

# ── Connexion Supabase (optionnelle) ─────────────────────────────────────────
@st.cache_resource
def get_supabase():
    try:
        from supabase import create_client
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        return None

supabase = get_supabase()
USE_SUPABASE = supabase is not None

# ── Persistance ───────────────────────────────────────────────────────────────
def load_data():
    if USE_SUPABASE:
        resp = supabase.table("pipe_do").select("*").order("id").execute()
        if resp.data:
            df = pd.DataFrame(resp.data)
            df = df.drop(columns=["created_at"], errors="ignore")
            return df
        return pd.DataFrame(columns=COLUMNS)
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        for col in ["type_contact", "fms_inclus", "fms_montant", "montant_total"]:
            if col not in df.columns:
                df[col] = {"type_contact": "Prospect", "fms_inclus": True,
                            "fms_montant": 0, "montant_total": df.get("montant_brut", 0)}.get(col)
        return df
    return pd.DataFrame(columns=COLUMNS)


def insert_row(row: dict):
    if USE_SUPABASE:
        payload = {k: v for k, v in row.items() if k != "id"}
        supabase.table("pipe_do").insert(payload).execute()
    else:
        df = load_data()
        row["id"] = int(df["id"].max() + 1) if not df.empty else 1
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)


def delete_row(row_id: int):
    if USE_SUPABASE:
        supabase.table("pipe_do").delete().eq("id", row_id).execute()
    else:
        df = load_data()
        df = df[df["id"] != row_id]
        df.to_csv(DATA_FILE, index=False)


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_eur(val):
    try:
        return f"{int(float(val)):,} €".replace(",", " ")
    except Exception:
        return "— €"

def get_coords(ville):
    for k, v in VILLES.items():
        if k.lower() == ville.strip().lower():
            return v
    return None


# ── Chargement ────────────────────────────────────────────────────────────────
df = load_data()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
.fms-badge { background:#1a6b3c; color:white; padding:1px 7px;
             border-radius:4px; font-size:0.75em; margin-left:6px; }
.fms-off   { background:#7a2020; color:white; padding:1px 7px;
             border-radius:4px; font-size:0.75em; margin-left:6px; }
</style>
""", unsafe_allow_html=True)

# ── En-tête ───────────────────────────────────────────────────────────────────
col_title, col_mode = st.columns([4, 1])
with col_title:
    st.markdown("## 🎯 Pipe Commercial — Dixionline")
with col_mode:
    if USE_SUPABASE:
        st.success("☁️ Cloud · Supabase", icon=None)
    else:
        st.warning("💾 Local · CSV")

# ── KPIs ──────────────────────────────────────────────────────────────────────
pipe_pondere    = df["montant_pondere"].sum()  if not df.empty else 0
premier_contact = len(df[df["statut"] == "Premier contact"]) if not df.empty else 0
chaud_montant   = df[df["temperature"] == "Chaud"]["montant_total"].sum() if not df.empty else 0

k1, k2, k3 = st.columns(3)
k1.metric("💰 Pipe pondéré total",           fmt_eur(pipe_pondere))
k2.metric("📋 Dossiers Premier contact",     premier_contact)
k3.metric("🔥 Montant opportunités Chaudes", fmt_eur(chaud_montant))

st.divider()

# ── Layout : Formulaire | Carte ───────────────────────────────────────────────
col_form, col_map = st.columns([1, 2])

with col_form:
    st.subheader("Nouvelle opportunité")
    with st.form("form_opp", clear_on_submit=True):
        client       = st.text_input("Nom du Client")
        ville        = st.text_input("Ville")
        type_contact = st.selectbox("Type", TYPE_CONTACT)
        offre        = st.selectbox("Proposition de Valeur", list(OFFRES.keys()))
        statut       = st.selectbox("Statut", STATUTS)
        temperature  = st.selectbox("Température", list(PROBA.keys()))

        # FMS — uniquement si l'offre a des frais de dossier
        fms_ref = OFFRES[offre]["fms"]
        if fms_ref > 0:
            fms_inclus = st.checkbox(
                f"Inclure FMS ({fmt_eur(fms_ref)})",
                value=True,
                help="Décocher = geste commercial, FMS offerts au client"
            )
        else:
            fms_inclus = False

        submitted = st.form_submit_button("Ajouter", type="primary", use_container_width=True)

    if submitted:
        if not client.strip() or not ville.strip():
            st.error("Merci de renseigner le client et la ville.")
        else:
            brut        = OFFRES[offre]["prix"]
            fms_montant = OFFRES[offre]["fms"] if fms_inclus else 0
            total       = brut + fms_montant
            proba       = PROBA[temperature]
            pondere     = total * proba

            row = {
                "client": client.strip(), "ville": ville.strip(),
                "type_contact": type_contact, "offre": offre,
                "statut": statut, "temperature": temperature,
                "montant_brut": brut, "fms_inclus": fms_inclus,
                "fms_montant": fms_montant, "montant_total": total,
                "probabilite": int(proba * 100), "montant_pondere": round(pondere, 2),
                "date_creation": datetime.today().strftime("%Y-%m-%d"),
            }
            insert_row(row)
            gc_label = " *(FMS offerts 🤝)*" if not fms_inclus and fms_ref > 0 else ""
            st.success(
                f"✅ Ajouté — {fmt_eur(brut)} + {fmt_eur(fms_montant)} FMS "
                f"= **{fmt_eur(total)}** → {fmt_eur(pondere)} pondéré{gc_label}"
            )
            st.rerun()

    st.markdown("""
**Légende carte**
🔴 Chaud (80 %)  &nbsp;|&nbsp; 🟠 Tiède (40 %)  &nbsp;|&nbsp; 🔵 Froid (10 %)
""")

with col_map:
    st.subheader("Carte des opportunités")
    m = folium.Map(location=[43.65, 4.20], zoom_start=8, tiles="CartoDB positron")

    if not df.empty:
        not_found = []
        for _, row in df.iterrows():
            coords = get_coords(row["ville"])
            if coords:
                couleur   = COULEURS.get(row["temperature"], "gray")
                tc        = row.get("type_contact", "Prospect")
                fms_ok    = row.get("fms_inclus", True)
                fms_m     = row.get("fms_montant", 0)
                total_val = row.get("montant_total", row["montant_brut"])
                fms_html  = (
                    f"<span class='fms-badge'>FMS {fmt_eur(fms_m)}</span>"
                    if fms_ok and float(fms_m) > 0
                    else ("<span class='fms-off'>FMS offerts</span>"
                          if float(row.get("fms_montant", 0)) == 0 and
                             OFFRES.get(row["offre"], {}).get("fms", 0) > 0
                          else "")
                )
                popup_html = (
                    f"<b>{row['client']}</b> "
                    f"<span style='background:#333;padding:1px 5px;"
                    f"border-radius:3px;font-size:0.8em'>{tc}</span><br>"
                    f"{row['ville']} · {row['offre']}<br>"
                    f"{fmt_eur(row['montant_brut'])} + FMS {fmt_eur(fms_m)} "
                    f"= <b>{fmt_eur(total_val)}</b><br>"
                    f"→ {fmt_eur(row['montant_pondere'])} pondéré {fms_html}<br>"
                    f"<span style='color:{couleur}'>● {row['temperature']}</span>"
                    f" | {row['statut']}"
                )
                folium.CircleMarker(
                    location=coords, radius=11,
                    color="white", weight=2,
                    fill=True, fill_color=couleur, fill_opacity=0.85,
                    popup=folium.Popup(popup_html, max_width=280),
                    tooltip=f"{row['client']} — {row['ville']}",
                ).add_to(m)
            else:
                not_found.append(row["ville"])

        if not_found:
            st.caption(f"⚠️ Villes non géolocalisées : {', '.join(set(not_found))}")

    st_folium(m, width=None, height=430, use_container_width=True)

st.divider()

# ── Tableau ───────────────────────────────────────────────────────────────────
st.subheader("Tableau des opportunités")

if df.empty:
    st.info("Aucune opportunité. Utilisez le formulaire pour commencer.")
else:
    df_show = df.copy()

    # Colonne FMS lisible
    def fms_label(r):
        try:
            if float(r.get("fms_montant", 0)) > 0:
                return f"✅ {fmt_eur(r['fms_montant'])}"
            fms_ref_val = OFFRES.get(r["offre"], {}).get("fms", 0)
            if fms_ref_val > 0:
                return "🤝 Offerts"
            return "—"
        except Exception:
            return "—"

    df_show["FMS"]             = df_show.apply(fms_label, axis=1)
    df_show["montant_brut"]    = df_show["montant_brut"].apply(fmt_eur)
    df_show["montant_total"]   = df_show["montant_total"].apply(fmt_eur)
    df_show["probabilite"]     = df_show["probabilite"].apply(lambda x: f"{int(x)} %")
    df_show["montant_pondere"] = df_show["montant_pondere"].apply(fmt_eur)

    df_show = df_show.rename(columns={
        "client": "Client", "ville": "Ville", "type_contact": "Type",
        "offre": "Offre", "statut": "Statut", "temperature": "Temp.",
        "montant_brut": "Prix HT", "montant_total": "Total HT",
        "probabilite": "Proba.", "montant_pondere": "Pondéré",
        "date_creation": "Date",
    })

    cols_display = ["Client", "Ville", "Type", "Offre", "FMS",
                    "Prix HT", "Total HT", "Temp.", "Proba.", "Pondéré", "Statut", "Date"]
    st.dataframe(
        df_show[[c for c in cols_display if c in df_show.columns]],
        use_container_width=True, hide_index=True,
    )

    # ── Suppression ───────────────────────────────────────────────────────────
    st.subheader("Supprimer une opportunité")
    labels = [f"#{int(r['id'])} — {r['client']} ({r['ville']})" for _, r in df.iterrows()]
    id_map = {lbl: int(r["id"]) for lbl, (_, r) in zip(labels, df.iterrows())}
    choix  = st.selectbox("Sélectionner", ["— Choisir —"] + labels,
                          label_visibility="collapsed")
    if choix != "— Choisir —":
        if st.button("🗑️ Supprimer cette opportunité", type="secondary"):
            delete_row(id_map[choix])
            st.success("Opportunité supprimée.")
            st.rerun()
