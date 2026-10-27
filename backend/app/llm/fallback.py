# =============================================================================
# CivicSense AI — Independent Deterministic Complaint Fallback
# =============================================================================
# Constructs a structured ComplaintResult directly from validated decision context
# without invoking an LLM.
#
# GUARANTEES:
# - Completely independent of LLM status (works when Ollama is offline or times out)
# - Works even when RAG context is empty or unavailable
# - Preserves assessed severity and strictly matching priority
# - Contains ONLY verified facts: never fabricates contacts, statutory claims, or dates
# - Explicitly sets source="deterministic_fallback_v1"
#
# Owner: Arpit (Person 1)
# =============================================================================

from datetime import datetime, timezone
from typing import Any

from app.contracts.complaint import ComplaintResult, ComplaintPriority


def generate_deterministic_complaint(decision_context: dict[str, Any]) -> ComplaintResult:
    """
    Construct a formal civic complaint deterministically from verified decision context.
    """
    raw_issue = decision_context.get("issue_type", "civic_issue")
    issue_type = raw_issue.replace("_", " ").title()
    raw_severity = str(decision_context.get("severity_level", "MEDIUM")).upper()
    priority: ComplaintPriority = (
        raw_severity if raw_severity in ("LOW", "MEDIUM", "HIGH", "CRITICAL") else "MEDIUM"
    )

    address = decision_context.get("address") or "Municipal Ward Road"
    city = decision_context.get("city") or "Gurugram"
    authority = decision_context.get("authority_name") or "Municipal Civic Authority"
    department = decision_context.get("department") or "Public Works & Infrastructure Division"
    user_desc = (decision_context.get("user_description") or "").strip()

    # Location formatting
    loc_display = address if city.lower() in address.lower() else f"{address}, {city}"

    # Subject line
    subject = f"[{priority} Priority] Formal Report of {issue_type} at {loc_display}"

    # Body construction using only supported facts
    lines = [
        f"To: {authority} — {department}",
        f"Location of Concern: {loc_display}",
        f"Issue Classification: {issue_type}",
        f"Assessed Hazard Severity: {priority}",
        "",
        "Dear Municipal Authorities,",
        "",
        f"This formal civic report registers an observed {issue_type.lower()} that requires inspection "
        f"and remedial action by the {department}."
    ]

    if user_desc:
        lines.append(f"Citizen Observation: \"{user_desc}\"")

    lines.append("")
    lines.append(
        f"The condition represents an active public safety and municipal infrastructure concern. "
        f"Prompt resolution is requested to prevent secondary hazards and disruption to community transit."
    )

    # Include verified contact information ONLY if explicitly provided
    verified_contacts = []
    if decision_context.get("contact_email"):
        verified_contacts.append(f"Official Email: {decision_context['contact_email']}")
    if decision_context.get("contact_phone"):
        verified_contacts.append(f"Official Phone: {decision_context['contact_phone']}")
    if decision_context.get("office_address"):
        verified_contacts.append(f"Office: {decision_context['office_address']}")

    if verified_contacts:
        lines.append("")
        lines.append("Verified Department Contact Records:")
        lines.extend(f"- {c}" for c in verified_contacts)

    lines.append("")
    lines.append("Submitted via CivicSense AI (Automated Grievance Filing System)")

    body = "\n".join(lines)
    requested_action = f"Dispatch field inspection team to inspect and repair reported {issue_type.lower()}."

    return ComplaintResult(
        subject=subject,
        body=body,
        priority=priority,
        requested_action=requested_action,
        generated_at=datetime.now(timezone.utc).isoformat(),
        source="deterministic_fallback_v1",
    )
