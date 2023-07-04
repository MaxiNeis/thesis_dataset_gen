import openai

class chatGPT(object):
    
    def __init__(self):
        self.message_history = []

    def dialogue_step(persona, user_query):
        
        if user_query == "":
            return self.message_history

        message_history.append({"role": "user", "content": user_query})
        query = [{"role": "system", "content": persona}]
        query.extend(message_history)
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=query
        )
        gpt_message = result["choices"][0]["message"]
        message_history.append({"role": gpt_message["role"], "content": gpt_message["content"]})
        print("GPT: " + gpt_message["content"])

        message_history

    def getResult():
        return 