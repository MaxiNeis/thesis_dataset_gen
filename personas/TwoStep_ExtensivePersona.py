from utils.chatGPT import *

class TwoStep_TrainerPersona:
  """
    s
  """


  def __init__(self, text):
    CGPT_message_history = []

    CGPT_message_history = dialogue_step(
    persona="""You are a fitness Trainer. Read a given text and return all fitness-exercises that are explained in detail in terms of proper execution. If no fitness-exercises are explained in detail, answer: none. Respond as a list containing the name of the exercise with the form of [Deadlift, Wide-Hands Pushup, Military Press]""",
    #persona="""You are a helpful cooking expert. You answer question by providing a short explanation and a list of easy to follow steps. You list ingredients, tools, and instructions.""",
    msg_history= CGPT_message_history,
    user_query=f"""The given text is: {text}.
    What fitness-exercises in the given text are explained in detail regarding its proper execution? If no fitness-exercises are explained in detail, answer: none. Respond as a list containing one name per exercise, e.g. [Deadlift, Wide-Hands Pushup, Military Press, Diamond Pushup]"""
    )

    # And why it thinks it is explained deeply
    CGPT_message_history = dialogue_step(
    persona="""You are a fitness Trainer. Read a given text and return all fitness-exercises that are explained in detail in terms of proper execution.""",
    #persona="""You are a helpful cooking expert. You answer question by providing a short explanation and a list of easy to follow steps. You list ingredients, tools, and instructions.""",
    msg_history= CGPT_message_history,
    user_query="""If you said None earlier, answer None again. Else: For each fitness-exercise you named, which text passages explain the exercise in terms of its execution? Cite the passages. If you can find them, cite the step-by-step instructions. """
    )

    # # Of the explanation found earlier, if there are passages that describe what NOT to do -> That would mean for the corresponding video segment it would show a wrong execution variant
    # CGPT_message_history = dialogue_step(
    # persona="""You are a fitness Trainer. Read a given text and return all fitness-exercises that are explained in detail in terms of proper execution.""",
    # #persona="""You are a helpful cooking expert. You answer question by providing a short explanation and a list of easy to follow steps. You list ingredients, tools, and instructions.""",
    # msg_history= CGPT_message_history,
    # user_query="""If you said None earlier, answer None again. Else: For each fitness-exercise you named, which text passages explain the exercise in terms of its execution? Cite the passages."""
    # )

    # Group the citations of an exercise as a list, e.g. ["To perform the deadlift you have to adopt a firm stance", "Place your hands about shoulder-wide on the barbell."] and return it alltogether as a python dictionary, meaning the key is the name of the exercise and the value is the respective list.
    #cite the respective passages of the given text that explain only it's proper execution in detail."""

PERSONA = """I want to mine data from Youtube's video subtitles and you will be my helpful assistant. I will give you Youtube-subtitle texts and ask you to idetify fitness  """