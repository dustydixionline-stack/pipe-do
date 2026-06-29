-- Coller ce script dans l'éditeur SQL de ton projet Supabase
-- Dashboard → SQL Editor → New query

CREATE TABLE IF NOT EXISTS pipe_do (
    id            BIGSERIAL PRIMARY KEY,
    client        TEXT        NOT NULL,
    ville         TEXT        NOT NULL,
    type_contact  TEXT        NOT NULL DEFAULT 'Prospect',
    offre         TEXT        NOT NULL,
    statut        TEXT        NOT NULL,
    temperature   TEXT        NOT NULL,
    montant_brut  NUMERIC(10,2) NOT NULL,
    fms_inclus    BOOLEAN     NOT NULL DEFAULT TRUE,
    fms_montant   NUMERIC(10,2) NOT NULL DEFAULT 0,
    montant_total NUMERIC(10,2) NOT NULL,
    probabilite   INTEGER     NOT NULL,
    montant_pondere NUMERIC(10,2) NOT NULL,
    date_creation DATE        NOT NULL DEFAULT CURRENT_DATE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Sécurité : Row Level Security activé, accès total avec la clé anon (outil interne)
ALTER TABLE pipe_do ENABLE ROW LEVEL SECURITY;

CREATE POLICY "acces_interne" ON pipe_do
    FOR ALL
    USING (true)
    WITH CHECK (true);
