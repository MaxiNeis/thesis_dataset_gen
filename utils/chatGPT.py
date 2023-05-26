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

    # answer_example = """- Diamond push-up: I'm going to go over how to do a diamond"""

    # prepend_messages = [
    # {"role": "system", "content": "You are a program that returns bullet points containing relevant data from text."},
    # {"role": "user",
    #     "content": f"Tell me all push-up variations that are explained in detail in the following text as bullet points:\n{full_video_subtitle_block}"},
    # {"role": "assistant", "content": answer_example}
    # ]
    
    # completion = openai.ChatCompletion.create(
    # model="gpt-3.5-turbo",
    # messages=[prepend_messages + {"role": "user", "content": "Tell me all push-up variations that are explained in detail in the following text as bullet points:\n{full_video_subtitle_block}"}])


    # print(completion.choices[0].message.content)
    # save_chatgpt_answer(completion.choices[0].message.content, query_directory)