class Question:
    """Question on a questionnaire."""

    def __init__(self, question, choices):
        """Create question"""

        if not choices:
            choices = ["Yes", "No"]

        self.question = question
        self.choices = choices
        


class Survey:
    """Questionnaire."""

    def __init__(self, title, instructions, questions):
        """Create questionnaire."""

        self.title = title
        self.instructions = instructions
        self.questions = questions
        


beer_survey = Survey(
    "Beer Survey",
    "I mean, what else are you doing? It's three questions and maybe you'll learn something.",
    [
        Question("Select a style",
                 ["IPA", "Pale Ale", "Stout", "Lager", "Pilsner"]),
        Question("Select a flavor",
                ["Fruit", "Spice", "Malt", "Chocolate", "Floral"]),
        Question("Select a bitterness level",
        ["No bitter taste", "Mild or noticeable bitterness", "Strong bitterness", "Any level / No preference"])
    ])


survey = {
    "beer": beer_survey,
}
