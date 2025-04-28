"""
Graph analysis functions for the knowledge graph.

This module provides functions to analyze the knowledge graph data
using various network analysis algorithms.
"""

import networkx as nx
import numpy as np
from users.arangodb import db
from collections import defaultdict
# Handle community detection with fallback
try:
    import community as community_louvain
except ImportError:
    # Fallback for Louvain community detection
    community_louvain = None
import itertools
import json

def build_mistake_similarity_graph():
    """
    Build a graph of mistakes where edges represent similarity.
    Uses Jaccard similarity to determine if two mistakes are related.
    
    Returns:
        networkx.Graph: Graph with mistakes as nodes and similarity as edges
    """
    try:
        # Get all mistakes
        mistakes = list(db.collection('mistakes').all())
        if not mistakes:
            return nx.Graph()
            
        G = nx.Graph()
        
        # Add nodes
        for mistake in mistakes:
            G.add_node(mistake['_id'], 
                       id=mistake['_id'],
                       label=mistake.get('question', 'Unknown'),
                       score=mistake.get('score_awarded', 0),
                       criteria=mistake.get('rubric_criteria_names', []))
        
        # Calculate Jaccard similarity between mistakes
        for i, m1 in enumerate(mistakes):
            criteria1 = set(m1.get('rubric_criteria_names', []))
            if not criteria1:
                continue
                
            for j, m2 in enumerate(mistakes[i+1:], i+1):
                criteria2 = set(m2.get('rubric_criteria_names', []))
                if not criteria2:
                    continue
                
                # Calculate Jaccard similarity: |intersection| / |union|
                similarity = len(criteria1.intersection(criteria2)) / len(criteria1.union(criteria2))
                
                # Add edge if similarity is above threshold
                if similarity > 0.3:  # Threshold can be adjusted
                    G.add_edge(m1['_id'], m2['_id'], weight=similarity)
        
        return G
    except Exception as e:
        print(f"Error building similarity graph: {e}")
        return nx.Graph()

def get_louvain_clusters(G=None):
    """
    Use Louvain community detection to cluster mistakes.
    
    Args:
        G (networkx.Graph, optional): Graph to analyze. If None, builds a new one.
    
    Returns:
        dict: Dictionary of community assignments
    """
    if G is None:
        G = build_mistake_similarity_graph()
    
    if len(G.nodes) == 0:
        return {}
    
    # Check if community_louvain module is available
    if community_louvain is None:
        # Fallback: use simple connected components as communities
        communities = {}
        for i, component in enumerate(nx.connected_components(G)):
            for node in component:
                communities[node] = i
        return communities
        
    # Run Louvain algorithm if available
    partition = community_louvain.best_partition(G)
    return partition

def get_pagerank_scores(G=None):
    """
    Calculate PageRank for each mistake to identify the most critical ones.
    
    Args:
        G (networkx.Graph, optional): Graph to analyze. If None, builds a new one.
    
    Returns:
        dict: Dictionary of PageRank scores
    """
    if G is None:
        G = build_mistake_similarity_graph()
    
    if len(G.nodes) == 0:
        return {}
        
    # Calculate PageRank
    pagerank = nx.pagerank(G)
    return pagerank

def get_mistake_clusters_with_stats():
    """
    Get mistake clusters along with statistics.
    
    Returns:
        dict: Dictionary with cluster information and statistics
    """
    G = build_mistake_similarity_graph()
    if len(G.nodes) == 0:
        return {'clusters': [], 'stats': {}}
    
    partition = get_louvain_clusters(G)
    pagerank = get_pagerank_scores(G)
    
    # Group mistakes by cluster
    clusters = defaultdict(list)
    for node, cluster_id in partition.items():
        node_data = G.nodes[node]
        clusters[cluster_id].append({
            'id': node,
            'label': node_data.get('label', 'Unknown'),
            'score': node_data.get('score', 0),
            'criteria': node_data.get('criteria', []),
            'importance': pagerank.get(node, 0)
        })
    
    # Sort clusters by size and importance
    result = []
    for cluster_id, nodes in clusters.items():
        # Sort nodes by importance
        nodes.sort(key=lambda x: x['importance'], reverse=True)
        
        # Calculate average score for the cluster
        avg_score = sum(n['score'] for n in nodes) / len(nodes) if nodes else 0
        
        # Get most common criteria
        all_criteria = list(itertools.chain(*[n['criteria'] for n in nodes]))
        criteria_count = defaultdict(int)
        for c in all_criteria:
            criteria_count[c] += 1
        
        top_criteria = sorted(criteria_count.items(), key=lambda x: x[1], reverse=True)[:3]
        
        result.append({
            'id': cluster_id,
            'size': len(nodes),
            'avg_score': avg_score,
            'top_criteria': [c[0] for c in top_criteria],
            'nodes': nodes
        })
    
    # Sort clusters by size
    result.sort(key=lambda x: x['size'], reverse=True)
    
    # Overall stats
    stats = {
        'total_mistakes': len(G.nodes),
        'total_connections': len(G.edges),
        'total_clusters': len(clusters),
        'avg_cluster_size': sum(len(c) for c in clusters.values()) / len(clusters) if clusters else 0
    }
    
    return {
        'clusters': result,
        'stats': stats
    }

