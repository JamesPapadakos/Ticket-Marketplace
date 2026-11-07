CREATE OR REPLACE FUNCTION purchase_ticket(
    p_listing_id BIGINT,
    p_buyer_id BIGINT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_seller_id BIGINT;
    v_price NUMERIC(10, 2);
    v_order_id BIGINT;
BEGIN
    -- Lock the ticket listing so another transaction cannot purchase it simultaneously.
    SELECT seller_id, price
    INTO v_seller_id, v_price
    FROM ticket_listings
    WHERE id = p_listing_id
      AND status = 'available'
    FOR UPDATE;

    -- Reject missing or unavailable listings.
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Ticket is unavailable';
    END IF;

    -- Prevent users from buying their own tickets.
    IF v_seller_id = p_buyer_id THEN
        RAISE EXCEPTION 'Cannot purchase your own ticket';
    END IF;

    -- Create the order.
    INSERT INTO orders (buyer_id, total_price, status)
    VALUES (p_buyer_id, v_price, 'completed')
    RETURNING id INTO v_order_id;

    -- Record the purchased ticket.
    INSERT INTO order_items (
        order_id,
        listing_id,
        purchase_price
    )
    VALUES (
        v_order_id,
        p_listing_id,
        v_price
    );

    -- Mark the ticket as sold.
    UPDATE ticket_listings
    SET status = 'sold'
    WHERE id = p_listing_id;

    RETURN v_order_id;
END;
$$;