def increment_seat_order(idx, seat_pool):
    try:
        next_organization = seat_pool[idx+1]
    except IndexError:
        next_organization = seat_pool[0]
    return next_organization