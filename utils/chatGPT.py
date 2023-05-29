import os
import openai
from tqdm.auto import tqdm

def askChatGPT(text, openAI_API_KEY):
    # Feed ChatGPT
    os.environ['OPENAI_API_KEY'] = openAI_API_KEY
    openai.api_key = os.environ['OPENAI_API_KEY']

    answer_example = """- Diamond puh-up
- Wide-hands push-up
- Deadlift """



    prepend_messages = [
    {"role": "system", "content": "You are a program that returns bullet points containing fitness-exercises that are explained in detail in a text."},
    {"role": "user",
        "content": f"Name all fitness exercises that are explained in detail here:\n{text}"},
    {"role": "assistant", "content": answer_example}
    ]
    max_messages_length = 2
    text = [text]
    messages = []
    for i, text in tqdm(enumerate(text)):
        message_user = {
            "role": "user", "content": f"Name all fitness exercises that are explained in detail here:\n{text}"}
        # let's keep only 4 messages max (2 examples)
        messages = messages + [message_user]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prepend_messages + messages[-max_messages_length:],
        )
        message_assistant = response.choices[0].message
        messages += [message_assistant]

    messages[1]['content'].replace("- ", "").split("\n")

    all_answers = []
    for message in messages:
        if message["role"] == "assistant":
            content = message["content"]
            content = content.replace("- ", "")
            data = content.split("\n")
            all_answers += data

    print(all_answers)

