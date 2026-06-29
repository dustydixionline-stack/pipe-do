import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
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
    "Jacou": [43.6623, 3.9241], "Poulx": [43.8806, 4.3778], "Codognan": [43.7167, 4.2333],
    "Bouc-Bel-Air": [43.4542, 5.4161], "Lunel-Viel": [43.6667, 4.1333],
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
    "date_dernier_echange",
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
        payload = {k: v for k, v in row.items() if k != "id" and v is not None}
        supabase.table("pipe_do").insert(payload).execute()
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


def update_row(row_id: int, data: dict):
    if USE_SUPA:
        supabase.table("pipe_do").update(data).eq("id", row_id).execute()
    else:
        df = load_data()
        for k, v in data.items():
            df.loc[df["id"] == row_id, k] = v
        df.to_csv(DATA_FILE, index=False)


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_eur(val):
    try:
        return f"{int(float(val)):,} €".replace(",", " ")
    except Exception:
        return "— €"


# ── Graphique répartition par offre ──────────────────────────────────────────
CAT_COLORS = {
    "Sites":   "#534AB7",
    "Digital": "#1D9E75",
    "Packs":   "#BA7517",
    "Image":   "#D4537E",
    "Service": "#888780",
    "Autre":   "#888780",
}

def make_offre_chart(df):
    if df.empty:
        return None
    totals = df.groupby("offre")["montant_total"].sum().reset_index()
    totals = totals.sort_values("montant_total", ascending=True)
    total_global = totals["montant_total"].sum()

    def cat_color(offre_name):
        cat = OFFRES.get(offre_name, {}).get("cat", "Autre")
        return CAT_COLORS.get(cat, "#888780")

    colors = [cat_color(o) for o in totals["offre"]]
    pcts   = [f"{int(v / total_global * 100)}%" if total_global > 0 else "0%"
              for v in totals["montant_total"]]

    fig = go.Figure(go.Bar(
        x=totals["montant_total"],
        y=totals["offre"],
        orientation="h",
        marker_color=colors,
        marker_line_width=0,
        text=pcts,
        textposition="inside",
        textfont=dict(color="white", size=11),
        hovertemplate="%{y}<br><b>%{x:,.0f} €</b><extra></extra>",
    ))
    fig.update_layout(
        margin=dict(l=0, r=60, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380,
        xaxis=dict(
            showgrid=True, gridcolor="rgba(128,128,128,0.12)",
            tickformat=",", ticksuffix=" €", title=None,
            tickfont=dict(size=11),
        ),
        yaxis=dict(showgrid=False, title=None, tickfont=dict(size=12)),
        showlegend=False,
        font=dict(family="system-ui, sans-serif"),
        bargap=0.25,
    )
    return fig


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

    # Date dernier échange
    date_echange = st.date_input("Date du dernier échange", value=None,
                                  key="f_date_echange",
                                  help="Laisser vide si pas encore d'échange")

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
                "commercial":           assigned_to,
                "date_creation":        datetime.today().strftime("%Y-%m-%d"),
                "date_dernier_echange": date_echange.strftime("%Y-%m-%d") if date_echange else None,
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

with col_map:
    st.subheader("Répartition par offre")
    fig = make_offre_chart(df)
    if fig:
        cat_legend = [
            ("Sites", "#534AB7"), ("Digital", "#1D9E75"),
            ("Packs", "#BA7517"), ("Image", "#D4537E"), ("Service / Autre", "#888780"),
        ]
        legend_html = " &nbsp; ".join(
            f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:11px;color:#888">'
            f'<span style="width:9px;height:9px;border-radius:2px;background:{c};display:inline-block"></span>{lbl}</span>'
            for lbl, c in cat_legend
        )
        st.markdown(legend_html, unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Aucune opportunité pour afficher le graphique.")

st.divider()

# ── Pipeline + Tableau ────────────────────────────────────────────────────────
scope_title = "Vue équipe" if is_admin else user["display_name"]
st.subheader(f"Opportunités — {scope_title}")

tab_pipe, tab_table = st.tabs(["📋  Pipeline", "📊  Tableau"])

# ── Onglet Kanban ─────────────────────────────────────────────────────────────
LEGENDE_TEMP = (
    '<div style="font-size:12px;color:#888;margin-bottom:10px">'
    '🔴&nbsp;&nbsp;🟠&nbsp;&nbsp;🔵'
    '</div>'
)

with tab_pipe:
    st.markdown(LEGENDE_TEMP, unsafe_allow_html=True)
    KANBAN_STATUTS = ["Premier contact", "Devis présenté", "Relance", "Gagné", "Perdu"]
    KANBAN_STYLE = {
        "Premier contact": {"bg": "#E6F1FB", "color": "#0C447C",  "icon": "📞"},
        "Devis présenté":  {"bg": "#EEEDFE", "color": "#3C3489",  "icon": "📄"},
        "Relance":         {"bg": "#FAEEDA", "color": "#633806",  "icon": "🔔"},
        "Gagné":           {"bg": "#EAF3DE", "color": "#27500A",  "icon": "✅"},
        "Perdu":           {"bg": "#FCEBEB", "color": "#791F1F",  "icon": "❌"},
    }
    TEMP_BADGE = {
        "Chaud": ("#FAECE7", "#993C1D"),
        "Tiède": ("#FAEEDA", "#854F0B"),
        "Froid": ("#E6F1FB", "#185FA5"),
    }
    TRANSITIONS = {
        "Premier contact": [("→ Devis",   "Devis présenté")],
        "Devis présenté":  [("→ Relance", "Relance"), ("✅ Gagné", "Gagné")],
        "Relance":         [("✅ Gagné",   "Gagné"),  ("❌ Perdu", "Perdu")],
        "Gagné":           [("↩ Relance", "Relance")],
        "Perdu":           [("↩ Relance", "Relance")],
    }

    cols_kb = st.columns(5)
    for col_kb, statut in zip(cols_kb, KANBAN_STATUTS):
        s      = KANBAN_STYLE[statut]
        df_col = df[df["statut"] == statut] if not df.empty else pd.DataFrame()
        count  = len(df_col)
        with col_kb:
            st.markdown(
                f'<div style="background:{s["bg"]};color:{s["color"]};font-size:12px;font-weight:500;'
                f'padding:6px 8px;border-radius:8px;text-align:center;margin-bottom:8px">'
                f'{s["icon"]} {statut} <span style="opacity:.6">({count})</span></div>',
                unsafe_allow_html=True,
            )
            if df_col.empty:
                st.markdown(
                    '<div style="font-size:11px;color:#999;text-align:center;padding:14px 0">—</div>',
                    unsafe_allow_html=True,
                )
            else:
                for _, row in df_col.iterrows():
                    temp          = row.get("temperature", "Froid")
                    bg_t, color_t = TEMP_BADGE.get(temp, ("#f0f0f0", "#555"))
                    co            = row.get("commercial", "—")
                    row_id        = int(row["id"])
                    st.markdown(
                        f'<div style="background:white;border:0.5px solid #e0e0e0;'
                        f'border-radius:10px 10px 0 0;padding:10px 11px 8px 11px">'
                        f'<div style="font-size:13px;font-weight:500;color:#111;margin-bottom:3px">{row["client"]}</div>'
                        f'<div style="font-size:10px;color:#666;margin-bottom:6px">{row["offre"]}</div>'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">'
                        f'<span style="font-size:12px;font-weight:500;color:#111">{fmt_eur(row["montant_total"])}</span>'
                        f'<span style="font-size:10px;padding:2px 6px;border-radius:20px;'
                        f'background:{bg_t};color:{color_t}">{temp}</span>'
                        f'</div>'
                        f'<div style="font-size:10px;color:#999">👤 {co} · {row["ville"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    transitions = TRANSITIONS.get(statut, [])
                    if transitions:
                        btn_cols = st.columns(len(transitions))
                        for bcol, (label, new_statut) in zip(btn_cols, transitions):
                            if bcol.button(label, key=f"kb_{row_id}_{new_statut}",
                                           use_container_width=True):
                                update_row(row_id, {"statut": new_statut})
                                st.rerun()
                    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

# ── Onglet Tableau ────────────────────────────────────────────────────────────
with tab_table:
    st.markdown(LEGENDE_TEMP, unsafe_allow_html=True)
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

        TEMP_EMOJI = {"Chaud": "🔴", "Tiède": "🟠", "Froid": "🔵"}
        df_show["FMS"]             = df_show.apply(fms_label, axis=1)
        df_show["temperature"]     = df_show["temperature"].map(TEMP_EMOJI).fillna("⚪")
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

        df_show = df_show.rename(columns={"date_dernier_echange": "Dernier échange"})
        base_cols  = ["Client", "Ville", "Type", "Offre", "FMS", "Prix HT", "Total HT",
                      "Temp.", "Proba.", "Pondéré", "Statut", "Date", "Dernier échange"]
        show_cols  = (["Commercial"] + base_cols) if is_admin else base_cols
        final_cols = [c for c in show_cols if c in df_show.columns]
        st.dataframe(df_show[final_cols], use_container_width=True, hide_index=True)

        # ── Modifier ─────────────────────────────────────────────────────────
        st.subheader("Modifier une opportunité")

        edit_labels = [
            f"#{int(r['id'])} — {r['client']} ({r['ville']})"
            for _, r in df.iterrows()
        ]
        edit_choice = st.selectbox(
            "Sélectionner", ["— Choisir —"] + edit_labels,
            key="edit_select", label_visibility="collapsed"
        )

        if edit_choice != "— Choisir —":
            idx     = edit_labels.index(edit_choice)
            erow    = df.iloc[idx]
            erow_id = int(erow["id"])
            kp      = f"ed_{erow_id}"   # préfixe clé unique par ligne

            offre_options = list(OFFRES.keys())
            stored_offre  = erow["offre"]
            default_idx   = offre_options.index(stored_offre) if stored_offre in offre_options else offre_options.index(OFFRE_CUSTOM)

            ec1, ec2 = st.columns(2)
            e_client = ec1.text_input("Client", value=erow["client"], key=f"{kp}_client")
            e_ville  = ec2.text_input("Ville",  value=erow["ville"],  key=f"{kp}_ville")

            ec3, ec4 = st.columns(2)
            e_type = ec3.selectbox("Type", TYPE_CONTACT, key=f"{kp}_type",
                index=TYPE_CONTACT.index(erow["type_contact"]) if erow["type_contact"] in TYPE_CONTACT else 0)
            e_statut = ec4.selectbox("Statut", STATUTS, key=f"{kp}_statut",
                index=STATUTS.index(erow["statut"]) if erow["statut"] in STATUTS else 0)

            e_offre = st.selectbox("Proposition de valeur", offre_options,
                                   index=default_idx, key=f"{kp}_offre")

            if e_offre == OFFRE_CUSTOM:
                default_nom  = stored_offre if stored_offre not in OFFRES else ""
                default_prix = int(float(erow["montant_brut"])) if stored_offre not in OFFRES else 0
                e_custom_nom = st.text_input("Intitulé de la prestation", value=default_nom, key=f"{kp}_custom_nom")
                e_brut       = st.number_input("Montant HT (€)", min_value=0, step=50,
                                               value=default_prix, key=f"{kp}_brut")
                e_fms        = False
                fms_ref_val  = 0
            else:
                e_custom_nom = ""
                e_brut       = OFFRES[e_offre]["prix"]
                fms_ref_val  = OFFRES[e_offre]["fms"]
                e_fms        = st.checkbox(f"Inclure FMS ({fmt_eur(fms_ref_val)})",
                                           value=bool(erow.get("fms_inclus", False)),
                                           key=f"{kp}_fms") if fms_ref_val > 0 else False

            temp_list = list(PROBA.keys())
            e_temp = st.selectbox("Température", temp_list, key=f"{kp}_temp",
                index=temp_list.index(erow["temperature"]) if erow["temperature"] in temp_list else 0)

            if is_admin:
                users_map_e = get_users()
                noms_co_e   = [u["display_name"] for u in users_map_e.values()]
                co_idx      = noms_co_e.index(erow["commercial"]) if erow["commercial"] in noms_co_e else 0
                e_co        = st.selectbox("Commercial", noms_co_e, index=co_idx, key=f"{kp}_co")
            else:
                e_co = user["display_name"]

            existing_date = erow.get("date_dernier_echange")
            try:
                from datetime import date as _date
                pre_date = _date.fromisoformat(str(existing_date)) if existing_date and str(existing_date) != "nan" else None
            except Exception:
                pre_date = None
            e_date_echange = st.date_input("Date du dernier échange", value=pre_date,
                                            key=f"{kp}_date_echange",
                                            help="Laisser vide si pas encore d'échange")

            if st.button("💾 Enregistrer les modifications", type="primary",
                         use_container_width=True, key=f"{kp}_save"):
                try:
                    if e_offre == OFFRE_CUSTOM:
                        offre_label = e_custom_nom.strip() or OFFRE_CUSTOM
                        brut        = float(e_brut)
                        fms_ref_val = 0
                        e_fms       = False
                    else:
                        offre_label = e_offre
                        brut        = float(OFFRES[e_offre]["prix"])
                        fms_ref_val = OFFRES[e_offre]["fms"]
                    fms_montant = fms_ref_val if (e_fms and e_offre != OFFRE_CUSTOM) else 0
                    total       = brut + fms_montant
                    proba       = PROBA[e_temp]
                    pondere     = round(total * proba, 2)

                    update_row(erow_id, {
                        "client":               e_client.strip(),
                        "ville":                e_ville.strip(),
                        "type_contact":         e_type,
                        "offre":                offre_label,
                        "statut":               e_statut,
                        "temperature":          e_temp,
                        "montant_brut":         brut,
                        "fms_inclus":           e_fms,
                        "fms_montant":          fms_montant,
                        "montant_total":        total,
                        "probabilite":          int(proba * 100),
                        "montant_pondere":      pondere,
                        "commercial":           e_co,
                        "date_dernier_echange": e_date_echange.strftime("%Y-%m-%d") if e_date_echange else None,
                    })
                    st.success("✅ Modifications enregistrées !")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Erreur : {ex}")

        st.divider()

        # ── Supprimer ─────────────────────────────────────────────────────────
        st.subheader("Supprimer une opportunité")

        if is_admin:
            deletable = df
        else:
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
