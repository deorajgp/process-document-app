import ollama
import ast

def get_question(prompt,question):
    return prompt.format(question = question)

def generate_questions(question,model = 'llama3.2:1b'):
    prompt = """
        You are a helpful assistant that rewrites and expands vague or ambiguous user questions.

        Given the following user question, your task is to:

        1. **Clarify the original question** — rewrite it to be more precise and complete.  
        2. **Generate 2 to 3 alternative versions** that express different interpretations or ways someone might ask the same or similar question.  
        3. Ensure that all variations are useful for retrieving relevant documents or generating better answers.  

        **User question:**  
        {question}
    """
    question = get_question(prompt,question = question)
    response = ollama.chat(
        model = model,
        messages = [
            {'role':'user','content':question}
        ]
    )

    return response["message"]["content"]

def choose_correct_response(question,answers,model = 'llama3.2:1b'):
    prompt = """
        You are given a question and a list of candidate answers. Your task is to select the single best answer that fully and accurately responds to the question.

        ## Question:
        {question}

        ## Candidate Answers:
    """
    question = get_question(prompt,question)

    for ind,answer in enumerate(answers):
        question+=f"{ind+1}. {answer}"
    
    question+="\n## Output Format:\nBest Answer: <Paste the best answer exactly as it appears from the list>\n"
    response = ollama.chat(
        model = model,
        messages=[
            {'role':'user','content':question}
        ]
    )
    return response["message"]["content"]
    

def get_summary_from_ollama(paragraph:str,model='llama3.2:1b')->str:
    prompt = """
            Summarize the following paragraph as briefly as possible :

            "{question}"
    """
    question = get_question(prompt,question = paragraph)
    response = ollama.chat(
        model = model,
        messages=[
            {'role':'user' , 'content':question}
        ]
    )


    return response["message"]["content"]

def get_keywords_from_ollama(paragraph:str,model='llama3.2:1b')->str:
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
        response = ollama.chat(
            model = model,
            messages=[
                {'role':'user' , 'content':question}
            ]
        )

        return ast.literal_eval(response["message"]["content"])#the returned 
    except Exception as e:
        raise e

def get_answer_from_para(paragraph:str,question:str,model = 'llama3.2:1b')->str:

    prompt = """
        You are a helpful AI assistant. Read the paragraph below and answer the following question based only on the information in the paragraph and dont include anything form outside the para.

        Paragraph:
        {paragraph}

        Question:
        {question}

        Answer:"""

    response = ollama.chat(
        model = model,
        messages=[
            {
                'role':'user',
                'content':prompt.format(paragraph = paragraph,question=question)
            }
        ]
    )

    return response['message']['content']