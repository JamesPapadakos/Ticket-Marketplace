-- Users 
CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- Venues 
CREATE TABLE venues (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    province VARCHAR(100) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);


-- Events
CREATE TABLE events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venue_id BIGINT NOT NULL REFERENCES venues(id), 
    name VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_date TIMESTAMPTZ NOT NULL
);


-- Sections 
CREATE TABLE sections (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venue_id BIGINT NOT NULL REFERENCES venues(id),
    name VARCHAR(50) NOT NULL,
    UNIQUE (venue_id, name),
    UNIQUE (id, venue_id)
);


-- Seats
CREATE TABLE seats (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    section_id BIGINT NOT NULL REFERENCES sections(id),
    row_number INTEGER NOT NULL CHECK (row_number > 0),
    seat_number INTEGER NOT NULL CHECK (seat_number > 0),
    UNIQUE (section_id, row_number, seat_number)
);


-- Ticket Listings 
CREATE TABLE ticket_listings (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id BIGINT NOT NULL REFERENCES events(id),
    seat_id BIGINT NOT NULL REFERENCES seats(id),
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    seller_id BIGINT NOT NULL REFERENCES users(id),
    status VARCHAR(20) NOT NULL DEFAULT 'available',
    CHECK (status IN ('available', 'sold', 'cancelled')),
    listed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- Orders 
CREATE TABLE orders (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    buyer_id BIGINT NOT NULL REFERENCES users(id),
    total_price NUMERIC(12, 2) NOT NULL CHECK (total_price >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    CHECK (status IN ('pending', 'completed', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- Order Items
CREATE TABLE order_items (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    listing_id BIGINT NOT NULL REFERENCES ticket_listings(id),
    purchase_price NUMERIC(10, 2) NOT NULL CHECK (purchase_price >= 0)
);