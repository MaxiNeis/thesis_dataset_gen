import openai
import json
import urllib.error as urllib2
import os

class chatGPT(object):
    message_archive = []
    
    def __init__(self):
        self.message_history = []
        for dialogue_step in self.instructions:
            self.dialogue_step(self.instructions[dialogue_step]['persona'], self.instructions[dialogue_step]['user_query'])
        # Output as dictionary to have structured data-format
        self.message_archive.append(self.message_history[0])
        del self.message_history[0]
        self.instructions[dialogue_step]['user_query'] = """Now return your findings as a python dictionary where each identified exercise represents a key and the corresponding citations represent its value.
                                                            If there are no actual fitness exercises in the dictionary, return an empty dictionary."""
        self.dialogue_step(self.instructions[dialogue_step]['persona'], self.instructions[dialogue_step]['user_query'])
        # Remove 'What not to do'
        self.message_archive.append(self.message_history[0])
        del self.message_history[0]
        self.instructions[dialogue_step]['user_query'] = """Finally, out of all instructions you cited earlier, remove every sentence that describes what NOT to do and return the updated dictionary"""
        self.dialogue_step(self.instructions[dialogue_step]['persona'], self.instructions[dialogue_step]['user_query'])
        
        
    def dialogue_step(self, persona, user_query, try_count=5):
        if user_query == "":
            return self.message_history

        self.message_history.append({"role": "user", "content": user_query})
        query = [{"role": "system", "content": persona}]
        query.extend(self.message_history)
        try:
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=query,
                temperature=0.2
                #temperature=0
            )
        except urllib2.HTTPError as err:
            if str(err.code)[:2] == 50: # 500 error family
                if try_count > 0:
                    return self.dialogue_step(self=self, persona=persona, user_query=user_query, try_count=try_count-1)
                else:
                    raise err

        gpt_message = result["choices"][0]["message"]#.strip("`Python").strip("`python")
        self.message_history.append({"role": gpt_message["role"], "content": gpt_message["content"].strip("`Python").strip("`python")})
        #print("GPT: " + gpt_message["content"].strip("`Python").strip("`python"))
        
    def getResult(self):
        try:
            final_message = self.message_history[-1]["content"]
            final_message_processed = final_message[final_message.find("{"):final_message.rfind("}")+1]
            #rtn = eval(self.message_history[-1]["content"].strip("`Python").strip("`python").replace("\n", ""))
            rtn = eval(final_message_processed.replace("\n", ""))
        except:
            rtn = {}
        return rtn
    
    def saveResult(self, videoID, chatGPT_results_directory):
        if not os.path.exists(chatGPT_results_directory):
                os.makedirs(chatGPT_results_directory)
        with open(f"{chatGPT_results_directory}\\{videoID}.json", "w") as outfile:
            final_message = self.message_history[-1]["content"]
            final_message_processed = final_message[final_message.find("{"):final_message.rfind("}")+1]
            json.dump(final_message_processed.replace("\n", ""), outfile, indent=4)