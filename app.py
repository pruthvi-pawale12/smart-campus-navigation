from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# =====================================
# AMGOI SMART CAMPUS LOCATIONS
# =====================================

CAMPUS_LOCATIONS = {

    "Main Gate": {
        "floor": "Ground Floor",
        "side": "Entrance",
        "info": "Main Campus Entrance",
        "rfid_tag": "12345678"
    },

    "Main Office": {
        "floor": "Ground Floor",
        "side": "Entrance Area",
        "info": "Main Office near Main Entrance",
        "rfid_tag": "OFFICE01"
    },

    "Civil Department": {
        "floor": "Ground Floor",
        "side": "Left Side",
        "info": "Civil Department",
        "rfid_tag": "CIVIL001"
    },

    "Mechanical Department": {
        "floor": "Ground Floor",
        "side": "Right Side",
        "info": "Mechanical Department",
        "rfid_tag": "MECH0001"
    },

    "Applied Science Department": {
        "floor": "First Floor",
        "side": "Left Side",
        "info": "Applied Science Department",
        "rfid_tag": "APPL0001"
    },

    "Computer Department": {
        "floor": "First Floor",
        "side": "Right Side",
        "info": "Computer Department",
        "rfid_tag": "COMP0001"
    },

    "Electrical Department": {
        "floor": "Second Floor",
        "side": "Left Side",
        "info": "Electrical Department",
        "rfid_tag": "ELEC0001"
    },

    "E&TC Department": {
        "floor": "Second Floor",
        "side": "Right Side",
        "info": "E&TC Department",
        "rfid_tag": "ENTC0001"
    },

    "Library": {
        "floor": "Second Floor",
        "side": "Central Corridor",
        "info": "Library in Second Floor Central Corridor",
        "rfid_tag": "LIBRARY01"
    },

    "Civil Lab": {
        "floor": "Ground Floor",
        "side": "Civil Department",
        "info": "Civil Department Laboratory",
        "rfid_tag": "CIVLAB01"
    },

    "Mechanical Lab": {
        "floor": "Ground Floor",
        "side": "Mechanical Department",
        "info": "Mechanical Department Laboratory",
        "rfid_tag": "MECHLAB01"
    },

    "Applied Science Lab": {
        "floor": "First Floor",
        "side": "Applied Science Department",
        "info": "Applied Science Department Laboratory",
        "rfid_tag": "APPLLAB01"
    },

    "Computer Lab": {
        "floor": "First Floor",
        "side": "Computer Department",
        "info": "Computer Department Laboratory",
        "rfid_tag": "COMPLAB01"
    },

    "Electrical Lab": {
        "floor": "Second Floor",
        "side": "Electrical Department",
        "info": "Electrical Department Laboratory",
        "rfid_tag": "ELECLAB01"
    },

    "E&TC Lab": {
        "floor": "Second Floor",
        "side": "E&TC Department",
        "info": "E&TC Department Laboratory",
        "rfid_tag": "ENTCLAB01"
    },

    "Canteen": {
        "floor": "To be confirmed",
        "side": "To be confirmed",
        "info": "Campus Canteen",
        "rfid_tag": "CANTEEN01"
    }
}


# =====================================
# ROUTE GENERATION
# =====================================

def generate_route(place):

    details = CAMPUS_LOCATIONS[place]

    floor = details["floor"]
    side = details["side"]

    if place == "Main Gate":
        return {
            "available": True,
            "staircase": "Not required",
            "steps": [
                "You are at the Main Entrance."
            ]
        }

    if place == "Main Office":
        return {
            "available": True,
            "staircase": "Not required",
            "steps": [
                "Start from Main Entrance.",
                "Walk towards entrance area.",
                "Reach Main Office."
            ]
        }

    if floor == "To be confirmed":
        return {
            "available": False,
            "staircase": "Not confirmed",
            "steps": [
                "Location details are not confirmed yet."
            ]
        }

    steps = ["Start from Main Entrance."]

    if place == "Library":

        staircase = "Left or Right Staircase"

        steps.extend([
            "Move through the Central Corridor.",
            "Use either staircase.",
            "Reach Second Floor.",
            "Walk towards the Central Corridor.",
            "Reach Library."
        ])

    elif floor == "Ground Floor":

        staircase = "Not required"

        steps.extend([
            "Enter Ground Floor.",
            f"Move towards {side}.",
            f"Reach {place}."
        ])

    else:

        if side in [
            "Left Side",
            "Civil Department",
            "Applied Science Department",
            "Electrical Department"
        ]:
            staircase = "Left Staircase"
        else:
            staircase = "Right Staircase"

        steps.append(f"Move towards {staircase}.")

        if floor == "First Floor":
            steps.append("Climb stairs to First Floor.")

        elif floor == "Second Floor":
            steps.append("Climb stairs to Second Floor.")

        steps.extend([
            f"Move towards {side}.",
            f"Reach {place}."
        ])

    return {
        "available": True,
        "staircase": staircase,
        "steps": steps
    }


# =====================================
# HOME PAGE
# =====================================

@app.route('/')
def home():

    return render_template(
        'index.html',
        locations=CAMPUS_LOCATIONS.keys()
    )


# =====================================
# CAMPUS MAP PAGE
# =====================================

@app.route('/map')
def show_map():

    selected_place = request.args.get(
        'place',
        'Main Gate'
    )

    if selected_place not in CAMPUS_LOCATIONS:
        selected_place = 'Main Gate'

    details = CAMPUS_LOCATIONS[selected_place]

    route = generate_route(selected_place)

    return render_template(
        'map.html',
        place=selected_place,
        details=details,
        locations=CAMPUS_LOCATIONS,
        route=route
    )


# =====================================
# ROUTE INFORMATION API
# =====================================

@app.route('/api/route')
def route_api():

    place = request.args.get(
        'place',
        'Main Gate'
    )

    if place not in CAMPUS_LOCATIONS:

        return jsonify({
            "status": "error",
            "message": "Invalid destination"
        }), 404

    return jsonify({
        "status": "success",
        "destination": place,
        "details": CAMPUS_LOCATIONS[place],
        "route": generate_route(place)
    })


# =====================================
# RFID HARDWARE API
# =====================================

@app.route('/api/hardware_trigger', methods=['POST'])
def hardware_trigger():

    data = request.get_json(silent=True) or {}

    card_id = data.get('rfid_id')

    for place, details in CAMPUS_LOCATIONS.items():

        if details["rfid_tag"] == card_id:

            return jsonify({
                "status": "success",
                "destination": place,
                "floor": details["floor"],
                "route": generate_route(place),
                "buzzer": "ON"
            })

    return jsonify({
        "status": "error",
        "message": "Unknown Card ID",
        "buzzer": "OFF"
    }), 404


# =====================================
# RUN FLASK SERVER
# =====================================

if __name__ == '__main__':

    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )