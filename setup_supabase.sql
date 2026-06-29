-- ─────────────────────────────────────────────────────────────────────────────
-- CRÉATION INITIALE (première installation)
-- Coller dans : Supabase → SQL Editor → New query → Run
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS pipe_do (
    id               BIGSERIAL PRIMARY KEY,
    client           TEXT          NOT NULL,
    ville            TEXT          NOT NULL,
    type_contact     TEXT          NOT NULL DEFAULT 'Prospect',
    offre            TEXT          NOT NULL,
    statut           TEXT          NOT NULL,
    temperature      TEXT          NOT NULL,
    montant_brut     NUMERIC(10,2) NOT NULL,
    fms_inclus       BOOLEAN       NOT NULL DEFAULT TRUE,
    fms_montant      NUMERIC(10,2) NOT NULL DEFAULT 0,
    montant_total    NUMERIC(10,2) NOT NULL,
    probabilite      INTEGER       NOT NULL,
    montant_pondere  NUMERIC(10,2) NOT NULL,
    commercial       TEXT          NOT NULL DEFAULT '—',
    date_creation    DATE          NOT NULL DEFAULT CURRENT_DATE,
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

ALTER TABLE pipe_do ENABLE ROW LEVEL SECURITY;

CREATE POLICY "acces_interne" ON pipe_do
    FOR ALL USING (true) WITH CHECK (true);

-- ─────────────────────────────────────────────────────────────────────────────
-- MIGRATION (si table déjà existante — ajoute uniquement la colonne commercial)
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE pipe_do ADD COLUMN IF NOT EXISTS commercial TEXT NOT NULL DEFAULT '—';
