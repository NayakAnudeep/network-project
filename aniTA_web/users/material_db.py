"""
Database functions for course materials, rubrics, and vector embeddings.

This module provides functions for storing and retrieving course materials,
rubrics, and vector embeddings in ArangoDB.
"""

from datetime import datetime
import json
import base64
import tempfile
import numpy as np
from .arangodb import db

def store_course_material(class_code, assignment_id, file_content, file_name, extracted_text):
    """
    Store course material in ArangoDB.
    
    Args:
        class_code (str): The class code
        assignment_id (str): The assignment ID
        file_content (str): Base64-encoded file content
        file_name (str): The file name
        extracted_text (str): Text extracted from the file
        
    Returns:
        str: Material ID if successful, None otherwise
    """
    try:
        # Store the material
        materials = db.collection('course_materials')
        material = {
            "class_code": class_code,
            "assignment_id": assignment_id,
            "file_name": file_name,
            "file_content": file_content,
            "extracted_text": extracted_text,
            "created_at": datetime.now().isoformat()
        }
        
        # Check if material already exists for this assignment
        existing = list(materials.find({
            "class_code": class_code,
            "assignment_id": assignment_id
        }))
        
        if existing:
            # Update existing material
            existing_doc = existing[0]
            existing_doc.update(material)
            materials.update(existing_doc)
            return existing_doc["_id"]
        else:
            # Insert new material
            result = materials.insert(material)
            return result["_id"]
            
    except Exception as e:
        print(f"Error storing course material: {e}")
        return None

def store_rubric(class_code, assignment_id, rubric_items):
    """
    Store rubric in ArangoDB.
    
    Args:
        class_code (str): The class code
        assignment_id (str): The assignment ID
        rubric_items (list): List of rubric items
        
    Returns:
        str: Rubric ID if successful, None otherwise
    """
    try:
        # Store the rubric
        rubrics = db.collection('rubrics')
        rubric = {
            "class_code": class_code,
            "assignment_id": assignment_id,
            "items": rubric_items,
            "created_at": datetime.now().isoformat()
        }
        
        # Check if rubric already exists for this assignment
        existing = list(rubrics.find({
            "class_code": class_code,
            "assignment_id": assignment_id
        }))
        
        if existing:
            # Update existing rubric
            existing_doc = existing[0]
            existing_doc.update(rubric)
            rubrics.update(existing_doc)
            return existing_doc["_id"]
        else:
            # Insert new rubric
            result = rubrics.insert(rubric)
            return result["_id"]
            
    except Exception as e:
        print(f"Error storing rubric: {e}")
        return None

def store_material_questions(class_code, assignment_id, questions):
    """
    Store questions extracted from course material.
    
    Args:
        class_code (str): The class code
        assignment_id (str): The assignment ID
        questions (list): List of questions extracted from the material
        
    Returns:
        str: Questions ID if successful, None otherwise
    """
    try:
        # Store the questions
        material_questions = db.collection('material_questions')
        question_doc = {
            "class_code": class_code,
            "assignment_id": assignment_id,
            "questions": questions,
            "created_at": datetime.now().isoformat()
        }
        
        # Check if questions already exist for this assignment
        existing = list(material_questions.find({
            "class_code": class_code,
            "assignment_id": assignment_id
        }))
        
        if existing:
            # Update existing questions
            existing_doc = existing[0]
            existing_doc.update(question_doc)
            material_questions.update(existing_doc)
            return existing_doc["_id"]
        else:
            # Insert new questions
            result = material_questions.insert(question_doc)
            return result["_id"]
            
    except Exception as e:
        print(f"Error storing material questions: {e}")
        return None

