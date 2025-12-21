import re
from datetime import datetime

try:
    from bson import ObjectId
    BSON_AVAILABLE = True
except ImportError:
    BSON_AVAILABLE = False


def serialize_doc(doc):
    """Convert MongoDB documents to JSON-serializable format"""
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    elif BSON_AVAILABLE and isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    return doc


def format_email_content(text, confidence=None):
    """
    Format email content in a clean professional structure:
    - Removes headers, markdown, placeholders
    - Normalizes spacing
    - Optionally appends confidence & hallucination report
    """

    if not text:
        return "No content available"

    # -----------------------------
    # Remove common email headers
    # -----------------------------
    text = re.sub(
        r'^(Subject:|From:|To:|Date:|Time:).*$', 
        '', 
        text, 
        flags=re.MULTILINE
    )

    # -----------------------------
    # Remove placeholders like [Name], [Date]
    # -----------------------------
    text = re.sub(r'\[.*?\]', '', text)

    # -----------------------------
    # Remove markdown formatting
    # -----------------------------
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

    # -----------------------------
    # Normalize whitespace
    # -----------------------------
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)

    # -----------------------------
    # Append Confidence Report (if available)
    # -----------------------------
    if confidence:
        confidence_block = [
            "",
            "----------------------------------------",
            "AI Confidence & Reliability Report",
            "----------------------------------------",
            f"Confidence Score     : {confidence.get('confidence_score', 'N/A')} / 100",
            f"Hallucination Risk   : {confidence.get('hallucination_risk', 'N/A')}",
        ]

        issues = confidence.get("issues", [])
        if issues:
            confidence_block.append("Identified Issues:")
            for i, issue in enumerate(issues, start=1):
                confidence_block.append(f"  {i}. {issue}")
        else:
            confidence_block.append("Identified Issues: None")

        text += "\n" + "\n".join(confidence_block)

    return text


def parse_command(command: str):
    """
    Parse commands like:
    - "create report and send to abc@gmail.com"
    - "send meeting reminder to xyz@gmail.com"
    
    Returns: {"goal": "...", "email": "..."}
    """
    # Email regex pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # Extract email
    email_match = re.search(email_pattern, command)
    if not email_match:
        raise ValueError("No valid email found in command")
    
    email = email_match.group(0)
    
    # Remove email and "send to"/"and send to" from command to get goal
    goal = re.sub(rf'\s+(and\s+)?send\s+to\s+{re.escape(email)}', '', command, flags=re.IGNORECASE)
    goal = re.sub(rf'\s+(and\s+)?send\s+to\s+{re.escape(email)}', '', goal, flags=re.IGNORECASE)
    goal = goal.strip()
    
    if not goal:
        raise ValueError("No goal/action found in command")
    
    return {"goal": goal, "email": email}

