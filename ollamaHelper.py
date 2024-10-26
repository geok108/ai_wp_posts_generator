import requests
import json
import ollama

class OllamaHelper:
    def __init__(self):
        print("here")

    def ChatOllama(self, prompt):

        # prompt = "You are an english sports journalist, an expert in football predictions and an expert in article writing. Write a prediction article about the upcoming soccer match between Leicester and Nottingham Forest. \nInclude:\n- a paragraph about Leicester went same to 14 with 9, its form which is DDLWW without mentioning the code, average goals for Leicester goals scored in home 1.0, goals scored away 2.0, goals against in home1.0, goals against away 2.5\n- a paragraph about Nottingham Forest went same to 8 with 13, its form which is WDLDW without mentioning the code, average goals for Nottingham Forest goals scored in home 0.8, goals scored away 1.3, goals against in home0.8, goals against away 0.8\n- a paragraph about head to head between the 2 teams which is: Leicester wins: 3, Nottingham Forest wins: 3, draws: 6. don't mention number just the general picture, and also the prediction and odds based on online search and the information mentioned above\n"
        

        stream = ollama.chat(
            model='qwen2.5',
            messages=[{'role': 'user', 'content': prompt}],
            stream=False,
        )

        return stream['message']['content'] 