def store_vector_embeddings(class_code, assignment_id, chunk_data):
    """
    Store vector embeddings in ArangoDB.
    
    Args:
        class_code (str): The class code
        assignment_id (str): The assignment ID
        chunk_data (list): List of dictionaries with text chunks and embeddings
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Store the vector embeddings
        vectors = db.collection('material_vectors')
        
        # Delete existing vectors for this assignment
        existing_query = f"""
        FOR v IN material_vectors
            FILTER v.class_code == "{class_code}" AND v.assignment_id == "{assignment_id}"
            REMOVE v IN material_vectors
        """
        db.aql.execute(existing_query)
        
        # Insert new vectors
        for i, chunk in enumerate(chunk_data):
            vector_doc = {
                "class_code": class_code,
                "assignment_id": assignment_id,
                "chunk_id": i,
                "text": chunk["text"],
                "embedding": chunk["embedding"].tolist() if isinstance(chunk["embedding"], np.ndarray) else chunk["embedding"],
                "created_at": datetime.now().isoformat()
            }
            vectors.insert(vector_doc)
            
        return True
            
    except Exception as e:
        print(f"Error storing vector embeddings: {e}")
        return False

def get_course_material(class_code, assignment_id):
    """
    Get course material from ArangoDB.
    
    Args:
        class_code (str): The class code
        assignment_id (str): The assignment ID
        
    Returns:
        dict: Course material document if found, None otherwise
    """
    try:
        materials = db.collection('course_materials')
        material_list = list(materials.find({
            "class_code": class_code,
            "assignment_id": assignment_id
        }))
        
        if material_list:
            return material_list[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error retrieving course material: {e}")
        return None

def get_rubric(class_code, assignment_id):
    """
    Get rubric from ArangoDB.
    
    Args:
        class_code (str): The class code
        assignment_id (str): The assignment ID
        
    Returns:
        dict: Rubric document if found, None otherwise
    """
    try:
        rubrics = db.collection('rubrics')
        rubric_list = list(rubrics.find({
            "class_code": class_code,
            "assignment_id": assignment_id
        }))
        
        if rubric_list:
            return rubric_list[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error retrieving rubric: {e}")
        return None

def get_material_questions(class_code, assignment_id):
    """
    Get questions extracted from course material.
    
    Args:
        class_code (str): The class code
        assignment_id (str): The assignment ID
        
    Returns:
        list: List of questions if found, None otherwise
    """
    try:
        material_questions = db.collection('material_questions')
        question_list = list(material_questions.find({
            "class_code": class_code,
            "assignment_id": assignment_id
        }))
        
        if question_list:
            return question_list[0]["questions"]
        else:
            return None
            
    except Exception as e:
        print(f"Error retrieving material questions: {e}")
        return None

def get_vector_embeddings(class_code, assignment_id):
    """
    Get vector embeddings from ArangoDB.
    
    Args:
        class_code (str): The class code
        assignment_id (str): The assignment ID
        
    Returns:
        list: List of vector embedding documents if found, empty list otherwise
    """
    try:
        vectors = db.collection('material_vectors')
        vector_list = list(vectors.find({
            "class_code": class_code,
            "assignment_id": assignment_id
        }))
        
        return vector_list
            
    except Exception as e:
        print(f"Error retrieving vector embeddings: {e}")
        return []

def get_similar_chunks(class_code, assignment_id, query_embedding, top_k=3):
    """
    Get similar chunks using vector search.
    This is a placeholder - in a real implementation, you would use ArangoDB's
    vector search capabilities or implement cosine similarity.
    
    Args:
        class_code (str): The class code
        assignment_id (str): The assignment ID
        query_embedding (list): Query embedding
        top_k (int): Number of top results to return
        
    Returns:
        list: List of similar chunks if found, empty list otherwise
    """
    try:
        vector_docs = get_vector_embeddings(class_code, assignment_id)
        
        if not vector_docs:
            return []
            
        # Convert query embedding to numpy array for calculations
        query_embedding_np = np.array(query_embedding)
        
        # Calculate cosine similarity for each vector
        results = []
        for doc in vector_docs:
            # Convert stored embedding back to numpy array
            doc_embedding = np.array(doc["embedding"])
            
            # Calculate cosine similarity
            similarity = np.dot(query_embedding_np, doc_embedding) / (
                np.linalg.norm(query_embedding_np) * np.linalg.norm(doc_embedding)
            )
            
            results.append({
                "chunk_id": doc["chunk_id"],
                "text": doc["text"],
                "similarity": float(similarity)
            })
        
        # Sort by similarity (highest first) and take top k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
            
    except Exception as e:
        print(f"Error performing vector search: {e}")
        return []
