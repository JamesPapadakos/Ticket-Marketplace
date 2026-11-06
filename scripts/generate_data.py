import os 
import random

import psycopg
from dotenv import load_dotenv
from faker import Faker

load_dotenv()

fake = Faker()
Faker.seed(42)
random.seed(42)

def connect_db():
    """Connect to the PostgreSQL database."""
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def generate_users(conn, count=1000): 
    """Generate fictional users."""
    users = []
    used_emails = set()
    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        while True:
            email = fake.unique.email()
            if email not in used_emails:
                used_emails.add(email)
                break
        users.append((first_name, last_name, email))
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO users (first_name, last_name, email)
            VALUES (%s, %s, %s)
            """,
            users,
        )
    print(f"Generated {count} users.")

def generate_venues(conn, count=30):
    """Generate fictional venues."""
    cities = [
        ("Toronto", "Ontario"),
        ("Ottawa", "Ontario"),
        ("Montreal", "Quebec"),
        ("Vancouver", "British Columbia"),
        ("Calgary", "Alberta"),
        ("Edmonton", "Alberta"),
        ("Winnipeg", "Manitoba"),
    ]
    venues = []
    for i in range(count):
        city, province = random.choice(cities)
        venue_name = f"{fake.company()} Arena {i+1}"
        capacity = random.randint(5000, 50000)
        venues.append((venue_name, city, province, capacity))
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO venues (name, city, province, capacity)
            VALUES (%s, %s, %s, %s)
            """,
            venues,
        )
    print(f"Generated {count} venues.")

def generate_events(conn, count=300):
    """Generate fictional events associated with existing venues."""
    with conn.cursor() as cur: 
        cur.execute("SELECT id FROM venues")
        venue_ids = [row[0] for row in cur.fetchall()]

    event_names = [
        ("Basketball Championship", "Sports"),
        ("Hockey Game", "sports"),
        ("Baseball Game", "sports"),
        ("Summer Music Festival", "concert"),
        ("Rock Concert", "concert"),
        ("Comedy Night", "comedy"),
        ("Stand-Up Comedy Show", "comedy"),
        ("Pop Music Tour", "concert"),
    ]

    events = []
    for _ in range(count):
        venue_id = random.choice(venue_ids)
        name, event_type = random.choice(event_names)
        event_date = fake.future_datetime(end_date="+2y")
        events.append((venue_id, name, event_type, event_date))

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO events (venue_id, name, event_type, event_date)
            VALUES (%s, %s, %s, %s)
            """,
            events,
        )
    print(f"Generated {count} events.")


def generate_sections(conn):
    """Generate five sections for each venue."""
    with conn.cursor() as cur: 
        cur.execute("SELECT id FROM venues")
        venue_ids = [row[0] for row in cur.fetchall()]

    sections = []
    for venue_id in venue_ids:
        for section_number in range(101, 106): 
            sections.append(
                (venue_id, f"Section {section_number}")
            )

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO sections (venue_id, name)
            VALUES (%s, %s)
            ON CONFLICT (venue_id, name) DO NOTHING
            """,
            sections,
        )
    print ("Generated missing venue sections.")


def generate_seats(conn):
    """Generate seats for every section."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM sections")
        section_ids = [row[0] for row in cur.fetchall()]

    seats = []

    for section_id in section_ids:
        for row_number in range(1, 11):
            for seat_number in range(1, 16):
                seats.append(
                    (section_id, row_number, seat_number)
                )

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO seats (section_id, row_number, seat_number)
            VALUES (%s, %s, %s)
            ON CONFLICT (section_id, row_number, seat_number)
            DO NOTHING
            """,
            seats,
        )

    print("Generated missing seats.")


def generate_listings(conn, count=8000):
    """Generate ticket listings for valid event-seat combinations."""

    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cur.fetchall()]

        # Find seats belonging to the event's venue.
        # Exclude seats that already have a listing.
        cur.execute("""
            SELECT e.id, s.id
            FROM events e
            JOIN sections sec ON sec.venue_id = e.venue_id
            JOIN seats s ON s.section_id = sec.id
            WHERE NOT EXISTS (
                SELECT 1
                FROM ticket_listings tl
                WHERE tl.event_id = e.id
                  AND tl.seat_id = s.id
            )
        """)

        available_pairs = cur.fetchall()

        if not user_ids:
            raise ValueError("No users found.")

        if len(available_pairs) < count:
            raise ValueError("Not enough available event-seat pairs.")

        selected_pairs = random.sample(available_pairs, count)

        listings = []

        for event_id, seat_id in selected_pairs:
            seller_id = random.choice(user_ids)
            price = round(random.uniform(40, 500), 2)

            listings.append((
                event_id,
                seat_id,
                seller_id,
                price,
            ))

        cur.executemany(
            """
            INSERT INTO ticket_listings
                (event_id, seat_id, seller_id, price)
            VALUES (%s, %s, %s, %s)
            """,
            listings,
        )

    print(f"Generated {count} ticket listings.")


def generate_orders(conn, count=3000):
    """Generate fictional purchases from available listings."""

    with conn.cursor() as cur:
        # Retrieve available listings and their sellers.
        cur.execute("""
            SELECT id, seller_id, price
            FROM ticket_listings
            WHERE status = 'available'
        """)
        available_listings = cur.fetchall()

        cur.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cur.fetchall()]

        if len(available_listings) < count:
            raise ValueError("Not enough available listings.")

        # Select distinct listings to purchase.
        selected = random.sample(available_listings, count)

        for listing_id, seller_id, price in selected:
            # Buyer cannot purchase their own listing.
            possible_buyers = [
                user_id for user_id in user_ids
                if user_id != seller_id
            ]

            buyer_id = random.choice(possible_buyers)

            # Create an order and retrieve its ID.
            cur.execute(
                """
                INSERT INTO orders
                    (buyer_id, total_price, status)
                VALUES (%s, %s, 'completed')
                RETURNING id
                """,
                (buyer_id, price),
            )

            order_id = cur.fetchone()[0]

            # Record the ticket purchased.
            cur.execute(
                """
                INSERT INTO order_items
                    (order_id, listing_id, purchase_price)
                VALUES (%s, %s, %s)
                """,
                (order_id, listing_id, price),
            )

            # Update the ticket's status.
            cur.execute(
                """
                UPDATE ticket_listings
                SET status = 'sold'
                WHERE id = %s
                """,
                (listing_id,),
            )

    print(f"Generated {count} completed orders.")


def main():
    with connect_db() as conn:
        generate_orders(conn)
    print("Completed orders generated successfully.")

if __name__ == "__main__":
    main()