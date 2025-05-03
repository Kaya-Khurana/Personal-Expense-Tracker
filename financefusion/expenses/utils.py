def categorize_expense(description):
    keywords = {
        'groceries': ['walmart', 'supermarket', 'grocery'],
        'entertainment': ['movie', 'concert', 'netflix'],
        'utilities': ['electricity', 'water', 'gas'],
        'transport': ['uber', 'taxi', 'bus', 'metro'],
        'food': ['restaurant', 'cafe', 'dine'],
        'other': []
    }

    for category, words in keywords.items():
        if any(word in description.lower() for word in words):
            return category
    return 'other'
