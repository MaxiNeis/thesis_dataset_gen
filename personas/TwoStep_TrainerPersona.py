from personas.chatGPT import *

class TwoStep_TrainerPersona(chatGPT):
  """
  - Too imprecise.
  - Example result: "Dip": [
        "now I can guarantee that there is no better exercise for building the triceps",
        "because you know what they say a man who loves dips loves your mum's big voluptuous"
        => Does not explain the exercise
        => Increase preciseness of exercise selection in first step
  """
  def __init__(self, text):
    
    CGPT_message_history = self.dialogue_step(
    persona="""You are a fitness Trainer. Read a given text and return all fitness-exercises that are explained in detail in terms of proper execution. If no fitness-exercises are explained in detail, answer: none. Respond as a list containing the name of the exercise with the form of [Deadlift, Wide-Hands Pushup, Military Press]""",
    #persona="""You are a helpful cooking expert. You answer question by providing a short explanation and a list of easy to follow steps. You list ingredients, tools, and instructions.""",
    msg_history= CGPT_message_history,
    user_query=f"""The given text is: {text}.
    What fitness-exercises in the given text are explained in detail regarding its proper execution? If no fitness-exercises are explained in detail, answer: none. Respond as a list containing one name per exercise, e.g. [Deadlift, Wide-Hands Pushup, Military Press, Diamond Pushup]"""
    )

    # And why it thinks it is explained deeply
    CGPT_message_history = self.dialogue_step(
    persona="""You are a fitness Trainer. Read a given text and return all fitness-exercises that are explained in detail in terms of proper execution.""",
    #persona="""You are a helpful cooking expert. You answer question by providing a short explanation and a list of easy to follow steps. You list ingredients, tools, and instructions.""",
    msg_history= CGPT_message_history,
    user_query="""If you said None earlier, answer None again. Else: For each fitness-exercise you named, which text passages explain the exercise in terms of its execution? Cite the passages."""
    )

    # Group the citations of an exercise as a list, e.g. ["To perform the deadlift you have to adopt a firm stance", "Place your hands about shoulder-wide on the barbell."] and return it alltogether as a python dictionary, meaning the key is the name of the exercise and the value is the respective list.
    #cite the respective passages of the given text that explain only it's proper execution in detail."""