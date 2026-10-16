"""NutriFit AI — Smart nutrition & fitness tracker: calorie/macro targets (Mifflin-St Jeor), food & water logging,
MET-based workouts, weight forecasting with regression and AI meal suggestions.
Run:  python app.py   →  http://127.0.0.1:5000   (demo: demo@example.com / Demo@1234)
"""
import random
from datetime import date, datetime, timedelta

import numpy as np
from flask import flash, g, jsonify, redirect, render_template, request, url_for

from core import create_app, execute, login_required, query
from foods import ACTIVITIES, FOOD_BY_ID, FOODS

UI = dict(
    name="NutriFit AI", short="Nutrition & Fitness Coach", icon="🥗", accent1="#22C55E", accent2="#06B6D4", home="today",
    tagline="Know exactly what to eat, drink and burn. Personal calorie & macro targets, a 60+ Indian food database and AI forecasts of your progress.",
    hero='Eat smart. Move more. <span class="gradient-text">See the future you.</span>', badge="Health & wellness AI",
    features=[("bi-fire", "Personal targets", "BMR, TDEE and macros from your body & goal"),
              ("bi-egg-fried", "Indian food database", "Log idli to biryani in two taps with live search"),
              ("bi-graph-down-arrow", "Weight forecast", "Regression predicts when you'll hit your target")],
    float=['🔥 <b>1,420</b> / 1,950 kcal today', '💧 <b class="gradient-text">2.25 L</b> water · goal reached!'],
    nav=[("Today", "today", "bi-sun"), ("Trends", "trends", "bi-graph-up"), ("Body & Goals", "plan", "bi-person-bounding-box")],
    search_hint="Search foods…", promo_title="Health note", promo="Estimates are for general wellness only — consult a professional for medical advice.",
)
SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE, gender TEXT DEFAULT 'male', age INTEGER DEFAULT 28,
    height_cm REAL DEFAULT 170, weight_kg REAL DEFAULT 70, activity REAL DEFAULT 1.375, goal TEXT DEFAULT 'maintain',
    target_weight REAL DEFAULT 68, water_goal INTEGER DEFAULT 2500);
CREATE TABLE IF NOT EXISTS food_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, date TEXT NOT NULL,
    meal TEXT NOT NULL, food TEXT NOT NULL, emoji TEXT, qty REAL NOT NULL, kcal REAL, protein REAL, carbs REAL, fat REAL);
CREATE TABLE IF NOT EXISTS water_logs (user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, date TEXT NOT NULL, ml INTEGER NOT NULL, PRIMARY KEY(user_id, date));
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, date TEXT NOT NULL,
    activity TEXT NOT NULL, minutes INTEGER NOT NULL, kcal REAL NOT NULL);
