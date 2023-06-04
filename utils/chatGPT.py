import openai

def dialogue_step(persona, msg_history, user_query):
    
    if user_query == "":
        return msg_history

    msg_history.append({"role": "user", "content": user_query})
    query = [{"role": "system", "content": persona}]
    query.extend(msg_history)
    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=query
    )
    gpt_message = result["choices"][0]["message"]
    msg_history.append({"role": gpt_message["role"], "content": gpt_message["content"]})
    print("GPT: " + gpt_message["content"])

    return msg_history
