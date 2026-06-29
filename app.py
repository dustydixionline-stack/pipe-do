import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="Pipe DO — Dixionline", page_icon="🎯", layout="wide")

# ── Constantes métier ─────────────────────────────────────────────────────────
OFFRE_CUSTOM = "✏️ Prestation hors catalogue"

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
    OFFRE_CUSTOM:                  {"prix": 0,    "fms": 0,    "cat": "Autre"},
}

TYPE_CONTACT = ["Prospect", "Client"]
STATUTS      = ["Premier contact", "Devis présenté", "Relance", "Gagné", "Perdu"]
PROBA        = {"Chaud": 0.80, "Tiède": 0.40, "Froid": 0.10}
COULEURS     = {"Chaud": "red", "Tiède": "orange", "Froid": "blue"}

VILLES = {
    "Montpellier": [43.6108, 3.8767], "Béziers": [43.3444, 3.2158],
    "Sète": [43.4027, 3.6958], "Agde": [43.3108, 3.4752],
    "Lunel": [43.6745, 4.1353], "Frontignan": [43.4472, 3.7558],
    "Pézenas": [43.4614, 3.4236], "Clermont-l'Hérault": [43.6290, 3.4355],
    "Mauguio": [43.6167, 4.0046], "Lattes": [43.5667, 3.8978],
    "Palavas-les-Flots": [43.5274, 3.9278], "Lodève": [43.7318, 3.3196],
    "Balaruc-les-Bains": [43.4556, 3.6788], "Marseillan": [43.3654, 3.5375],
    "Ganges": [43.9339, 3.7077],
    "Nîmes": [43.8367, 4.3601], "Alès": [44.1258, 4.0822],
    "Uzès": [44.0122, 4.4191], "Beaucaire": [43.8050, 4.6442],
    "Bagnols-sur-Cèze": [44.1614, 4.6193], "Vauvert": [43.6933, 4.2750],
    "Saint-Gilles": [43.6771, 4.4313], "Anduze": [44.0511, 3.9856],
    "Le Grau-du-Roi": [43.5367, 4.1372], "La Grande-Motte": [43.5612, 4.0837],
    "Carcassonne": [43.2130, 2.3491], "Narbonne": [43.1848, 3.0042],
    "Castelnaudary": [43.3183, 1.9536], "Limoux": [43.0575, 2.2197],
    "Lézignan-Corbières": [43.2010, 2.7591], "Port-la-Nouvelle": [43.0178, 3.0536],
    "Marseille": [43.2965, 5.3698], "Aix-en-Provence": [43.5298, 5.4474],
    "Arles": [43.6767, 4.6278], "Salon-de-Provence": [43.6400, 5.0972],
    "Aubagne": [43.2947, 5.5664], "Istres": [43.5139, 4.9872],
    "Martigues": [43.4047, 5.0517], "La Ciotat": [43.1742, 5.6075],
    "Vitrolles": [43.4611, 5.2486], "Miramas": [43.5847, 5.0003],
    "Fos-sur-Mer": [43.4375, 4.9472], "Gardanne": [43.4558, 5.4703],
    "Avignon": [43.9493, 4.8055], "Carpentras": [44.0556, 5.0483],
    "Apt": [43.8764, 5.3961], "Orange": [44.1361, 4.8086],
    "Cavaillon": [43.8347, 5.0378], "L'Isle-sur-la-Sorgue": [43.9183, 5.0492],
    "Pertuis": [43.6950, 5.5028], "Vaison-la-Romaine": [44.2428, 5.0703],
    "Bollène": [44.2819, 4.7472], "Sorgues": [44.0058, 4.8719],
    "Paris": [48.8566, 2.3522], "Lyon": [45.7640, 4.8357],
    "Toulouse": [43.6047, 1.4442], "Nice": [43.7102, 7.2620],
    "Bordeaux": [44.8378, -0.5792], "Grenoble": [45.1885, 5.7245],
    "Toulon": [43.1242, 5.9280], "Perpignan": [42.6887, 2.8948],
    "Valence": [44.9334, 4.8924], "Cannes": [43.5528, 7.0174],
}

# ── Supabase ──────────────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        client = create_client(url, key)
        # Test de connexion rapide
        client.table("pipe_do").select("id").limit(1).execute()
        return client, None
    except KeyError as e:
        return None, f"Secret manquant : {e}"
    except Exception as e:
        return None, str(e)

