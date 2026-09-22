-- ==========================================================
-- FITFLOW — PG_CRON NIGHTLY AGGREGATION SETUP (POSTGRESQL)
-- ==========================================================
-- This script configures the nightly background aggregation job
-- in PostgreSQL / Supabase using the pg_cron extension.
--
-- Running time: Every night at 02:00 UTC (07:30 IST)
-- Target: summary_metrics table
-- ==========================================================

-- 1. Ensure pg_cron extension exists (on Supabase, enable via Dashboard -> Database -> Extensions)
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 2. Stored function to recompute daily metrics for ALL gyms
CREATE OR REPLACE FUNCTION recompute_gym_metrics_for_all(target_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
DECLARE
    gym_rec RECORD;
    v_active_members INT;
    v_mrr NUMERIC(12, 2);
    v_renewal_rate NUMERIC(5, 2);
    v_at_risk_count INT;
    v_ended_count INT;
    v_renewed_count INT;
BEGIN
    FOR gym_rec IN SELECT id FROM gyms LOOP
        -- Active Members
        SELECT COUNT(DISTINCT member_id)
        INTO v_active_members
        FROM memberships
        WHERE gym_id = gym_rec.id
          AND status = 'active'
          AND target_date BETWEEN start_date AND end_date;

        -- Monthly Recurring Revenue (Normalized 30-day baseline)
        SELECT COALESCE(SUM(p.price * (30.0 / NULLIF(p.duration_days, 0))), 0.00)
        INTO v_mrr
        FROM memberships m
        JOIN membership_plans p ON m.plan_id = p.id
        WHERE m.gym_id = gym_rec.id
          AND m.status = 'active'
          AND target_date BETWEEN m.start_date AND m.end_date;

        -- Renewal Rate (rolling 30-day window)
        SELECT COUNT(DISTINCT member_id)
        INTO v_ended_count
        FROM memberships
        WHERE gym_id = gym_rec.id
          AND end_date BETWEEN (target_date - INTERVAL '30 days')::DATE AND target_date;

        IF v_ended_count > 0 THEN
            SELECT COUNT(DISTINCT m.member_id)
            INTO v_renewed_count
            FROM memberships m
            WHERE m.gym_id = gym_rec.id
              AND (m.status = 'active' OR m.start_date >= (target_date - INTERVAL '30 days')::DATE)
              AND m.member_id IN (
                  SELECT member_id FROM memberships
                  WHERE gym_id = gym_rec.id AND end_date BETWEEN (target_date - INTERVAL '30 days')::DATE AND target_date
              );
            v_renewal_rate := LEAST(100.0, (v_renewed_count::NUMERIC / v_ended_count::NUMERIC) * 100.0);
        ELSE
            IF v_active_members > 0 THEN
                v_renewal_rate := 100.00;
            ELSE
                v_renewal_rate := 0.00;
            END IF;
        END IF;

        -- At-Risk Members Count:
        -- Rule 1: Active membership expiring in <= 7 days
        -- Rule 2: Failed payment in last 30 days without subsequent success
        SELECT COUNT(DISTINCT member_id)
        INTO v_at_risk_count
        FROM (
            SELECT member_id
            FROM memberships
            WHERE gym_id = gym_rec.id
              AND status = 'active'
              AND end_date BETWEEN target_date AND (target_date + INTERVAL '7 days')::DATE
            UNION
            SELECT p.member_id
            FROM payments p
            WHERE p.gym_id = gym_rec.id
              AND p.status = 'failed'
              AND p.paid_at >= (target_date - INTERVAL '30 days')
              AND NOT EXISTS (
                  SELECT 1 FROM payments p2
                  WHERE p2.gym_id = gym_rec.id
                    AND p2.member_id = p.member_id
                    AND p2.status = 'success'
                    AND p2.paid_at > p.paid_at
              )
        ) at_risk_combined;

        -- Upsert into summary_metrics
        INSERT INTO summary_metrics (
            id,
            gym_id,
            metric_date,
            active_members,
            mrr,
            renewal_rate,
            at_risk_count,
            new_members,
            churned_members,
            created_at
        )
        VALUES (
            gen_random_uuid(),
            gym_rec.id,
            target_date,
            COALESCE(v_active_members, 0),
            COALESCE(v_mrr, 0.00),
            COALESCE(v_renewal_rate, 0.00),
            COALESCE(v_at_risk_count, 0),
            0,
            0,
            NOW()
        )
        ON CONFLICT (gym_id, metric_date) DO UPDATE SET
            active_members = EXCLUDED.active_members,
            mrr = EXCLUDED.mrr,
            renewal_rate = EXCLUDED.renewal_rate,
            at_risk_count = EXCLUDED.at_risk_count;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 3. Schedule the cron job to run nightly at 02:00 AM UTC
-- Remove existing schedule if present
SELECT cron.unschedule('fitflow-nightly-aggregation')
WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'fitflow-nightly-aggregation');

SELECT cron.schedule(
    'fitflow-nightly-aggregation',
    '0 2 * * *',
    'SELECT recompute_gym_metrics_for_all(CURRENT_DATE);'
);
