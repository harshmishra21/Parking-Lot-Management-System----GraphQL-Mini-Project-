# 🅿️ Parking Lot API - Test Queries (Hinglish Guide)

Yeh file mein saare **5 main GraphQL queries** hain jo aap seedha playground mein copy-paste karke test kar sakte ho.

**Playground kholo:** [http://localhost:8001/graphql](http://localhost:8001/graphql)

> ⚠️ **Zaroori tip:** Har query paste karne se pehle editor mein `Cmd + A` dabao (sab select karo), phir purana text delete karo, **tab** naya query paste karo. Nahi toh syntax error aayega!

---

## 🔍 Query 1 — Parking Lot Ka Poora Status

**Kya karta hai?**
Yeh query batata hai ki parking lot mein:
- Kitne spots **available** hain (khali jagah)
- Kitne spots **occupied** hain (bhari jagah)
- Lot ka **overall status** kya hai — `"Available"`, `"Almost Full"`, `"Full"`, ya `"Empty"`
- Har individual spot ka **number, type aur status**

Basically, is ek query se puri parking lot ki LIVE picture mil jaati hai! 🎯

```graphql
query {
  parkingLot(id: 1) {
    name
    totalSpots
    availableSpots
    occupiedSpots
    lotStatus
    spots {
      spotNumber
      type
      status
    }
  }
}
```

**Expected Result:** `"lotStatus": "Available"` — Downtown Central Parking ke 20 spots mein se 18 available honge (seed ke baad).

---

## 🚗 Query 2 — Vehicle (Gaadi) Ki Poori Parking History

**Kya karta hai?**
Kisi bhi specific gaadi (yahan ID 1 wali Tesla) ka complete parking record dikhata hai:
- Har session ka **entryTime** (kab aayi)
- **exitTime** (kab gayi)
- **totalFee** (kitne paise diye)
- **status** (completed hai ya abhi bhi active)

Gaadi ka poora itihaar ek baar mein! 📋

```graphql
query {
  vehicle(id: 1) {
    licensePlate
    make
    sessions {
      entryTime
      exitTime
      totalFee
      status
    }
  }
}
```

**Expected Result:** `"licensePlate": "XYZ-123"` wali Tesla ki completed sessions aur fees dikhegi.

---

## 🔴 Query 3 — Abhi Kaun Kaun Khada Hai? (Live Active Sessions)

**Kya karta hai?**
Real-time mein jo bhi gaadiyaan parking lot mein khadi hain, unki poori list aati hai:
- **Session ID** (unique number)
- **entryTime** — kab se gaadi andar hai
- **exitTime** — abhi active sessions mein yeh `null` hoga (gaadi abhi baahar nahi gayi)
- Spot ka **spotNumber** aur **status**
- Gaadi ka **licensePlate**

Security waly ya attendant is query se check kar sakte hain ki kaun parking mein hai! 👀

```graphql
query {
  activeSessions {
    id
    entryTime
    exitTime
    status
    spot {
      spotNumber
      status
    }
    vehicle {
      licensePlate
    }
  }
}
```

**Expected Result:** 2 active sessions hongi (seed ke baad) — LMN-456 aur EVR-777 wali gaadiyan.

---

## 🟢 Query 4 — Naya Parking Session Shuru Karo (Gaadi Andar Aaye)

**Kya karta hai?**
Jab koi nayi gaadi parking mein aati hai, tab yeh mutation run karo. Isse:
- Ek **naya session** create hota hai
- **entryTime** automatically set ho jaata hai (abhi ka time)
- **exitTime** abhi `null` hoga (gaadi andar hai)
- Spot status `"occupied"` ho jaata hai

> ⚠️ **Dhyan rakhna:** `spotId: 3` sirf tabhi kaam karega jab spot available ho. Pehle Query 1 chalao aur dekho kaunsa spot `"available"` hai, phir woh `spotId` yahan daalein!

```graphql
mutation {
  startSession(input: {
    lotId: 1
    spotId: 3
    vehicleId: 1
  }) {
    session {
      id
      entryTime
      exitTime
      status
    }
  }
}
```

**Expected Result:** Naya session bana, `"status": "active"`, `"exitTime": null`. **Response mein jo `id` aaye, usse note karo — Query 5 mein kaam aayega!**

---

## 🔴 Query 5 — Parking Session Khatam Karo (Gaadi Baahir Jaaye)

**Kya karta hai?**
Jab gaadi baahir jaati hai, yeh mutation chalao. Isse:
- **exitTime** automatically set hota hai (abhi ka time)
- **totalFee** calculate hoti hai (ghante ke hisaab se — minimum 1 ghante ka charge)
- Session **status** `"completed"` ho jaata hai
- Spot dobara `"available"` ho jaata hai

> ⚠️ **Pehle Query 4 chalao**, phir ussi response mein `id` jo aaye (jaise `5`), woh `sessionId` ki jagah yahan daalein!

```graphql
mutation {
  endSession(input: {
    sessionId: 5
  }) {
    session {
      id
      entryTime
      exitTime
      totalFee
      status
    }
  }
}
```

**Expected Result:** `"status": "completed"`, `"totalFee": 5.0` (1 ghante ka minimum charge × ₹5/hr rate).

---

## ✅ Sahi Order Mein Chalao

Sabse best experience ke liye, queries is order mein chalao:

```
Query 1 → Dekho kaun se spots available hain
Query 2 → Kisi gaadi ki history dekho
Query 3 → Abhi kaun andar hai dekho
Query 4 → Naya session start karo (entry) → ID note karo!
Query 5 → Session end karo (exit) → ID use karo jo Query 4 ne diya
```

---

## 🔄 Fresh Data Chahiye? Database Re-seed Karo

Agar database mein bahut saare test sessions aa gaye hain aur clean start chahiye, toh terminal mein yeh command chalao:

```bash
python seed.py
```

Isse sab purana data hat jaata hai aur fresh demo data aa jaata hai. Phir server restart karo:

```bash
uvicorn main:app --reload
```