_supa_result = get_supabase()
supabase  = _supa_result[0]
_supa_err = _supa_result[1]
USE_SUPA  = supabase is not None
DATA_FILE = os.path.join(os.path.dirname(__file__), "pipe_do.csv")
COLUMNS   = [
    "id", "client", "ville", "type_contact", "offre", "statut", "temperature",
    "montant_brut", "fms_inclus", "fms_montant", "montant_total",
    "probabilite", "montant_pondere", "commercial", "date_creation",
]


# ── Auth ──────────────────────────────────────────────────────────────────────
def get_users():
    try:
        return {
            "dusty.dixionline@gmail.com": {
                "password":     st.secrets.get("PASSWORD_DUSTY", "admin"),
                "role":         "admin",
                "display_name": "Dusty",
                "label":        "Dir. Commercial",
            },
            "hugo.dixionline@gmail.com": {
                "password":     st.secrets.get("PASSWORD_COMMERCIAL", "commercial"),
                "role":         "commercial",
                "display_name": "Hugo",
                "label":        "Commercial",
            },
        }
    except Exception:
        return {
            "dusty.dixionline@gmail.com": {"password": "admin",      "role": "admin",      "display_name": "Dusty", "label": "Dir. Commercial"},
            "hugo.dixionline@gmail.com":  {"password": "commercial", "role": "commercial", "display_name": "Hugo",  "label": "Commercial"},
        }


def login_page():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 🎯 Pipe Commercial\n### Dixionline")
        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("login"):
            username = st.text_input("Adresse email")
            password = st.text_input("Mot de passe", type="password")
            ok = st.form_submit_button("Connexion", type="primary", use_container_width=True)
        if ok:
            users = get_users()
            u = users.get(username.strip().lower())
            if u and u["password"] == password:
                st.session_state["user"] = {
                    "username":     username.strip().lower(),
                    "display_name": u["display_name"],
                    "role":         u["role"],
                    "label":        u["label"],
                }
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")


if "user" not in st.session_state:
    login_page()
    st.stop()

user     = st.session_state["user"]
is_admin = user["role"] == "admin"


# ── Persistance ───────────────────────────────────────────────────────────────
def load_data():
    if USE_SUPA:
        resp = supabase.table("pipe_do").select("*").order("id").execute()
        df   = pd.DataFrame(resp.data) if resp.data else pd.DataFrame(columns=COLUMNS)
        df   = df.drop(columns=["created_at"], errors="ignore")
    elif os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=COLUMNS)

    for col, default in [
        ("type_contact", "Prospect"), ("fms_inclus", True),
        ("fms_montant", 0), ("montant_total", 0), ("commercial", "—"),
    ]:
        if col not in df.columns:
            df[col] = default
    return df


def insert_row(row: dict):
    if USE_SUPA:
        supabase.table("pipe_do").insert({k: v for k, v in row.items() if k != "id"}).execute()
    else:
        df = load_data()
        row["id"] = int(df["id"].max() + 1) if not df.empty else 1
        pd.concat([df, pd.DataFrame([row])], ignore_index=True).to_csv(DATA_FILE, index=False)


def delete_row(row_id: int):
    if USE_SUPA:
        supabase.table("pipe_do").delete().eq("id", row_id).execute()
    else:
        df = load_data()
        df[df["id"] != row_id].to_csv(DATA_FILE, index=False)


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


# ── Chargement + filtre rôle ──────────────────────────────────────────────────
df_all = load_data()

if is_admin:
    df = df_all.copy()
else:
    df = df_all[df_all["commercial"] == user["display_name"]].copy() if not df_all.empty else df_all.copy()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.55rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
h1, h2 = st.columns([5, 1])
with h1:
    role_badge = "👑 Admin" if is_admin else "🧑‍💼 Commercial"
    st.markdown(f"## 🎯 Pipe Commercial — Dixionline &nbsp; `{user['display_name']}` &nbsp; {role_badge}")
with h2:
    if USE_SUPA:
        st.success("☁️ Cloud")
    else:
        st.warning("💾 Local")
        if _supa_err:
            st.caption(f"⚠️ {_supa_err}")
    if st.button("Déconnexion", use_container_width=True):
        del st.session_state["user"]
        st.rerun()

# ── KPIs ──────────────────────────────────────────────────────────────────────
pipe_pondere   = df["montant_pondere"].sum() if not df.empty else 0
ca_gagne       = df[df["statut"] == "Gagné"]["montant_total"].sum() if not df.empty else 0
a_relancer     = len(df[df["statut"] == "Relance"]) if not df.empty else 0
actifs         = len(df[~df["statut"].isin(["Gagné", "Perdu"])]) if not df.empty else 0
chaud_montant  = df[df["temperature"] == "Chaud"]["montant_total"].sum() if not df.empty else 0