def get_student_mistakes(student_id):
    """
    Get all mistakes made by a specific student.
    
    Args:
        student_id (str): Student ID
    
    Returns:
        list: List of mistakes with section recommendations
    """
    try:
        # Find all mistakes made by this student
        query = f"""
        FOR edge IN made_mistake
            FILTER edge._from == "{student_id}"
            FOR mistake IN mistakes
                FILTER mistake._id == edge._to
                RETURN mistake
        """
        mistakes = list(db.aql.execute(query))
        
        # Get related sections for each mistake
        for mistake in mistakes:
            section_query = f"""
            FOR edge IN related_to
                FILTER edge._from == "{mistake['_id']}"
                FOR section IN sections
                    FILTER section._id == edge._to
                    RETURN {{
                        id: section._id,
                        title: section.title,
                        content: SUBSTRING(section.content, 0, 200) + "..."
                    }}
            """
            sections = list(db.aql.execute(section_query))
            mistake['related_sections'] = sections
        
        return mistakes
    except Exception as e:
        print(f"Error getting student mistakes: {e}")
        return []

def get_student_weakest_areas(student_id):
    """
    Get the student's weakest areas based on rubric criteria.
    
    Args:
        student_id (str): Student ID
    
    Returns:
        list: List of criteria with counts and average scores
    """
    try:
        # Find all criteria from mistakes made by this student
        query = f"""
        FOR edge IN made_mistake
            FILTER edge._from == "{student_id}"
            FOR mistake IN mistakes
                FILTER mistake._id == edge._to
                FOR criteria IN mistake.rubric_criteria_names
                    COLLECT name = criteria INTO scores KEEP mistake.score_awarded
                    RETURN {{
                        criteria: name,
                        count: LENGTH(scores),
                        avg_score: AVERAGE(scores[*].mistake.score_awarded)
                    }}
        """
        criteria = list(db.aql.execute(query))
        
        # Sort by average score (ascending)
        criteria.sort(key=lambda x: x.get('avg_score', 100))
        
        return criteria
    except Exception as e:
        print(f"Error getting student weakest areas: {e}")
        return []

def get_section_recommendations(student_id):
    """
    Get section recommendations for a student based on mistakes.
    
    Args:
        student_id (str): Student ID
    
    Returns:
        list: List of recommended sections
    """
    try:
        # Find all sections related to mistakes made by this student
        query = f"""
        FOR edge IN made_mistake
            FILTER edge._from == "{student_id}"
            FOR mistake IN mistakes
                FILTER mistake._id == edge._to
                FOR rel IN related_to
                    FILTER rel._from == mistake._id
                    FOR section IN sections
                        FILTER section._id == rel._to
                        COLLECT secId = section._id, title = section.title, 
                                classCode = section.class_code
                        AGGREGATE count = COUNT()
                        SORT count DESC
                        RETURN {{
                            id: secId,
                            title: title, 
                            class_code: classCode,
                            relevance: count
                        }}
        """
        sections = list(db.aql.execute(query))
        return sections
    except Exception as e:
        print(f"Error getting section recommendations: {e}")
        return []

def get_instructor_mistake_heatmap(instructor_id):
    """
    Generate a heatmap of mistakes for an instructor.
    
    Args:
        instructor_id (str): Instructor ID
    
    Returns:
        dict: Heatmap data organized by course, rubric criteria, and frequency
    """
    try:
        # Get all courses taught by this instructor
        query = f"""
        FOR course IN courses
            FILTER course.instructor_id == "{instructor_id}"
            RETURN course
        """
        courses = list(db.aql.execute(query))
        
        # For each course, get the distribution of mistakes by criteria
        result = {}
        for course in courses:
            class_code = course['class_code']
            result[class_code] = {
                'title': course['class_title'],
                'criteria_data': {}
            }
            
            # Get submission count
            submission_query = f"""
            FOR submission IN submission
                FILTER submission.class_code == "{class_code}"
                COLLECT WITH COUNT INTO count
                RETURN count
            """
            submission_count = list(db.aql.execute(submission_query))
            submission_count = submission_count[0] if submission_count else 0
            
            result[class_code]['submission_count'] = submission_count
            
            # Get mistakes distribution
            criteria_query = f"""
            FOR submission IN submission
                FILTER submission.class_code == "{class_code}"
                FOR edge IN has_feedback_on
                    FILTER edge._from == submission._id
                    FOR mistake IN mistakes
                        FILTER mistake._id == edge._to
                        FOR criteria IN mistake.rubric_criteria_names
                            COLLECT criteriaName = criteria INTO mistakes
                            RETURN {{
                                criteria: criteriaName,
                                count: LENGTH(mistakes),
                                percentage: LENGTH(mistakes) / {max(1, submission_count)} * 100
                            }}
            """
            criteria_stats = list(db.aql.execute(criteria_query))
            
            # Organize by criteria
            for stats in criteria_stats:
                result[class_code]['criteria_data'][stats['criteria']] = {
                    'count': stats['count'],
                    'percentage': stats['percentage']
                }
        
        return result
    except Exception as e:
        print(f"Error generating instructor heatmap: {e}")
        return {}

