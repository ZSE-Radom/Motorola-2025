session_events = {}


def add_event(session_id, event):
    if session_id not in session_events:
        session_events[session_id] = []
    session_events[session_id].append(event)


def get_events(session_id):
    if session_id not in session_events:
        return []
    events = session_events[session_id]
    session_events[session_id] = []
    return events
