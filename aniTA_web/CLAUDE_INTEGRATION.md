# Claude API with Knowledge Graph for AI TA

This document explains the implementation of Claude API with Knowledge Graph for the AI TA (AniTA) project.

## Overview

The Claude API integration with Knowledge Graph enhances the grading system by:

1. Storing course materials, questions, and rubrics in ArangoDB
2. Using vector embeddings for efficient retrieval of relevant context
3. Structuring feedback based on rubric criteria
4. Creating relationships between materials, questions, submissions, and feedback

## Database Structure

The implementation adds several collections to ArangoDB:

- **course_materials** - Stores uploaded PDFs and extracted text
- **rubrics** - Stores rubric criteria and point values
- **material_questions** - Stores questions extracted from course materials
- **material_vectors** - Stores vector embeddings for efficient retrieval
- **has_rubric**, **has_material**, **has_question** - Edge collections for relationships

## Key Components

### 1. Course Material Processing

When an instructor uploads course materials:
- Text is extracted from PDFs
- Questions are identified and stored
- Text is split into chunks for embedding
- Vector embeddings are generated and stored
- Rubric items are parsed and stored

### 2. Vector-Based Context Retrieval

When grading a submission:
- The system finds relevant context based on vector similarity
- Only the most relevant parts of course materials are sent to Claude
- This improves efficiency and reduces costs compared to sending entire documents

### 3. Rubric-Based Feedback

The system provides structured feedback based on rubric criteria:
- Each question/answer is evaluated against specific rubric criteria
- Feedback is organized by criteria, making it more useful for students
- Scores are calculated based on rubric points

## How to Use

### 1. Setup

Before using the Claude integration, you'll need to:

1. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure ArangoDB is running (via Docker or directly).

### 2. Adding an Assignment with Rubric

As an instructor:
1. Go to "Add Assignment" for a course
2. Fill in the assignment details
3. Upload three files:
   - Instructions file (for students)
   - Subject info file (for AI grading)
   - Answer key
4. Optionally upload a rubric file (format: Criteria - Points: Description)

The system will:
- Store all files in ArangoDB
- Extract text and questions
- Generate vector embeddings
- Create a knowledge graph structure

### 3. Student Submission and Grading

When a student submits an assignment:
1. The system extracts text from the submission
2. Vector similarity is used to find relevant context
3. Claude evaluates the submission against the rubric
4. Structured feedback is provided based on rubric criteria

### 4. Testing

You can test the Claude integration with:
```bash
python test_claude_integration.py
```

## Benefits

- **Efficiency**: Only relevant context is sent to Claude, reducing token usage
- **Consistency**: Structured rubrics ensure consistent grading
- **Transparency**: Students see exactly how they performed on each criterion
- **Knowledge Graph**: Relationships between materials, questions, and feedback enable deeper analysis

## Future Enhancements

The knowledge graph structure enables several future enhancements:

1. **Mistake Clustering**: Group similar student mistakes together
2. **Feedback Reuse**: Reuse effective feedback for similar mistakes
3. **Pattern Identification**: Identify common misconceptions across students
4. **Rubric Refinement**: Analyze which rubric criteria are most effective

## Troubleshooting

- **API Key Issues**: Ensure your Anthropic API key is valid and correctly set
- **Database Connection**: Make sure ArangoDB is running and accessible
- **PDF Extraction**: If PDF text extraction fails, try converting to a different format
- **Model Selection**: If costs are a concern, adjust to use Claude 3 Haiku instead of Sonnet/Opus