scope_label = "équipe" if is_admin else user["display_name"]
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric(f"💰 Pipe pondéré ({scope_label})", fmt_eur(pipe_pondere))
k2.metric("✅ CA Gagné",                      fmt_eur(ca_gagne))
k3.metric("🔔 Dossiers à relancer",           a_relancer)
k4.metric("📂 Dossiers actifs",               actifs)
k5.metric("🔥 Opportunités Chaudes",          fmt_eur(chaud_montant))

# Vue consolidée admin : répartition par commercial
if is_admin and not df_all.empty and "commercial" in df_all.columns:
    with st.expander("📊 Vue équipe — répartition par commercial"):
        recap = (
            df_all.groupby("commercial")
            .agg(
                Dossiers=("id", "count"),
                Pipe_pondere=("montant_pondere", "sum"),
                Chaud=("temperature", lambda x: (x == "Chaud").sum()),
            )
            .reset_index()
            .rename(columns={"commercial": "Commercial", "Pipe_pondere": "Pipe pondéré", "Chaud": "Opportunités chaudes"})
        )
        recap["Pipe pondéré"] = recap["Pipe pondéré"].apply(fmt_eur)
        st.dataframe(recap, use_container_width=True, hide_index=True)

st.divider()

# ── Formulaire + Carte ────────────────────────────────────────────────────────
col_form, col_map = st.columns([1, 2])

