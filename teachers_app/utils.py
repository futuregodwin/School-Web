def convert_to_grade(score):
    """
    Converts a numeric score to an alphabetic grade.
    """
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    elif score >= 40:
        return 'E'
    else:
        return 'F'
