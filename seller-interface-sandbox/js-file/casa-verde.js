/* Casa Verde · synthetic public merchant data · research only */
export const merchant = Object.freeze({
  "schema_version": "0.2",
  "data_version": "casa-verde-v0-2026-11-17",
  "merchant_id": "casa-verde-hk-demo",
  "demo_only": true,
  "name": "Casa Verde",
  "tagline": "Neighbourhood Italian Kitchen",
  "description": "A fictional Italian neighbourhood restaurant known for creamy pasta, wood-fired pizza and accessible sharing plates. All facts are synthetic.",
  "cuisine": "Italian",
  "address": {
    "english": "1/F, 26 Fern Passage, Sheung Wan, Hong Kong",
    "chinese": "香港上環蕨葉巷26號1樓",
    "fictional": true,
    "country": "Hong Kong"
  },
  "phone": "+852 0000 0000",
  "phone_is_user_supplied_demo": false,
  "timezone": "Asia/Hong_Kong",
  "currency": "USD",
  "average_price_per_person": 62,
  "price_note": "Demo menu in USD; prices exclude tax and gratuity.",
  "opening_hours": {
    "monday": "17:00-22:00",
    "tuesday": "17:00-22:00",
    "wednesday": "17:00-22:00",
    "thursday": "17:00-22:00",
    "friday": "17:00-23:00",
    "saturday": "17:00-23:00",
    "sunday": "17:00-21:00"
  },
  "amenities": {
    "indoor_seating": true,
    "outdoor_seating": true,
    "vegetarian_options": true
  },
  "reservation_policy": {
    "demo_only": true,
    "party_size_min": 2,
    "party_size_max": 6,
    "cancel_at_least_hours_before": 2,
    "real_booking_supported": false,
    "payments_supported": false
  },
  "menu": [
    {
      "id": "verde_01",
      "name": "Tomato & Whipped Ricotta",
      "description": "Sweet tomatoes, basil oil, whipped ricotta, sourdough.",
      "category": "Starters",
      "price": 18,
      "dietary_note": "Vegetarian"
    },
    {
      "id": "verde_02",
      "name": "Truffle Mushroom Pappardelle",
      "description": "Wild mushrooms, black truffle cream, parmesan, broad ribbons.",
      "category": "Pasta",
      "price": 32,
      "dietary_note": "Vegetarian"
    },
    {
      "id": "verde_03",
      "name": "Four Cheese Pizza",
      "description": "Mozzarella, gorgonzola, fontina, parmesan, thyme.",
      "category": "Pizza",
      "price": 25,
      "dietary_note": "Vegetarian"
    },
    {
      "id": "verde_04",
      "name": "Lemon Ricotta Gnocchi",
      "description": "Soft potato gnocchi, lemon, ricotta, toasted sage.",
      "category": "Pasta",
      "price": 26,
      "dietary_note": "Vegetarian"
    },
    {
      "id": "verde_05",
      "name": "Herb-Roasted Chicken",
      "description": "Garlic herb jus, roast potatoes, seasonal greens.",
      "category": "Mains",
      "price": 33,
      "dietary_note": "Gluten-free option"
    },
    {
      "id": "verde_06",
      "name": "Vanilla Panna Cotta",
      "description": "Soft-set vanilla cream, roasted berries.",
      "category": "Dessert",
      "price": 12,
      "dietary_note": "Vegetarian"
    }
  ],
  "availability": [
    {
      "date": "2026-12-04",
      "time": "18:00",
      "seating": "indoor",
      "max_party_size": 6,
      "status": "available"
    },
    {
      "date": "2026-12-04",
      "time": "18:30",
      "seating": "outdoor",
      "max_party_size": 4,
      "status": "available"
    },
    {
      "date": "2026-12-04",
      "time": "18:30",
      "seating": "indoor",
      "max_party_size": 8,
      "status": "available"
    },
    {
      "date": "2026-12-04",
      "time": "19:00",
      "seating": "outdoor",
      "max_party_size": 0,
      "status": "fully_booked"
    },
    {
      "date": "2026-12-04",
      "time": "19:00",
      "seating": "indoor",
      "max_party_size": 2,
      "status": "available"
    },
    {
      "date": "2026-12-04",
      "time": "19:30",
      "seating": "indoor",
      "max_party_size": 4,
      "status": "available"
    },
    {
      "date": "2026-12-04",
      "time": "20:00",
      "seating": "outdoor",
      "max_party_size": 6,
      "status": "available"
    },
    {
      "date": "2026-12-04",
      "time": "20:00",
      "seating": "indoor",
      "max_party_size": 6,
      "status": "available"
    },
    {
      "date": "2026-12-05",
      "time": "17:30",
      "seating": "outdoor",
      "max_party_size": 2,
      "status": "available"
    },
    {
      "date": "2026-12-05",
      "time": "18:30",
      "seating": "outdoor",
      "max_party_size": 4,
      "status": "available"
    },
    {
      "date": "2026-12-05",
      "time": "19:00",
      "seating": "outdoor",
      "max_party_size": 0,
      "status": "fully_booked"
    },
    {
      "date": "2026-12-05",
      "time": "19:00",
      "seating": "indoor",
      "max_party_size": 6,
      "status": "available"
    },
    {
      "date": "2026-12-05",
      "time": "20:30",
      "seating": "indoor",
      "max_party_size": 6,
      "status": "available"
    },
    {
      "date": "2026-12-06",
      "time": "18:30",
      "seating": "outdoor",
      "max_party_size": 6,
      "status": "available"
    },
    {
      "date": "2026-12-06",
      "time": "19:00",
      "seating": "outdoor",
      "max_party_size": 6,
      "status": "available"
    },
    {
      "date": "2026-12-06",
      "time": "19:00",
      "seating": "indoor",
      "max_party_size": 6,
      "status": "available"
    }
  ],
  "data_freshness": "static_fixed_demo_snapshot",
  "notes": [
    "The address is fictional.",
    "This is not a real restaurant reservation system.",
    "The listed phone is user-supplied demo contact data.",
    "The sample availability covers Dec 4–6, 2026 only."
  ]
});
export default merchant;