with col_form:
    st.subheader("Nouvelle opportunité")

    # Widgets hors st.form pour permettre l'affichage conditionnel
    client       = st.text_input("Nom du Client", key="f_client")
    ville        = st.text_input("Ville", key="f_ville")
    type_contact = st.selectbox("Type", TYPE_CONTACT, key="f_type")
    offre        = st.selectbox("Proposition de Valeur", list(OFFRES.keys()), key="f_offre")

    # Champs supplémentaires si hors catalogue
    offre_custom_nom  = ""
    offre_custom_prix = 0
    if offre == OFFRE_CUSTOM:
        st.markdown("**Détail de la prestation hors catalogue**")
        offre_custom_nom  = st.text_input("Intitulé de la prestation", key="f_custom_nom",
                                           placeholder="Ex : Module réservation en ligne")
        offre_custom_prix = st.number_input("Montant HT (€)", min_value=0, step=50,
                                             key="f_custom_prix", value=0)

    statut      = st.selectbox("Statut", STATUTS, key="f_statut")
    temperature = st.selectbox("Température", list(PROBA.keys()), key="f_temp")

    # FMS (uniquement si l'offre a des frais)
    fms_ref = OFFRES[offre]["fms"] if offre != OFFRE_CUSTOM else 0
    if fms_ref > 0:
        fms_inclus = st.checkbox(f"Inclure FMS ({fmt_eur(fms_ref)})", value=True, key="f_fms",
                                  help="Décocher = FMS offerts (geste commercial)")
    else:
        fms_inclus = False

    # Admin peut choisir pour quel commercial
    if is_admin:
        users_map   = get_users()
        noms_co     = [u["display_name"] for u in users_map.values()]
        assigned_to = st.selectbox("Assigner à", noms_co, key="f_assign")
    else:
        assigned_to = user["display_name"]

    add_btn = st.button("➕ Ajouter l'opportunité", type="primary", use_container_width=True)

    if add_btn:
        errors = []
        if not client.strip():
            errors.append("Nom du client requis.")
        if not ville.strip():
            errors.append("Ville requise.")
        if offre == OFFRE_CUSTOM:
            if not offre_custom_nom.strip():
                errors.append("Intitulé de la prestation requis.")
            if offre_custom_prix <= 0:
                errors.append("Montant de la prestation requis (> 0).")

        if errors:
            for e in errors:
                st.error(e)
        else:
            if offre == OFFRE_CUSTOM:
                offre_label = offre_custom_nom.strip()
                brut        = offre_custom_prix
                fms_ref_val = 0
                fms_inclus  = False
            else:
                offre_label = offre
                brut        = OFFRES[offre]["prix"]
                fms_ref_val = OFFRES[offre]["fms"]

            fms_montant = fms_ref_val if fms_inclus else 0
            total       = brut + fms_montant
            proba       = PROBA[temperature]
            pondere     = round(total * proba, 2)

            row = {
                "client":        client.strip(),
                "ville":         ville.strip(),
                "type_contact":  type_contact,
                "offre":         offre_label,
                "statut":        statut,
                "temperature":   temperature,
                "montant_brut":  brut,
                "fms_inclus":    fms_inclus,
                "fms_montant":   fms_montant,
                "montant_total": total,
                "probabilite":   int(proba * 100),
                "montant_pondere": pondere,
                "commercial":    assigned_to,
                "date_creation": datetime.today().strftime("%Y-%m-%d"),
            }
            insert_row(row)
            gc = " *(FMS offerts 🤝)*" if not fms_inclus and fms_ref_val > 0 else ""
            st.success(
                f"✅ **{offre_label}** — {fmt_eur(brut)} + FMS {fmt_eur(fms_montant)} "
                f"= **{fmt_eur(total)}** → {fmt_eur(pondere)} pondéré{gc}"
            )
            # Nettoyage des champs
            for k in ["f_client", "f_ville", "f_custom_nom", "f_custom_prix"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    st.markdown("""
**Légende carte**
🔴 Chaud (80 %)&nbsp;|&nbsp;🟠 Tiède (40 %)&nbsp;|&nbsp;🔵 Froid (10 %)
""")

with col_map:
    st.subheader("Carte des opportunités")
    m = folium.Map(location=[43.65, 4.20], zoom_start=8, tiles="CartoDB positron")

    if not df.empty:
        not_found = []
        for _, row in df.iterrows():
            coords = get_coords(row["ville"])
            if coords:
                couleur = COULEURS.get(row["temperature"], "gray")
                fms_m   = float(row.get("fms_montant", 0))
                total_v = float(row.get("montant_total", row["montant_brut"]))
                tc      = row.get("type_contact", "Prospect")
                co      = row.get("commercial", "—")
                popup_html = (
                    f"<b>{row['client']}</b> "
                    f"<span style='background:#333;padding:1px 5px;border-radius:3px;"
                    f"font-size:0.8em'>{tc}</span><br>"
                    f"🧑 {co} · {row['ville']}<br>"
                    f"{row['offre']}<br>"
                    f"{fmt_eur(row['montant_brut'])} + FMS {fmt_eur(fms_m)} = <b>{fmt_eur(total_v)}</b><br>"
                    f"→ {fmt_eur(row['montant_pondere'])} pondéré<br>"
                    f"<span style='color:{couleur}'>● {row['temperature']}</span> | {row['statut']}"
                )
                folium.CircleMarker(
                    location=coords, radius=11,
                    color="white", weight=2,
                    fill=True, fill_color=couleur, fill_opacity=0.85,
                    popup=folium.Popup(popup_html, max_width=290),
                    tooltip=f"{row['client']} — {row['ville']} ({co})",
                ).add_to(m)
            else:
                not_found.append(row["ville"])
        if not_found:
            st.caption(f"⚠️ Villes non géolocalisées : {', '.join(set(not_found))}")

    st_folium(m, width=None, height=430, use_container_width=True)

st.divider()

# ── Tableau ───────────────────────────────────────────────────────────────────
st.subheader("Tableau des opportunités" + (" — Vue équipe" if is_admin else f" — {user['display_name']}"))

if df.empty:
    st.info("Aucune opportunité. Utilisez le formulaire pour commencer.")
else:
    df_show = df.copy()

    def fms_label(r):
        try:
            val = float(r.get("fms_montant", 0))
            if val > 0:
                return f"✅ {fmt_eur(val)}"
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
        "commercial": "Commercial", "date_creation": "Date",
    })

    base_cols  = ["Client", "Ville", "Type", "Offre", "FMS", "Prix HT", "Total HT",
                  "Temp.", "Proba.", "Pondéré", "Statut", "Date"]
    show_cols  = (["Commercial"] + base_cols) if is_admin else base_cols
    final_cols = [c for c in show_cols if c in df_show.columns]
    st.dataframe(df_show[final_cols], use_container_width=True, hide_index=True)

    # ── Suppression ──────────────────────────────────────────────────────────
    st.subheader("Supprimer une opportunité")

    if is_admin:
        deletable = df
    else:
        # Commercial ne peut supprimer que ses propres entrées
        deletable = df[df.get("commercial", pd.Series(dtype=str)) == user["display_name"]]

    if deletable.empty:
        st.caption("Aucune opportunité à supprimer.")
    else:
        labels = [
            f"#{int(r['id'])} — {r['client']} ({r['ville']}) · {r.get('commercial','')}"
            for _, r in deletable.iterrows()
        ]
        id_map = {lbl: int(r["id"]) for lbl, (_, r) in zip(labels, deletable.iterrows())}
        choix  = st.selectbox("Sélectionner", ["— Choisir —"] + labels,
                              label_visibility="collapsed")
        if choix != "— Choisir —":
            if st.button("🗑️ Supprimer cette opportunité", type="secondary"):
                delete_row(id_map[choix])
                st.success("Opportunité supprimée.")
                st.rerun()
