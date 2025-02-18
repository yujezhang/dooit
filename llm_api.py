import streamlit as st
import os
from typing import List

from langchain_community.llms import OpenAI
from langchain_core.prompts import PromptTemplate  
from langchain_core.runnables import RunnableSequence  
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator


os.environ['OPENAI_API_KEY'] = st.secrets['api_key']

# Initialize LLM
llm = OpenAI(temperature=0.5)

# Parse job
class JobReason(BaseModel):
    job: str = Field(description='name of the job')
    reason: str = Field(description='why suggest this job')
class JobPrediction(BaseModel):
    job_prediction: List[JobReason] = Field(description="list of jobs")

JobPrediction.model_json_schema = classmethod(lambda cls: cls.schema())

# Parse talent
class TalentReason(BaseModel):
    talent: str = Field(description='name of the employee')
    reason: str = Field(description='why choose this employee')
class TalentSearch(BaseModel):
    talent_search: List[TalentReason] = Field(description='list of talents')
    
TalentSearch.model_json_schema = classmethod(lambda cls: cls.schema())

def job_predict(emp_data):
    hardskill = emp_data['HardSkill']
    softskill = emp_data['SoftSkill']
    
    parser = JsonOutputParser(pydantic_object=JobPrediction)
    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    prompt_and_model = prompt | llm
    output = prompt_and_model.invoke({"query": f"My employee individual has hardskill: {hardskill} and has softskill: {softskill}, suggest 3 roles for this employee and give me reason, call this employee 'this person'"})
    result = parser.invoke(output)

    return result

def talent_search(req, emps):
    parser = JsonOutputParser(pydantic_object=TalentSearch)
    prompt = PromptTemplate(
        partial_variables={"format_instructions": parser.get_format_instructions()},
        input_variables=['req', 'emps'],
        template="Answer the user query.\n{format_instructions}\n{query}\n"
    )
    prompt_and_model = prompt | llm
    output = prompt_and_model.invoke({"query": f"here are my employees:{emps}\nwhat are 5 best candidates who are good at:{req}, give me reason for each in 40 words"})
    result = parser.invoke(output)

    return result