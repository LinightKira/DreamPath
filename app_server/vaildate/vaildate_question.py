from datetime import datetime


def validate_question_data(data):
    if not data.get('title'):
        return 'title is required'
    if not data.get('q_type'):
        return 'type is required'
    if not data.get('theme_id'):
        return 'theme_id is required'
    return None

