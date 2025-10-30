"""
Business configuration - Template for easy customization.

TODO: Copy this file for each new client and update all values below.
"""

# ===== BUSINESS IDENTITY =====
BUSINESS_NAME = "YOUR_BUSINESS_NAME"  # e.g., "Acme Salon" or "Smith Law Office"

# ===== SERVICES OFFERED =====
SERVICES = [
    # Format: {"name": "Service Name", "price": "Price or 'varies'"}
    {"name": "SERVICE_1", "price": "$XX"},
    {"name": "SERVICE_2", "price": "$YY"},
    {"name": "SERVICE_3", "price": "varies"},
]

# ===== BUSINESS HOURS =====
HOURS = {
    "weekday": "Monday – Friday: 9:00 AM – 5:00 PM",
    "weekend": "Saturday & Sunday: Closed",
    "notes": "Evening appointments available by request",
}

# ===== STAFF =====
STAFF = [
    {"role": "ROLE_1", "name": "FULL_NAME_1"},
    {"role": "ROLE_2", "name": "FULL_NAME_2"},
]

# ===== OFFICE LOCATION(S) =====
LOCATION = "CITY, STATE"  # e.g., "Jersey City, NJ"

# ===== CONTACT INFO =====
PHONE = "+1XXXXXXXXXX"
EMAIL = "contact@yourbusiness.com"

# ===== ESCALATION =====
ESCALATION_CONTACT = "STAFF_NAME"  # Who to transfer to for human help
ESCALATION_PHONE = "+1XXXXXXXXXX"  # Optional: number to dial for transfer
