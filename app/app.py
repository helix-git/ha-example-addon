import os
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
CORE_API_URL = "http://supervisor/core/api"


def get_person_entity(user_id, headers):
    """Find person entity matching the user_id and get entity_picture"""
    try:
        response = requests.get(
            f"{CORE_API_URL}/states",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        states = response.json()

        # Find person.* entity where user_id attribute matches
        for state in states:
            if state.get('entity_id', '').startswith('person.'):
                attrs = state.get('attributes', {})
                if attrs.get('user_id') == user_id:
                    return {
                        'entity_id': state.get('entity_id'),
                        'friendly_name': attrs.get('friendly_name'),
                        'entity_picture': attrs.get('entity_picture'),
                    }
        return None
    except Exception as e:
        print(f"Error fetching person entity: {e}", flush=True)
        return None


@app.route('/')
def index():
    # Get user info from Ingress headers
    user_id = request.headers.get('X-Remote-User-Id')
    user_name = request.headers.get('X-Remote-User-Name')
    user_display_name = request.headers.get('X-Remote-User-Display-Name')

    print(f"Ingress Headers - ID: {user_id}, Name: {user_name}", flush=True)

    user_info = None
    error_message = None

    if user_id and SUPERVISOR_TOKEN:
        headers = {
            "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
            "Content-Type": "application/json",
        }

        # Get person entity for profile picture
        person = get_person_entity(user_id, headers)

        user_info = {
            "id": user_id,
            "name": user_display_name or user_name or "Unknown User",
            "username": user_name,
            "picture": person.get('entity_picture') if person else None,
            "entity_id": person.get('entity_id') if person else None,
        }
        print(f"User info: {user_info}", flush=True)

    else:
        if not user_id:
            error_message = "X-Remote-User-Id header missing. Access via Ingress required."
        if not SUPERVISOR_TOKEN:
            error_message = "SUPERVISOR_TOKEN not available."

    return render_template('index.html', user=user_info, error=error_message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8099, debug=False)
