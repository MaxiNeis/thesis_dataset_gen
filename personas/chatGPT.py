import openai

class chatGPT(object):
    
    def __init__(self):
        self.message_history = []
        for dialogue_step in self.instructions:
            self.dialogue_step(self.instructions[dialogue_step]['persona'], self.instructions[dialogue_step]['user_query'])
        # Output as dictionary to have structured data-format
        self.instructions[dialogue_step]['user_query'] = """Now return your findings as a python dictionary where each identified exercise represents a key and the corresponding citations represent its value"""
        self.dialogue_step(self.instructions[dialogue_step]['persona'], self.instructions[dialogue_step]['user_query'])
        # Remove 'What not to do'
        self.instructions[dialogue_step]['user_query'] = """Finally, out of all instructions you cited earlier, remove every sentence that describes what NOT to do and return the updated dictionary"""
        self.dialogue_step(self.instructions[dialogue_step]['persona'], self.instructions[dialogue_step]['user_query'])
        
        
    def dialogue_step(self, persona, user_query):
        if user_query == "":
            return self.message_history

        self.message_history.append({"role": "user", "content": user_query})
        query = [{"role": "system", "content": persona}]
        query.extend(self.message_history)
        result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=query
        )
        gpt_message = result["choices"][0]["message"]
        self.message_history.append({"role": gpt_message["role"], "content": gpt_message["content"]})
        print("GPT: " + gpt_message["content"])
        

    def getResult(self):
        return self.message_history[-1]["content"]