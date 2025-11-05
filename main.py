from fastapi import FastAPI
from pydantic import BaseModel
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import aspect

app = FastAPI(
    title="Synastry Compatibility API",
    description="Compare two birth charts and return romantic compatibility insights.",
    version="1.0.0"
)

# --- INPUT MODELS ---
class Person(BaseModel):
    date: str   # YYYY-MM-DD
    time: str   # HH:MM (24-hour)
    lat: float  # Latitude
    lon: float  # Longitude

class SynastryInput(BaseModel):
    person1: Person
    person2: Person

# --- CORE LOGIC ---
@app.post("/synastry")
def synastry_chart(data: SynastryInput):
    p1 = data.person1
    p2 = data.person2

    chart1 = Chart(Datetime(p1.date, p1.time, '+00:00'), GeoPos(p1.lat, p1.lon))
    chart2 = Chart(Datetime(p2.date, p2.time, '+00:00'), GeoPos(p2.lat, p2.lon))

    planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']
    aspects_found = []

    # Compare planets between charts
    for a in planets:
        for b in planets:
            asp = aspect.getAspect(chart1.get(a), chart2.get(b))
            if asp:
                aspects_found.append({
                    "person1_planet": a,
                    "person2_planet": b,
                    "aspect": asp.type,
                    "orb": round(asp.orb, 2)
                })

    score, summary = calculate_score(aspects_found)

    return {
        "compatibility_score": score,
        "summary": summary,
        "aspects": aspects_found
    }


# --- COMPATIBILITY SCORING ---
def calculate_score(aspects):
    weights = {
        "CONJUNCTION": 10,
        "TRINE": 8,
        "SEXTILE": 6,
        "SQUARE": -5,
        "OPPOSITION": -8
    }

    romantic_pairs = [
        ("Venus", "Mars"), ("Mars", "Venus"),
        ("Sun", "Moon"), ("Moon", "Sun"),
        ("Venus", "Venus"), ("Mars", "Mars")
    ]

    total = 0
    romantic_bonus = 0

    for asp in aspects:
        base = weights.get(asp["aspect"], 0)
        total += base
        pair = (asp["person1_planet"], asp["person2_planet"])
        if pair in romantic_pairs:
            romantic_bonus += base * 0.5

    final_score = total + romantic_bonus
    normalized = round((final_score + 100) / 20, 1)  # 0–10 scale

    # Generate a short summary
    if normalized >= 8:
        summary = "Excellent chemistry and emotional harmony 💞"
    elif normalized >= 6:
        summary = "Strong potential with some dynamic tension 💫"
    elif normalized >= 4:
        summary = "Mixed connection — lessons and attraction both ⚖️"
    else:
        summary = "Challenging compatibility — may require patience 💔"

    return normalized, summary


# --- HEALTH CHECK ---
@app.get("/")
def home():
    return {"message": "Synastry API is live! Visit /docs to test."}
