# Network Simulation ArangoDB Integration Guide

This document explains how to use the ArangoDB integration for the network simulation module, which enables advanced educational analytics.

## Overview

The ArangoDB integration stores network simulation data in a graph database, enabling powerful analytics capabilities:

- Consistency checking in grading across instructors
- Identifying student weaknesses and suggesting course materials
- Detecting common mistake patterns among students
- Providing instructors with insights to improve teaching

## Setup Instructions

### 1. Generate Network Data with Famous Names

```bash
# Navigate to the project root
cd /path/to/project/aniTA_web

# Run the data generation script
python manage.py shell -c "from network_simulation.generate_data import generate_data, save_data_as_csv, save_data_as_json, save_user_credentials_csv; data = generate_data(); save_data_as_csv(data, 'csv_data'); save_data_as_json(data, 'network_data.json'); save_user_credentials_csv(data, 'csv_data')"
```

This generates:
- Educational data in `network_data.json`
- CSV files in the `csv_data/` directory
- User credentials in `csv_data/student_credentials.csv` and `csv_data/instructor_credentials.csv`

### 2. Import Data to Django Models

```bash
python manage.py shell -c "from network_simulation.import_data import import_from_json; import_from_json('network_data.json')"
```

### 3. Import Network Data to ArangoDB

```bash
python manage.py import_network_to_arango --json network_data.json --csv-dir csv_data
```

## Usage

### API Endpoints

#### Student Analytics

- `/network/api/arango/student-weaknesses/<student_id>/` - Get a student's weak areas and recommendations
- `/network/api/arango/course-material-recommendations/<student_id>/` - Get personalized course material recommendations

#### Instructor Analytics

- `/network/api/arango/instructor-insights/<instructor_id>/` - Get teaching insights for an instructor
- `/network/api/arango/grading-inconsistencies/` - Detect potential grading inconsistencies

#### Network Visualizations

- `/network/api/arango/student-instructor-network/` - Get student-instructor network data
- `/network/api/arango/course-network/` - Get course network data

### Example API Response: Student Weaknesses

```json
{
  "weak_areas": [
    {
      "type": "Quiz",
      "avg_grade": 72.5,
      "count": 3
    }
  ],
  "common_mistakes": [
    {
      "topic": "Fundamental Concepts",
      "justification": "Missing understanding of basic principles",
      "count": 2
    }
  ],
  "recommendations": [
    {
      "type": "Quiz",
      "avg_grade": 72.5,
      "recommendation": "Focus on improving your performance in Quiz assignments",
      "related_issues": [
        {
          "topic": "Fundamental Concepts",
          "justification": "Missing understanding of basic principles",
          "count": 2
        }
      ],
      "detailed_recommendation": "Pay special attention to Fundamental Concepts"
    }
  ]
}
```

### Example API Response: Instructor Insights

```json
{
  "courses": [
    {
      "code": "CS101",
      "title": "Introduction to Computer Science"
    }
  ],
  "course_insights": [
    {
      "course": "Introduction to Computer Science",
      "code": "CS101",
      "avg_grade": 78.2,
      "submission_count": 35,
      "problematic_assignments": [
        {
          "id": "CS101_Quiz_1",
          "avg": 65.3
        }
      ],
      "recommendation": "Consider reviewing the content or assessment criteria for these assignments"
    }
  ],
  "common_mistakes": [
    {
      "topic": "Fundamental Concepts",
      "justification": "Missing understanding of basic principles",
      "count": 15
    }
  ],
  "teaching_recommendations": [
    {
      "issue": "Fundamental Concepts",
      "description": "Missing understanding of basic principles",
      "frequency": 15,
      "suggestion": "Consider focusing more classroom time on Fundamental Concepts"
    }
  ],
  "grading_inconsistencies": [
    {
      "course": "Introduction to Computer Science",
      "assignment_id": "CS101_Quiz_1",
      "inconsistency": {
        "student1": {
          "name": "Albert Einstein",
          "grade": 85
        },
        "student2": {
          "name": "Marie Curie",
          "grade": 68
        },
        "difference": 17
      },
      "instructor": "Richard Feynman"
    }
  ]
}
```

## Implementation Details

### Data Flow

1. Generate simulated network data
2. Store in both Django models and ArangoDB
3. Create relationships in ArangoDB graph
4. Run analytics on the graph data

### Graph Schema

- **Users**: Students and instructors with profiles
- **Courses**: Educational course information
- **Submissions**: Student assignments and grades
- **Mistakes**: Common error patterns
- **Edges**: Relationships between entities (made_mistake, enrolled_in, etc.)

## Troubleshooting

### Common Issues

1. **Missing Data**: Ensure the JSON and CSV files exist before importing
   ```bash
   ls -la network_data.json csv_data/
   ```

2. **ArangoDB Connection Errors**: Check connection settings in settings.py
   ```python
   ARANGO_DB = {
       'HOST': 'http://localhost',
       'PORT': '8529',
       'DATABASE': 'your_db',
       'USERNAME': 'your_username',
       'PASSWORD': 'your_password'
   }
   ```

3. **No Analytics Data**: Verify data was imported correctly
   ```bash
   python manage.py shell -c "from users.arangodb import db; print(db.collection('users').count())"
   ```