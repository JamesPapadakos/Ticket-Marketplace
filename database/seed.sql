-- Users 
INSERT INTO users (first_name, last_name, email) 
VALUES
    ('John', 'Smith', 'john@example.com'),
    ('Sarah', 'Johnson', 'sarah@example.com'),
    ('Michael', 'Brown', 'michael@example.com');


-- Venues
INSERT INTO venues (name, city, province, capacity)
VALUES
    ('Scotiabank Arena', 'Toronto', 'Ontario', 19800),
    ('Rogers Centre', 'Toronto', 'Ontario', 39000);


-- Events
INSERT INTO events (venue_id, name, event_type, event_date)
VALUES
    (1, 'Toronto Raptors vs Boston Celtics', 'sports', '2027-01-15 19:30:00-05'),
    (2, 'Toronto Blue Jays vs New York Yankees', 'sports', '2027-05-20 19:00:00-04');

-- Sections 
INSERT INTO sections (venue_id, name)
VALUES
    (1, 'Section 101'),
    (1, 'Section 102'),
    (2, 'Section 120');


-- Seats 
INSERT INTO seats (section_id, row_number, seat_number)
VALUES
    (1, 1, 1),
    (1, 1, 2),
    (1, 1, 3),
    (2, 5, 10),
    (3, 3, 7);


-- Ticket Listings
INSERT INTO ticket_listings (event_id, seat_id, seller_id, price)
VALUES
    (1, 1, 1, 150.00),
    (1, 2, 2, 175.00),
    (1, 3, 3, 200.00),
    (1, 4, 1, 120.00),
    (2, 5, 2, 95.00);


-- Orders 
INSERT INTO orders (buyer_id, total_price, status)
VALUES
    (3, 150.00, 'completed');


-- Order Items 
INSERT INTO order_items (order_id, listing_id, purchase_price)
VALUES
    (1, 1, 150.00);


UPDATE ticket_listings
SET status = 'sold'
WHERE id = 1;