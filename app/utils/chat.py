import ollama
import ast
import os
import openai
from openai import OpenAI
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_question(prompt,question):
    return prompt.format(question = question)

class llmchat:
    def __init__(self,model):
        self.api_key = GOOGLE_API_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)

    def chat(self,question):
        response = self.model.generate_content(question)
        return response.text.strip()

    def generate_questions(self,question):
        prompt = f"""
            You are a helpful assistant that rewrites and expands vague or ambiguous user questions.

            Your task is to:

            1. Clarify the original question — rewrite it to be more precise and complete.  
            2. Generate 2 to 3 alternative versions of the questions that express different interpretations or ways someone might ask the same or similar question.  
            3. Return all variations as a list of strings — no explanation, no markdown, no bullet points.

            ### Example

            User question:  
            How does AI work?

            Output:  
            [
                "How does artificial intelligence function in practical applications?",
                "What are the basic working principles behind AI systems?",
                "Can you explain how AI processes data to make decisions?"
            ]

            ### Now answer the following:

            User question:  
            {question}

            Output:
            """

        question = get_question(prompt,question = question)

        questions = self.chat(question)
        try:
            print(questions)
            questions_list = ast.literal_eval(questions)
            return questions_list
        except:
            return []

    def choose_correct_response(self,question,answers,context):
        prompt = """
            You are given a question and a list of candidate answers and context. Your task is to select the single best answer that fully and accurately responds to the question and return that answer only without any formatting

            ## Question:
            {question}

            ## Candidate Answers:
        """
        question = get_question(prompt,question)

        for ind,answer in enumerate(answers):
            question+=f"{ind+1}. {answer}"
        
        question+="\n## Output Format:\nBest Answer: <Paste the best answer exactly as it appears from the list>\n"
        question+="\n## ## Context:\n"
        for con in context:
            question+=f"{con}\n"

        return self.chat(question)
        

    def get_summary_from_ollama(self,paragraph:str)->str:
        prompt = """
                Summarize the following paragraph as briefly as possible :

                "{question}"
        """
        question = get_question(prompt,question = paragraph)
        return self.chat(question)

    def get_keywords_from_ollama(self,paragraph:str)->str:
        try:
            prompt = """
                Extract the keywords from the following paragraph. Do not leave out anything important.

                Return only a JSON array of strings.
                Do not include any explanation, code block, or extra text.
                Example: ["keyword1", "keyword2", "another keyword"]

                Text:
                "{question}"
                """
            question = get_question(prompt,question = paragraph)

            return ast.literal_eval(self.chat(question))#the returned 
        except Exception as e:
            return []

    def get_answer_from_para(self,paragraph:str,question:str)->str:

        prompt = """
            You are a helpful AI assistant. Read the paragraph below and answer the following question based only on the information in the paragraph and dont include anything form outside the para.

            Paragraph:
            {paragraph}

            Question:
            {question}

            Answer:"""

        question = prompt.format(paragraph = paragraph,question=question)

        return self.chat(question)