def get_top_common_mistakes(instructor_id):
    """
    Get top common mistakes across all courses for an instructor.
    
    Args:
        instructor_id (str): Instructor ID
    
    Returns:
        list: Top common mistakes
    """
    try:
        # Get all courses taught by this instructor
        course_query = f"""
        FOR course IN courses
            FILTER course.instructor_id == "{instructor_id}"
            RETURN course.class_code
        """
        course_codes = list(db.aql.execute(course_query))
        
        if not course_codes:
            return []
            
        # Format as JSON array for AQL
        course_codes_json = json.dumps(course_codes)
        
        # Get most common mistakes
        query = f"""
        FOR submission IN submission
            FILTER submission.class_code IN {course_codes_json}
            FOR edge IN has_feedback_on
                FILTER edge._from == submission._id
                FOR mistake IN mistakes
                    FILTER mistake._id == edge._to
                    COLLECT question = mistake.question, justification = mistake.justification 
                    INTO occurrences
                    SORT LENGTH(occurrences) DESC
                    LIMIT 10
                    RETURN {{
                        question: question,
                        justification: justification,
                        count: LENGTH(occurrences)
                    }}
        """
        top_mistakes = list(db.aql.execute(query))
        return top_mistakes
    except Exception as e:
        print(f"Error getting top common mistakes: {e}")
        return []

def detect_grading_inconsistencies(instructor_id):
    """
    Detect potential grading inconsistencies.
    
    Args:
        instructor_id (str): Instructor ID
    
    Returns:
        list: Potential inconsistencies
    """
    try:
        # Get all courses taught by this instructor
        course_query = f"""
        FOR course IN courses
            FILTER course.instructor_id == "{instructor_id}"
            RETURN course.class_code
        """
        course_codes = list(db.aql.execute(course_query))
        
        if not course_codes:
            return []
            
        # Format as JSON array for AQL
        course_codes_json = json.dumps(course_codes)
        
        # Find similar justifications with different scores
        query = f"""
        LET submissions = (
            FOR submission IN submission
                FILTER submission.class_code IN {course_codes_json}
                RETURN submission
        )
        
        LET mistake_groups = (
            FOR submission IN submissions
                FOR edge IN has_feedback_on
                    FILTER edge._from == submission._id
                    FOR mistake IN mistakes
                        FILTER mistake._id == edge._to
                        
                        // Extract key terms from justification
                        LET words = SPLIT(LOWER(mistake.justification), " ")
                        LET key_terms = (
                            FOR word IN words
                                FILTER LENGTH(word) > 4
                                RETURN word
                        )
                        
                        RETURN {{
                            id: mistake._id,
                            question: mistake.question,
                            justification: mistake.justification,
                            score: mistake.score_awarded,
                            key_terms: key_terms
                        }}
        )
        
        // Group similar justifications
        FOR m1 IN mistake_groups
            FOR m2 IN mistake_groups
                FILTER m1.id != m2.id
                FILTER m1.question == m2.question
                
                // Calculate term overlap
                LET common_terms = LENGTH(
                    FOR term IN m1.key_terms
                        FILTER term IN m2.key_terms
                        RETURN term
                )
                
                LET total_terms = LENGTH(m1.key_terms) + LENGTH(m2.key_terms)
                LET similarity = common_terms / MAX(1, total_terms) * 2
                
                // Check for significant score difference
                FILTER similarity > 0.5
                FILTER ABS(m1.score - m2.score) > 20
                
                COLLECT 
                    question = m1.question,
                    justification1 = m1.justification,
                    score1 = m1.score,
                    justification2 = m2.justification,
                    score2 = m2.score
                SORT ABS(score1 - score2) DESC
                LIMIT 10
                
                RETURN {{
                    question: question,
                    inconsistency: {{
                        case1: {{
                            justification: justification1,
                            score: score1
                        }},
                        case2: {{
                            justification: justification2,
                            score: score2
                        }},
                        score_difference: ABS(score1 - score2)
                    }}
                }}
        """
        
        inconsistencies = list(db.aql.execute(query))
        return inconsistencies
    except Exception as e:
        print(f"Error detecting grading inconsistencies: {e}")
        return []