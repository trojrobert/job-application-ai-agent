import sys
import os 
from PyPDF2 import PdfReader

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

from typing import List, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel 

from browser_use import ActionResult, Agent, Browser, Controller

load_dotenv()

controller = Controller()

class Job(BaseModel):
    title: str
    link: str
    company: str
    salary: Optional[str]
    location: Optional[str]
    description: Optional[str]

class Jobs(BaseModel):
    jobs: List[Job]


@controller.action(description="Save jobs to a file", param_model=Jobs)
def save_jobs(jobs: Jobs) -> None:
    with open(file="jobs.csv", mode="a", newline="") as f:
        writer = csv.writer(csvfile=f)
        for job in params.jobs:
            writer.writerow([job.title, job.link, job.company, job.salary, job.location, job.description])

@controller.action(description="Read jobs from a file")
def read_jobs() -> str:
    with open(file="jobs.csv", mode="r") as f:
        return f.read()
    
@controller.action(description="Ask me for help")
def ask_human(question: str) -> str:
    return input(prompt=question)

@controller.action(description="Read my cv for coontext to fill the forms")
def read_cv() -> str:
    pdf = PdfReader(file="cv.pdf")
    text = ""
    for page in pdf.pages: 
        text += page.extract_text() or "" 
    return ActionResult(extracted_context=text, include_in_memory=True)

@controller.action(description="Upload cv to index", requires_browser=True)
async def upload_cv_to_index(index: int, browser: Browser) -> str:
    await close_file_dialog(browser)
    element = await browser.get_element_by_index(index=index)
    my_cv = Path.cwd() / "cv.pdf"
    if not element:
        raise Exception(f"Element with index {index} not found")
    await  element.set_input_files(files=str(object=my_cv.absolute()))
    return f"Uploaded cv to index {index}"

@controller.action(description="Close file dialog ", requires_browser=True)
async def close_file_dialog(browser: Browser) -> None:
    page = await browser.get_current_page()
    await page.keyboard.press(key="Escape")

async def main() -> None:
    task = (
        "Read my cv & find machine learning engineer jobs for me"
        "Save them to a file"
        "then start applying for them in new tabs - please not via job portals like linkedin or indeed"
        "If you need more information for help, ask me"

    )

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = Agent(task=task, llm=model, controller=controller)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main=main())