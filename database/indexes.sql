-- Don't allow duplicate available listings for the same ticket. 
CREATE UNIQUE INDEX unique_available_ticket ON ticket_listings (event_id, seat_id)
WHERE status = 'available';

