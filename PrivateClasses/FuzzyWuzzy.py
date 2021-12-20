from Levenshtein import ratio as Ratio


class FuzzyWuzzy:
    def __init__(self, input_string, control_strings):
        self.input_string = input_string.lower()
        self.control_strings = control_strings

    def compare(self):
        best_match = None
        best_ratio = 0
        for control_string in self.control_strings:
            ratio = Ratio(self.input_string, control_string.lower())
            if ratio > best_ratio and ratio > 0.52:
                best_match = control_string
                best_ratio = ratio
        return best_match
