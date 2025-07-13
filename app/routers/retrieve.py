from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.models import DocumentData
from app.utils.chat import llmchat
from app.database import get_db

router = APIRouter(
    prefix = "/retrieve",
    tags = ["retrieval"]
)

#this function gets the data stored in chunk ids order by their chunk_number for continuity
def get_para(chunk_ids:list,db:Session):
    try:
        result = db.query(DocumentData.chunk_content).filter(DocumentData.chunk_id.in_(chunk_ids)).order_by(DocumentData.chunk_number).all()
        return "".join(row[0] for row in result)
    except Exception as e:
        print(e)

#this function gets chunk ids with matching keywords and the no of matched keywords is atleast required_match param
def get_chunk_ids(required_keywords:list , db:Session,role:str ,required_match:int = 1)->list:
    try:
        if role != "manager": #The manager can access any data
            result = db.query(DocumentData.chunk_id, DocumentData.keywords).filter(DocumentData.role==role).all()
        else: #get role specific data
            result = db.query(DocumentData.chunk_id, DocumentData.keywords).all()
        related_chunk_ids = []

        for id,keywords in result:
            match_count = sum(1 for kw in keywords if kw in required_keywords)
            if match_count >= required_match:
                related_chunk_ids.append(id)
        
        return related_chunk_ids
    except Exception as e:
        print(e)

#retriever for the user query
@router.get("/")
def get_answer(question:str,role:str,db:Session = Depends(get_db))->str:
    """
    first generate synonym questions for better retrieval
    then get keywords from the question 
    then get chunk ids from the db relating to the question keywords
    add the chunks context to final context
    add answers to answers list 
    fimmaly compare the answers to the context thus generated
    """
    try:
        llm = llmchat(model="gemini-1.5-pro")
        questions = llm.generate_questions(question)
        questions.append(question)
        answers = []
        context = []
        for question in questions:
            required_keywords = llm.get_keywords_from_ollama(question)
            required_keywords = [keyword.lower() for keyword in required_keywords]
            chunk_ids = get_chunk_ids(required_keywords , db,role = role,required_match=1)
            para = get_para(chunk_ids,db)
            print(para)
            context.append(para)
            result = llm.get_answer_from_para(paragraph=para,question=question)
            answers.append(result)
        
        return llm.choose_correct_response(question,context,answers)
    except Exception as e:
        print(e)
        return "Server Error"

