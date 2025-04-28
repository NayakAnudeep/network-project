# Educational Network Analysis Dashboard - Usage Guide

This guide explains how to use the educational network analysis dashboard to gain insights from student-instructor relationships and course connections.

## Getting Started

After installation and data generation (see README.md), you'll have access to four main dashboard views:

1. **Main Dashboard** - Overview of all metrics and statistics
2. **Student-Instructor Network** - Relationships between students and instructors
3. **Course Network** - Connections between courses via shared students
4. **Student Performance** - Academic performance analytics

## Network Analysis Concepts

This dashboard uses several network analysis concepts:

- **Nodes** - Entities in the network (students, instructors, courses)
- **Edges** - Connections between entities (enrollment, assessment)
- **Centrality** - Measure of importance in the network
- **Communities** - Groups of closely related entities
- **Density** - Proportion of potential connections that are actual connections

## Using the Dashboard

### Main Dashboard

The main dashboard provides a high-level overview of the educational network:

- **Key Metrics** - Student, instructor, and course counts
- **Network Previews** - Small visualizations of the networks
- **Performance Summary** - Overall grade distribution
- **Top Performers** - List of highest-performing students

### Student-Instructor Network

This view visualizes and analyzes the relationships between students and instructors:

- **Network Visualization** - Interactive graph of student-instructor connections
- **Network Metrics** - Quantitative analysis of the network structure
- **Top Instructors** - Instructors with the most student connections
- **Top Students** - Students with the most instructor interactions
- **Score Distribution** - Performance metrics by instructor

Use the view toggles to change the visualization mode:

- **All** - Show all connections
- **Top Connections** - Focus on the strongest relationships
- **By Performance** - Color-code by academic performance

### Course Network

This view analyzes how courses are connected through shared student enrollments:

- **Network Visualization** - Interactive graph of course relationships
- **Network Metrics** - Quantitative analysis of the course network
- **Course Enrollment** - Student count by course
- **Course Grades** - Average grade by course
- **Course Connections** - Strength of relationships between courses

### Student Performance

This view provides detailed analysis of academic performance patterns:

- **GPA Distribution** - Overall distribution of student GPAs
- **Course Grade Distribution** - Grade breakdowns by course
- **Top Students** - Highest-performing students
- **Assessment Performance** - Analysis by assessment type
- **Year-wise Performance** - Performance trends by academic year

## Detail Views

Each entity type has a detailed profile view:

### Student Profiles

- Personal information and GPA
- Course enrollment and grades
- Assessment history
- Instructor interactions

### Instructor Profiles

- Professional information
- Courses taught
- Assessment statistics
- Student interactions

### Course Profiles

- Course information
- Grade distribution
- Instructor list
- Enrolled students
- Assessment statistics

## Using Network Metrics

The dashboard provides several metrics to understand network dynamics:

- **Node Count** - Total number of entities in the network
- **Edge Count** - Total number of connections
- **Density** - Percentage of possible connections that actually exist
- **Diameter** - Maximum distance between any two nodes
- **Average Path Length** - Average number of steps between nodes
- **Centrality** - Identifies the most influential entities
- **Communities** - Detects clusters of closely related entities

## Extending the Analysis

For more advanced analysis, you can:

1. Export data for external analysis
2. Modify the `network_analysis.py` file to add custom metrics
3. Use the Django shell to run custom analyses:

```python
from network_simulation.network_analysis import build_student_instructor_network
from network_simulation.models import Student, Instructor

# Get network
G = build_student_instructor_network()

# Run custom analysis
# Example: Find students with highest betweenness centrality
import networkx as nx
betweenness = nx.betweenness_centrality(G)
top_students = {node: value for node, value in betweenness.items() 
               if G.nodes[node].get('type') == 'student'}
sorted_students = sorted(top_students.items(), key=lambda x: x[1], reverse=True)
for student_id, centrality in sorted_students[:5]:
    student = Student.objects.get(student_id=student_id)
    print(f"{student.name}: {centrality:.4f}")
```

## Data Interpretation

When interpreting results from the dashboard:

- **High centrality** suggests influential entities in the network
- **Tightly clustered communities** indicate groups with strong internal connections
- **Strong course connections** indicate common enrollment patterns
- **Performance patterns** may reveal correlations between network position and academic success

## Troubleshooting

- If visualizations don't load, ensure matplotlib and networkx are properly installed
- For large datasets, some metrics may take longer to calculate
- If community detection fails, the python-louvain package may not be installed
