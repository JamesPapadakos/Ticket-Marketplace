from fastapi import FastAPI

from backend.database import get_connection

app = FastAPI(
    title="Ticket Marketplace API",
    description="A PostgreSQL-backed event ticket marketplace.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Ticket Marketplace API is running"
    }


@app.get("/events")
def get_events():
    """Return upcoming events from PostgreSQL."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    e.id,
                    e.name,
                    e.event_type,
                    e.event_date,
                    v.name AS venue,
                    v.city
                FROM events e
                JOIN venues v ON e.venue_id = v.id
                WHERE e.event_date >= NOW()
                ORDER BY e.event_date
                LIMIT 50
                """
            )

            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "event_type": row[2],
            "event_date": row[3],
            "venue": row[4],
            "city": row[5],
        }
        for row in rows
    ]
