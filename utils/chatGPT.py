import os
import openai
from tqdm.auto import tqdm

def talk_with(persona, tell_user, ask_user):
    message_history = []
    while True:
        user_input = ask_user()
        if user_input == "":
            return message_history

        message_history.append({"role": "user", "content": user_input})
        query = [{"role": "system", "content": persona}]
        query.extend(message_history)
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=query
        )
        gpt_message = result["choices"][0]["message"]
        message_history.append({"role": gpt_message["role"], "content": gpt_message["content"]})
        tell_user("GPT: " + gpt_message["content"])
