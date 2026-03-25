import json
import os

STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")

DEFAULT_STATE = {"deal_active": False, "coupon_code": None, "discount": None}


def load_state():
    """Load the last known deal state from disk."""
    if not os.path.exists(STATE_FILE):
        return DEFAULT_STATE.copy()
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return DEFAULT_STATE.copy()


def save_state(state):
    """Persist the current deal state to disk."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def detect_new_deal(current_scrape):
    """
    Compare current scrape against stored state.
    Returns (should_alert: bool, deal_data: dict)
    Alert only fires on inactive → active transition.
    """
    previous = load_state()

    deal_active = current_scrape.get("deal_active", False)
    was_active = previous.get("deal_active", False)

    # Build new state
    new_state = {
        "deal_active": deal_active,
        "coupon_code": current_scrape.get("coupon_code"),
        "discount": current_scrape.get("discount"),
    }

    # Trigger alert only on transition: inactive → active
    should_alert = deal_active and not was_active

    # Save updated state
    save_state(new_state)

    if should_alert:
        print("[Detector] New deal detected! Triggering alert.")
    elif deal_active:
        print("[Detector] Deal still active, no new alert needed.")
    else:
        print("[Detector] No deal active.")

    return should_alert, new_state
