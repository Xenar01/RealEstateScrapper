from fuzzywuzzy import fuzz


def deduplicate(listings):
    unique = []
    for item in listings:
        dup = False
        for u in unique:
            score = fuzz.token_set_ratio(
                f"{item.get('title')}{item.get('price')}{item.get('location')}",
                f"{u.get('title')}{u.get('price')}{u.get('location')}"
            )
            if score > 90:
                dup = True
                break
        if not dup:
            unique.append(item)
    return unique