CREATE TABLE IF NOT EXISTS weights (user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, date TEXT NOT NULL, kg REAL NOT NULL, PRIMARY KEY(user_id, date));
"""
GOALS = {"lose": (-500, "Lose weight"), "maintain": (0, "Maintain"), "gain": (300, "Build muscle")}
ACT_LEVELS = [(1.2, "Sedentary (desk job)"), (1.375, "Lightly active (1–3 days/wk)"), (1.55, "Moderately active (3–5 days/wk)"),
              (1.725, "Very active (6–7 days/wk)"), (1.9, "Athlete / physical job")]
MEALS = [("breakfast", "Breakfast", "🌅"), ("lunch", "Lunch", "☀️"), ("snacks", "Snacks", "🍎"), ("dinner", "Dinner", "🌙")]


def log_food(uid, d, meal, food, qty):
    execute("INSERT INTO food_logs(user_id,date,meal,food,emoji,qty,kcal,protein,carbs,fat) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (uid, d, meal, food["name"], food["emoji"], qty, food["kcal"] * qty, food["protein"] * qty, food["carbs"] * qty, food["fat"] * qty))


def seed_demo(uid):
    rng = random.Random(4)
    execute("INSERT INTO profiles(user_id,gender,age,height_cm,weight_kg,activity,goal,target_weight) VALUES(?,?,?,?,?,?,?,?)",
            (uid, "male", 32, 172, 81, 1.375, "lose", 74))
    plan = {"breakfast": [1, 2, 4, 5, 7, 8, 28, 41], "lunch": [11, 13, 18, 20, 21, 25, 40, 12], "snacks": [31, 32, 37, 28, 46, 55], "dinner": [9, 13, 17, 19, 59, 23, 60]}
    w = 84.5
    for back in range(45, -1, -1):
        d = (date.today() - timedelta(days=back)).isoformat()
        for meal, ids in plan.items():
            if back == 0 and meal == "dinner":
                continue
            for fid in rng.sample(ids, 2 if meal != "snacks" else 1):
                log_food(uid, d, meal, FOOD_BY_ID[fid], rng.choice([1, 1, 1, 1.5, 2]))
        execute("INSERT INTO water_logs VALUES(?,?,?)", (uid, d, rng.choice([1750, 2000, 2250, 2500, 2750]) if back else 1500))
        if rng.random() < .6:
            act = rng.choice(list(ACTIVITIES))
            mins = rng.choice([20, 30, 45, 60])
            execute("INSERT INTO workouts(user_id,date,activity,minutes,kcal) VALUES(?,?,?,?,?)", (uid, d, act, mins, round(ACTIVITIES[act] * w * mins / 60)))
        w -= rng.uniform(0.02, 0.17)
        if back % 3 == 0:
            execute("INSERT INTO weights VALUES(?,?,?)", (uid, d, round(w + rng.uniform(-.3, .3), 1)))
    execute("UPDATE profiles SET weight_kg=? WHERE user_id=?", (round(w, 1), uid))


def on_register(uid):
    execute("INSERT INTO profiles(user_id) VALUES(?)", (uid,))


app = create_app(__name__, UI, SCHEMA, seed_demo=seed_demo, on_register=on_register)


def profile(uid):
    p = query("SELECT * FROM profiles WHERE user_id=?", (uid,), one=True)
    if not p:
        execute("INSERT INTO profiles(user_id) VALUES(?)", (uid,))
        p = query("SELECT * FROM profiles WHERE user_id=?", (uid,), one=True)
    bmr = 10 * p["weight_kg"] + 6.25 * p["height_cm"] - 5 * p["age"] + (5 if p["gender"] == "male" else -161)
    tdee = bmr * p["activity"]
    target = max(1200, tdee + GOALS[p["goal"]][0])
    protein = round(p["weight_kg"] * (2.0 if p["goal"] == "gain" else 1.6))
    fat = round(target * 0.27 / 9)
    carbs = round((target - protein * 4 - fat * 9) / 4)
    bmi = p["weight_kg"] / (p["height_cm"] / 100) ** 2
    cat = "Underweight" if bmi < 18.5 else "Healthy" if bmi < 23 else "Overweight" if bmi < 27.5 else "Obese"  # Asian BMI cut-offs
    return dict(p, bmr=round(bmr), tdee=round(tdee), target=round(target), protein=protein, fat=fat, carbs=carbs, bmi=round(bmi, 1), bmi_cat=cat)


def day_summary(uid, d):
    foods = query("SELECT * FROM food_logs WHERE user_id=? AND date=? ORDER BY id", (uid, d))
    water = (query("SELECT ml FROM water_logs WHERE user_id=? AND date=?", (uid, d), one=True) or {"ml": 0})["ml"]
    wk = query("SELECT * FROM workouts WHERE user_id=? AND date=? ORDER BY id", (uid, d))
    tot = {k: round(sum(f[k] for f in foods), 1) for k in ("kcal", "protein", "carbs", "fat")}
    return dict(foods=foods, water=water, workouts=wk, totals=tot, burned=round(sum(w["kcal"] for w in wk)))


def suggestions(pr, day):
    """Greedy picks of foods that fit remaining calories, prioritising protein density."""
    remaining = pr["target"] - day["totals"]["kcal"] + day["burned"]
    need_p = pr["protein"] - day["totals"]["protein"]
    pool = sorted([f for f in FOODS if f["kcal"] <= max(remaining, 0)], key=lambda f: -(f["protein"] / max(f["kcal"], 1)) if need_p > 15 else abs(f["kcal"] - remaining / 2))
    picks, left = [], remaining
    for f in pool:
        if f["kcal"] <= left and len(picks) < 4 and f["name"] not in {x["food"] for x in day["foods"]}:
            picks.append(f)
            left -= f["kcal"]
    return round(remaining), picks


@app.route("/today")
@login_required
def today():
    d = request.args.get("date") or date.today().isoformat()
    pr = profile(g.user["id"])
    day = day_summary(g.user["id"], d)
    rem, picks = suggestions(pr, day)
    return render_template("today.html", pr=pr, day=day, d=d, rem=rem, picks=picks, MEALS=MEALS, ACTIVITIES=ACTIVITIES, page_title="Today")


@app.route("/trends")
@login_required
def trends():
    uid, pr = g.user["id"], profile(g.user["id"])
    days = [(date.today() - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]
    cal = {r["date"]: r for r in query("SELECT date, SUM(kcal) kcal, SUM(protein) p, SUM(carbs) c, SUM(fat) f FROM food_logs WHERE user_id=? GROUP BY date", (uid,))}
    burn = {r["date"]: r["k"] for r in query("SELECT date, SUM(kcal) k FROM workouts WHERE user_id=? GROUP BY date", (uid,))}
    water = {r["date"]: r["ml"] for r in query("SELECT date, ml FROM water_logs WHERE user_id=?", (uid,))}
    ws = query("SELECT date, kg FROM weights WHERE user_id=? ORDER BY date", (uid,))
    forecast = None
    if len(ws) >= 4:
        x = np.array([(datetime.strptime(w["date"], "%Y-%m-%d").date() - date.today()).days for w in ws], float)
        y = np.array([w["kg"] for w in ws])
        slope, icpt = np.polyfit(x, y, 1)
        weekly = slope * 7
        eta = None
        if (pr["goal"] == "lose" and slope < 0 and pr["target_weight"] < icpt) or (pr["goal"] == "gain" and slope > 0 and pr["target_weight"] > icpt):
            eta_days = int((pr["target_weight"] - icpt) / slope)
            eta = (date.today() + timedelta(days=eta_days)).strftime("%d %b %Y")
        future = [(date.today() + timedelta(days=k)).isoformat() for k in range(0, 61, 5)]
        forecast = dict(weekly=round(weekly, 2), eta=eta, line=[{"d": f, "kg": round(icpt + slope * k, 1)} for f, k in zip(future, range(0, 61, 5))])
    logged = [cal[d]["kcal"] for d in days if d in cal]
    return render_template("trends.html", pr=pr, page_title="Trends",
                           data=dict(days=[d[5:] for d in days], kcal=[round(cal[d]["kcal"]) if d in cal else 0 for d in days],
                                     burn=[round(burn.get(d, 0)) for d in days], water=[water.get(d, 0) for d in days],
                                     weights=ws, forecast=forecast, target=pr["target"],
                                     macros=[round(sum(cal[d][k] for d in days if d in cal) / max(1, len(logged))) for k in ("p", "c", "f")]),
                           avg=round(sum(logged) / len(logged)) if logged else 0, streak=sum(1 for d in days if d in cal))


@app.route("/plan", methods=["GET", "POST"])
@login_required
def plan():
    if request.method == "POST":
        f = request.form
        try:
            vals = (f["gender"], int(f["age"]), float(f["height_cm"]), float(f["weight_kg"]), float(f["activity"]), f["goal"], float(f["target_weight"]), int(f["water_goal"]))
            assert 10 <= vals[1] <= 100 and 100 <= vals[2] <= 250 and 25 <= vals[3] <= 300 and vals[5] in GOALS
        except (KeyError, ValueError, AssertionError):
            flash("Please check the values you entered.", "danger")
            return redirect(url_for("plan"))
        execute("UPDATE profiles SET gender=?,age=?,height_cm=?,weight_kg=?,activity=?,goal=?,target_weight=?,water_goal=? WHERE user_id=?", vals + (g.user["id"],))
        execute("INSERT INTO weights VALUES(?,?,?) ON CONFLICT(user_id,date) DO UPDATE SET kg=excluded.kg", (g.user["id"], date.today().isoformat(), vals[3]))
        flash("Targets recalculated ✨", "success")
        return redirect(url_for("plan"))
    return render_template("plan.html", pr=profile(g.user["id"]), GOALS=GOALS, ACT=ACT_LEVELS, page_title="Body & Goals")


# ---------------------------------------------------------------- API
@app.get("/api/foods")
@login_required
def api_foods():
    q = request.args.get("q", "").lower().strip()
    res = [f for f in FOODS if q in f["name"].lower()] if q else FOODS[:12]
    return jsonify(res[:12])


@app.post("/api/food")
@login_required
def api_food_add():
    d = request.get_json(force=True)
    food = FOOD_BY_ID.get(int(d.get("food_id", 0)))
    meal = d.get("meal") if d.get("meal") in {m[0] for m in MEALS} else "snacks"
    qty = max(0.25, min(10, float(d.get("qty", 1))))
    if not food:
        return jsonify(error="Unknown food"), 400
    log_food(g.user["id"], d.get("date") or date.today().isoformat(), meal, food, qty)
    return jsonify(ok=True)


@app.delete("/api/food/<int:fid>")
@login_required
def api_food_del(fid):
    execute("DELETE FROM food_logs WHERE id=? AND user_id=?", (fid, g.user["id"]))
    return jsonify(ok=True)


@app.post("/api/water")
@login_required
def api_water():
    d = request.get_json(force=True)
    day = d.get("date") or date.today().isoformat()
    delta = int(d.get("ml", 250))
    cur = (query("SELECT ml FROM water_logs WHERE user_id=? AND date=?", (g.user["id"], day), one=True) or {"ml": 0})["ml"]
    new = max(0, min(8000, cur + delta))
    execute("INSERT INTO water_logs VALUES(?,?,?) ON CONFLICT(user_id,date) DO UPDATE SET ml=excluded.ml", (g.user["id"], day, new))
    return jsonify(ml=new)


@app.post("/api/workout")
@login_required
def api_workout():
    d = request.get_json(force=True)
    act, mins = d.get("activity"), int(d.get("minutes", 0))
    if act not in ACTIVITIES or not 1 <= mins <= 600:
        return jsonify(error="Choose an activity and duration"), 400
    kcal = round(ACTIVITIES[act] * profile(g.user["id"])["weight_kg"] * mins / 60)
    execute("INSERT INTO workouts(user_id,date,activity,minutes,kcal) VALUES(?,?,?,?,?)", (g.user["id"], d.get("date") or date.today().isoformat(), act, mins, kcal))
    return jsonify(ok=True, kcal=kcal)


@app.delete("/api/workout/<int:wid>")
@login_required
def api_workout_del(wid):
    execute("DELETE FROM workouts WHERE id=? AND user_id=?", (wid, g.user["id"]))
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(debug=True)
