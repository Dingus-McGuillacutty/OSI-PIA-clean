// Controlled status transition for an Assessment.
// Suggested statuses: draft, review, validated, superseded, rejected.

:param assessment_id => 'ASM-SYNTHETIC-001';
:param new_status => 'review';
:param reviewer => 'REPLACE_REVIEWER_ID';
:param review_note => '';

MATCH (a:Assessment {assessment_id: $assessment_id})
SET a.status = $new_status,
    a.updated_at = datetime(),
    a.last_reviewed_by = $reviewer,
    a.review_note = $review_note
RETURN a.assessment_id, a.status, a.updated_at, a.last_reviewed_by;
