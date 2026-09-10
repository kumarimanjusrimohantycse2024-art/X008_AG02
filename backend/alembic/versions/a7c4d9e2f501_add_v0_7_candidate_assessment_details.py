"""add v0.7 candidate assessment details

Revision ID: a7c4d9e2f501
Revises: e116ecc0f691
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a7c4d9e2f501"
down_revision: Union[str, None] = "e116ecc0f691"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_candidate_assessments_required_coverage_range", "candidate_assessments", type_="check")
    op.drop_constraint("ck_candidate_assessments_preferred_coverage_range", "candidate_assessments", type_="check")
    op.drop_constraint("ck_candidate_assessments_evidence_quality_range", "candidate_assessments", type_="check")
    jsonb = postgresql.JSONB(astext_type=sa.Text())
    op.alter_column("candidate_assessments", "required_coverage", type_=jsonb, postgresql_using="jsonb_build_object('total', 0, 'met', 0, 'partially_met', 0, 'unsupported', 0, 'not_found', 0, 'coverage', required_coverage)", existing_nullable=False)
    op.alter_column("candidate_assessments", "preferred_coverage", type_=jsonb, postgresql_using="jsonb_build_object('total', 0, 'met', 0, 'partially_met', 0, 'unsupported', 0, 'not_found', 0, 'coverage', preferred_coverage)", existing_nullable=False)
    op.alter_column("candidate_assessments", "evidence_quality", type_=jsonb, postgresql_using="jsonb_build_object('label', 'insufficient', 'strong', 0, 'moderate', 0, 'weak', 0, 'none', 0, 'coverage', evidence_quality)", existing_nullable=False)
    op.add_column("assessments", sa.Column("claim_id", sa.UUID(), nullable=True))
    op.add_column("assessments", sa.Column("claim_ids", jsonb, nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.add_column("assessments", sa.Column("evidence_refs", jsonb, nullable=False, server_default=sa.text("'[]'::jsonb")))
    op.create_foreign_key("fk_assessments_claim_id_claims", "assessments", "claims", ["claim_id"], ["id"], ondelete="SET NULL")
    op.alter_column("assessments", "claim_ids", server_default=None)
    op.alter_column("assessments", "evidence_refs", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_assessments_claim_id_claims", "assessments", type_="foreignkey")
    op.drop_column("assessments", "evidence_refs")
    op.drop_column("assessments", "claim_ids")
    op.drop_column("assessments", "claim_id")
    numeric = sa.Numeric(4, 3)
    op.alter_column("candidate_assessments", "required_coverage", type_=numeric, postgresql_using="COALESCE(required_coverage->>'coverage', '0')::numeric", existing_nullable=False)
    op.alter_column("candidate_assessments", "preferred_coverage", type_=numeric, postgresql_using="COALESCE(preferred_coverage->>'coverage', '0')::numeric", existing_nullable=False)
    op.alter_column("candidate_assessments", "evidence_quality", type_=numeric, postgresql_using="COALESCE(evidence_quality->>'coverage', '0')::numeric", existing_nullable=False)
    op.create_check_constraint("ck_candidate_assessments_required_coverage_range", "candidate_assessments", "required_coverage >= 0 AND required_coverage <= 1")
    op.create_check_constraint("ck_candidate_assessments_preferred_coverage_range", "candidate_assessments", "preferred_coverage >= 0 AND preferred_coverage <= 1")
    op.create_check_constraint("ck_candidate_assessments_evidence_quality_range", "candidate_assessments", "evidence_quality >= 0 AND evidence_quality <= 1")