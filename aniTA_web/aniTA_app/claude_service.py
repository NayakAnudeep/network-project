import os
import json
import base64
import tempfile
import re
import numpy as np
from datetime import datetime
from django.conf import settings
from anthropic import Anthropic
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from users.material_db import (
    get_course_material,
    get_rubric,
    get_material_questions,
    get_vector_embeddings,
    get_similar_chunks,
    store_course_material,
    store_rubric,
    store_material_questions,
    store_vector_embeddings
)
from users.arangodb import db

# Simple function to get a response from Claude
def get_claude_response(prompt, max_tokens=1000):
    """
    Send a prompt to Claude and get a response.
    
    Args:
        prompt: The text prompt to send to Claude
        max_tokens: Maximum number of tokens in the response
        
    Returns:
        The text response from Claude
    """
    try:
        api_key = getattr(settings, 'ANTHROPIC_API_KEY', os.getenv('ANTHROPIC_API_KEY'))
        if not api_key:
            raise ValueError("Anthropic API key is required.")
            
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=max_tokens,
            system="You are a helpful AI assistant for educational content generation.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return f"Error: Could not get response from Claude. {str(e)}"

class ClaudeGradingService:
    def __init__(self, api_key=None):
        self.api_key = api_key or getattr(settings, 'ANTHROPIC_API_KEY', os.getenv('ANTHROPIC_API_KEY'))
        if not self.api_key:
            raise ValueError("Anthropic API key is required.")
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-haiku-20240307"
        self.embeddings_model = None

    def get_embeddings_model(self):
        if self.embeddings_model is None:
            self.embeddings_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        return self.embeddings_model

    def extract_text_from_pdf(self, pdf_path):
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def extract_questions_from_text(self, text):
        pattern = re.compile(r"(Q\d+[:.\s]+)(.*?)(?=\nQ\d+[:.\s]+|$)", re.DOTALL | re.IGNORECASE)
        questions = []
        for i, (_, q) in enumerate(pattern.findall(text)):
            q = q.strip()
            parts = q.split('\n', 1)
            if len(parts) > 1:
                question = parts[0].strip()
                expected_answer = parts[1].strip()
            else:
                question = q
                expected_answer = ""
            questions.append({
                "id": f"Q{i+1}",
                "text": question,
                "expected_answer": expected_answer
            })
        return questions

    def create_text_chunks(self, text, chunk_size=500, chunk_overlap=50):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        return splitter.split_text(text)

    def create_embeddings(self, text_chunks):
        embeddings_model = self.get_embeddings_model()
        embeddings = embeddings_model.embed_documents(text_chunks)
        return [
            {"text": chunk, "embedding": embedding}
            for chunk, embedding in zip(text_chunks, embeddings)
        ]

    def split_into_sections(self, text):
        """
        Split extracted course material into logical sections based on headings.
        """
        pattern = r'\n\d+(\.\d+)*\s+(.+?)\n'
        sections = []
        matches = list(re.finditer(pattern, text))

        for idx, match in enumerate(matches):
            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            title = match.group(0).strip()
            content = text[start:end].strip()

            sections.append({
                "title": title,
                "content": content
            })
        return sections

    def process_course_material(self, class_code, assignment_id, pdf_path, rubric_items=None):
        extracted_text = self.extract_text_from_pdf(pdf_path)
        if not extracted_text:
            return {"error": "Could not extract text from PDF"}

        with open(pdf_path, 'rb') as pdf_file:
            file_content = base64.b64encode(pdf_file.read()).decode('utf-8')

        material_id = store_course_material(
            class_code,
            assignment_id,
            file_content,
            os.path.basename(pdf_path),
            extracted_text
        )

        questions = self.extract_questions_from_text(extracted_text)
        if questions:
            store_material_questions(class_code, assignment_id, questions)

        text_chunks = self.create_text_chunks(extracted_text)
        chunk_data = self.create_embeddings(text_chunks)
        store_vector_embeddings(class_code, assignment_id, chunk_data)

        # 🔥 Store Sections
        sections = self.split_into_sections(extracted_text)
        sections_collection = db.collection('sections')
        for section in sections:
            sections_collection.insert({
                "assignment_id": assignment_id,
                "class_code": class_code,
                "title": section["title"],
                "content": section["content"],
                "created_at": datetime.utcnow().isoformat()
            })

        if rubric_items:
            store_rubric(class_code, assignment_id, rubric_items)

        return {
            "success": True,
            "material_id": material_id,
            "questions_count": len(questions),
            "chunks_count": len(text_chunks),
            "sections_count": len(sections)
        }

    def get_assignment_context(self, class_code, assignment_id, query_text=None):
        context = {
            "material_text": "",
            "questions": [],
            "rubric": None,
            "relevant_chunks": []
        }

        material = get_course_material(class_code, assignment_id)
        if material:
            context["material_text"] = material.get("extracted_text", "")

        questions = get_material_questions(class_code, assignment_id)
        if questions:
            context["questions"] = questions

        rubric = get_rubric(class_code, assignment_id)
        if rubric:
            context["rubric"] = rubric.get("items", [])

        if query_text and context["material_text"]:
            embeddings_model = self.get_embeddings_model()
            query_embedding = embeddings_model.embed_documents([query_text])[0]

            similar_chunks = get_similar_chunks(
                class_code,
                assignment_id,
                query_embedding
            )

            if similar_chunks:
                context["relevant_chunks"] = [chunk["text"] for chunk in similar_chunks]

        return context

    def match_student_answers(self, student_text, questions):
        answers = []
        for i, question in enumerate(questions):
            q_text = question["text"]
            q_id = question["id"]

            index = student_text.find(q_text)
            if index == -1:
                index = student_text.find(q_id)
                if index == -1:
                    answers.append({
                        "question_id": q_id,
                        "question_text": q_text,
                        "student_answer": ""
                    })
                    continue

            start = index + len(q_text)
            next_q = None

            if i + 1 < len(questions):
                next_q_text = questions[i+1]["text"]
                next_q_id = questions[i+1]["id"]
                next_index = student_text.find(next_q_text, start)
                if next_index == -1:
                    next_index = student_text.find(next_q_id, start)
                next_q = next_index if next_index != -1 else None

            end = next_q if next_q is not None else len(student_text)
            answer = student_text[start:end].strip()

            answers.append({
                "question_id": q_id,
                "question_text": q_text,
                "student_answer": answer
            })
        return answers

    def grade_submission(self, student_text, context, class_code, assignment_id):
        questions = context.get("questions", [])
        matched_answers = self.match_student_answers(student_text, questions)

        rubric_text = ""
        rubric_items = context.get("rubric", [])
        if rubric_items:
            rubric_text = "Grading Rubric:\n"
            for item in rubric_items:
                criteria = item.get("criteria", "")
                points = item.get("points", 0)
                description = item.get("description", "")
                rubric_text += f"- {criteria} ({points} points): {description}\n"

        relevant_context = ""
        relevant_chunks = context.get("relevant_chunks", [])
        if relevant_chunks:
            relevant_context = "Relevant Course Material:\n" + "\n---\n".join(relevant_chunks)

        system_prompt = """
        You are an AI teaching assistant that grades student submissions according to rubrics.
        
        Follow these guidelines:
        1. Grade each answer based on the provided rubric criteria
        2. Provide actionable feedback
        3. Format your response as valid JSON
        """

        user_prompt = f"""
        Class: {class_code}
        Assignment: {assignment_id}
        
        {rubric_text}
        
        {relevant_context}
        
        Student Submission:
        {student_text}
        
        Matched Answers:
        {matched_answers}
        """

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            content = response.content[0].text

            import re
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                json_str = json_match.group(1) if json_match else content

            result = json.loads(json_str)
            return {
                "student_id": "",
                "assignment_id": assignment_id,
                "total_score": result.get("total_score", 0.0),
                "results": result.get("results", []),
                "relevant_chunks": context.get("relevant_chunks", [])
            }

        except Exception as e:
            print(f"Error during grading with Claude: {e}")
            return {
                "error": str(e),
                "student_id": "",
                "assignment_id": assignment_id,
                "total_score": 0.0,
                "results": []
            }

    def grade_from_pdf_data(self, student_pdf_path, class_code, assignment_id):
        student_text = self.extract_text_from_pdf(student_pdf_path)
        if not student_text:
            return {
                "error": "Could not extract text from student PDF",
                "student_id": "",
                "assignment_id": assignment_id,
                "total_score": 0.0,
                "results": []
            }
        context = self.get_assignment_context(class_code, assignment_id, student_text)
        return self.grade_submission(student_text, context, class_code, assignment_id)
