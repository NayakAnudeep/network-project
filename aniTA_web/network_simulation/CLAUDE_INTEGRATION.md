# Claude Integration for Network Simulation

This document explains how the Claude API is integrated with the network simulation to generate realistic educational content, assignments, and feedback.

## Overview

The integration uses Claude to create and analyze:

1. **Source Materials**: Research paper-style content in sections (Introduction, Methodology, etc.)
2. **Assignments**: Instructions and questions for various assignment types
3. **Student Submissions**: Simulated student responses with deliberate errors
4. **Instructor Feedback**: Detailed grading and error identification
5. **Knowledge Graph**: Network of concepts, mistakes, and learning materials

## Components

### Data Generation

- `claude_integration.py`: Main module with all Claude-powered generation functions
- `generate_assignments.py`: Management command to run the generation process

### Data Storage

- **ArangoDB Collections**:
  - `users`: Student and instructor profiles
  - `courses`: Course information and assignments
  - `sections`: Individual sections of source materials
  - `course_materials`: Complete source materials
  - `submission`: Student submissions
  - `mistakes`: Identified misconceptions
  - `rubrics`: Grading criteria

### Graph Relationships (Edges)

- `made_mistake`: Links students to mistakes they made
- `related_to`: Links mistakes to relevant sections of source materials
- `has_feedback_on`: Links submissions to identified mistakes

### Network Analysis

- PageRank algorithm ranks sections by importance in the knowledge graph
- Section recommendations based on student mistake patterns
- Identification of problematic sections for instructors

## Usage

### Generating Data

```bash
# Generate assignments with source materials and feedback
python manage.py generate_assignments --courses 3 --students 5
```

Parameters:
- `--courses`: Number of courses to generate assignments for
- `--students`: Number of students per assignment
- `--delay`: Delay between Claude API calls in seconds

### Viewing Results

- `/network/source-materials/`: List of all source materials
- `/network/source-material/<id>/`: View a specific source material
- `/network/section/<id>/`: View a section with related information
- `/network/student-recommendations/<id>/`: View personalized recommendations for a student
- `/network/instructor-problem-sections/<id>/`: View problematic sections for an instructor

## Implementation Details

### Source Material Generation

Source materials are generated in research paper format with structured sections:
1. Abstract
2. Introduction
3. Background
4. Methodology
5. Results
6. Discussion
7. Conclusion
8. References

### Claude-Powered Feedback

For each student submission, Claude analyzes:
- Specific misconceptions and errors
- Which source material sections address these errors
- Scores based on a rubric

### Knowledge Graph Construction

The system builds a knowledge graph where:
- Nodes are students, mistakes, and source material sections
- Edges represent relationships (made_mistake, related_to)
- Edge weights indicate relationship strength

### PageRank for Recommendations

The PageRank algorithm is applied to the knowledge graph to:
1. Identify the most important sections
2. Rank recommendations for students
3. Highlight problematic areas for instructors

## Technical Notes

- The PageRank implementation uses NetworkX
- Sections, mistakes, and connections are tagged with `is_simulated=True`
- Markdown content is rendered as HTML in the templates
- API calls are rate-limited with delays to prevent overloading Claude API