# =============================================================================
# CivicSense AI — LLM Prompt Templates & Assembly
# =============================================================================
# Constructs system and user prompts with strict anti-hallucination guardrails.
#
# Owner: Arpit (Person 1)
# =============================================================================

from typing import Any

SYSTEM_PROMPT = """You are CivicSense AI, an intelligent civic assistant that drafts formal, high-impact municipal grievance complaints on behalf of citizens.

Your task is to draft a structured civic complaint based strictly on verified evidence and administrative context.

CRITICAL OPERATIONAL RULES:
1. OUTPUT FORMAT: Respond ONLY with a valid JSON object matching this exact schema:
   {
     "subject": "<Concise, professional subject line mentioning priority, issue, and location>",
     "body": "<Formal grievance letter addressed to the authority, stating observations, location, hazard level, and urgency>",
     "priority": "<Must match the assessed severity level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'>",
     "requested_action": "<Specific, practical repair or inspection action requested>"
   }

2. ANTI-HALLUCINATION CONSTRAINTS:
   - Authority contact details (emails, phone numbers, office addresses) MUST NEVER be invented. You may only mention contacts that appear explicitly in the "Verified Authority Contacts" section. If no verified contact is provided, do NOT mention any phone numbers or emails.
   - Statutory deadlines, penal provisions, and specific laws MUST NEVER be fabricated. Only reference procedural guidelines or timelines if they are explicitly quoted in the "Retrieved Civic Knowledge" section.
   - Ground the complaint exclusively in the verified facts provided (issue type, severity, location, and user observation).
   - The complaint priority MUST strictly equal the provided severity level.
"""


def build_complaint_prompt(context: dict[str, Any]) -> str:
    """
    Construct the user prompt for the LLM from the validated decision context.
    """
    issue_type = context.get("issue_type", "civic issue").replace("_", " ").title()
    severity = context.get("severity_level", "MEDIUM").upper()
    address = context.get("address", "Unresolved Location")
    city = context.get("city", "Unresolved City")
    authority = context.get("authority_name", "Municipal Authority")
    department = context.get("department", "Public Works")
    user_desc = context.get("user_description", "").strip()

    # Verified contacts
    contact_email = context.get("contact_email")
    contact_phone = context.get("contact_phone")
    office_address = context.get("office_address")

    contacts_lines = []
    if contact_email:
        contacts_lines.append(f"- Email: {contact_email}")
    if contact_phone:
        contacts_lines.append(f"- Phone: {contact_phone}")
    if office_address:
        contacts_lines.append(f"- Office: {office_address}")
    contacts_str = "\n".join(contacts_lines) if contacts_lines else "None provided (DO NOT INVENT ANY CONTACTS)"

    # RAG knowledge
    rag_docs = context.get("rag_documents", [])
    if rag_docs:
        docs_formatted = "\n\n".join(f"[Guideline {i+1}]: {doc}" for i, doc in enumerate(rag_docs))
    else:
        docs_formatted = "No specific municipal charter documents available. (DO NOT INVENT CITATIONS OR STATUTORY DEADLINES)"

    prompt = f"""Draft a formal civic complaint based on the following verified decision context:

--- ISSUE DETAILS ---
- Primary Issue: {issue_type}
- Assessed Severity Level: {severity} (Complaint priority MUST be set to {severity})
- Citizen Note: {user_desc if user_desc else "No additional description provided"}

--- LOCATION CONTEXT ---
- Address: {address}
- City: {city}

--- RESPONSIBLE AUTHORITY ---
- Authority Name: {authority}
- Department: {department}

--- VERIFIED AUTHORITY CONTACTS ---
{contacts_str}

--- RETRIEVED CIVIC KNOWLEDGE ---
{docs_formatted}

Draft the formal complaint JSON now. Remember: pure JSON output only, no surrounding commentary, and do not invent any contact numbers, emails, or statutory deadlines.
"""
    return prompt
