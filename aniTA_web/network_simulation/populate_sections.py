"""
Script to populate the sections collection in ArangoDB with educational content.
These sections will be linked to mistake nodes to create a knowledge graph.
"""

import datetime
import random
from users.arangodb import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Educational content for various topics
SECTIONS = {
    "Introduction to Computer Science": [
        {
            "title": "1. Compiler vs Interpreter",
            "content": """<h3>Compilers and Interpreters</h3>
            <p>Compilers and interpreters are both tools that translate source code into machine-readable instructions, but they work in fundamentally different ways:</p>
            
            <h4>Compilers</h4>
            <ul>
                <li><strong>Translation Process:</strong> Translates the entire source code into machine code before execution</li>
                <li><strong>Output:</strong> Creates standalone executable files (.exe, .out, etc.)</li>
                <li><strong>Execution Speed:</strong> Usually faster execution as optimization happens during compilation</li>
                <li><strong>Error Reporting:</strong> Reports all syntax errors at once during compilation</li>
                <li><strong>Examples:</strong> C, C++, Rust, Go compilers</li>
            </ul>
            
            <h4>Interpreters</h4>
            <ul>
                <li><strong>Translation Process:</strong> Executes code line-by-line at runtime</li>
                <li><strong>Output:</strong> No separate machine code file is created</li>
                <li><strong>Execution Speed:</strong> Generally slower but more flexible</li>
                <li><strong>Error Reporting:</strong> Reports errors one at a time as it interprets each line</li>
                <li><strong>Examples:</strong> Python, JavaScript, Ruby interpreters</li>
            </ul>
            
            <p>Some languages use a hybrid approach with a "bytecode compiler" followed by a virtual machine interpreter (Java, C#).</p>"""
        },
        {
            "title": "2. Time Complexity Analysis",
            "content": """<h3>Time Complexity and Algorithm Efficiency</h3>
            <p>Time complexity measures how the runtime of an algorithm grows as the input size increases.</p>
            
            <h4>Common Time Complexities</h4>
            <ul>
                <li><strong>O(1) - Constant Time:</strong> Runtime doesn't change with input size (e.g., array access)</li>
                <li><strong>O(log n) - Logarithmic Time:</strong> Runtime grows logarithmically (e.g., binary search)</li>
                <li><strong>O(n) - Linear Time:</strong> Runtime grows linearly with input size (e.g., linear search)</li>
                <li><strong>O(n log n) - Linearithmic Time:</strong> Common in efficient sorting algorithms (e.g., mergesort)</li>
                <li><strong>O(n²) - Quadratic Time:</strong> Nested loops over the data (e.g., bubble sort)</li>
                <li><strong>O(2ⁿ) - Exponential Time:</strong> Runtime doubles with each additional element (e.g., recursive Fibonacci)</li>
            </ul>
            
            <h4>Why Binary Search is O(log n)</h4>
            <p>Binary search divides the search space in half with each comparison:</p>
            <ol>
                <li>Start with n elements</li>
                <li>After 1 comparison: n/2 elements remain</li>
                <li>After 2 comparisons: n/4 elements remain</li>
                <li>After k comparisons: n/2ᵏ elements remain</li>
            </ol>
            <p>The search terminates when n/2ᵏ ≈ 1, which happens when k ≈ log₂(n).</p>"""
        },
        {
            "title": "3. Object-Oriented Programming Principles",
            "content": """<h3>Core Principles of Object-Oriented Programming</h3>
            
            <h4>Encapsulation</h4>
            <p>Encapsulation is the bundling of data and methods that operate on that data within a single unit (class). It restricts direct access to some of the object's components and can prevent unintended interference.</p>
            <pre><code>class BankAccount {
    private double balance; // Private data
    
    public void deposit(double amount) {
        // Method to modify private data
        if (amount > 0) {
            balance += amount;
        }
    }
}</code></pre>
            <p>Benefits of encapsulation:</p>
            <ul>
                <li>Data hiding and controlled access</li>
                <li>Modularity and reduced complexity</li>
                <li>Easier maintenance and future changes</li>
            </ul>
            
            <h4>Inheritance</h4>
            <p>Inheritance allows a class to inherit properties and methods from another class. This promotes code reuse and establishes a relationship between parent and child classes.</p>
            
            <h4>Polymorphism</h4>
            <p>Polymorphism allows objects of different classes to be treated as objects of a common superclass. It enables methods to do different things based on the object they're acting upon.</p>
            
            <h4>Abstraction</h4>
            <p>Abstraction means hiding complex implementation details behind a simple interface, showing only the essential features of an object.</p>"""
        }
    ],
    "Data Structures": [
        {
            "title": "1. Stack and Queue Fundamentals",
            "content": """<h3>Stacks vs Queues</h3>
            <p>Stacks and queues are fundamental data structures that store collections of elements, but with different access patterns.</p>
            
            <h4>Stack (LIFO - Last In, First Out)</h4>
            <p>A stack resembles a stack of plates - you can only add or remove from the top.</p>
            <ul>
                <li><strong>Operations:</strong>
                    <ul>
                        <li><code>push(item)</code>: Add an item to the top</li>
                        <li><code>pop()</code>: Remove and return the top item</li>
                        <li><code>peek()</code>: View the top item without removing it</li>
                    </ul>
                </li>
                <li><strong>Applications:</strong>
                    <ul>
                        <li>Function call stack in programming languages</li>
                        <li>Undo/Redo operations</li>
                        <li>Expression evaluation and syntax parsing</li>
                        <li>Backtracking algorithms</li>
                    </ul>
                </li>
            </ul>
            
            <h4>Queue (FIFO - First In, First Out)</h4>
            <p>A queue resembles a line of people - first come, first served.</p>
            <ul>
                <li><strong>Operations:</strong>
                    <ul>
                        <li><code>enqueue(item)</code>: Add an item to the rear</li>
                        <li><code>dequeue()</code>: Remove and return the front item</li>
                        <li><code>peek()</code>: View the front item without removing it</li>
                    </ul>
                </li>
                <li><strong>Applications:</strong>
                    <ul>
                        <li>Task scheduling</li>
                        <li>Breadth-first search algorithms</li>
                        <li>Print queue management</li>
                        <li>Message buffers and data streaming</li>
                    </ul>
                </li>
            </ul>"""
        },
        {
            "title": "2. Array vs Linked List",
            "content": """<h3>Arrays vs Linked Lists</h3>
            <p>Arrays and linked lists are both used to store collections of data, but they have different performance characteristics and use cases.</p>
            
            <h4>Arrays</h4>
            <p>Arrays store elements in contiguous memory locations.</p>
            <ul>
                <li><strong>Characteristics:</strong>
                    <ul>
                        <li>Fixed size in many languages (dynamic arrays can grow)</li>
                        <li>Direct access to elements via index (O(1) time)</li>
                        <li>Memory-efficient for storage</li>
                        <li>Fast iteration through elements</li>
                    </ul>
                </li>
                <li><strong>Performance:</strong>
                    <ul>
                        <li>Access: O(1) - Constant time</li>
                        <li>Search: O(n) - Linear time (O(log n) if sorted and using binary search)</li>
                        <li>Insertion/Deletion: O(n) - Linear time (requires shifting elements)</li>
                    </ul>
                </li>
            </ul>
            
            <h4>Linked Lists</h4>
            <p>Linked lists store elements in nodes scattered in memory, each with a reference to the next node.</p>
            <ul>
                <li><strong>Characteristics:</strong>
                    <ul>
                        <li>Dynamic size that can easily grow or shrink</li>
                        <li>No direct access to elements (must traverse from head)</li>
                        <li>Extra memory needed for pointer storage</li>
                        <li>Simple insertion and deletion once position is found</li>
                    </ul>
                </li>
                <li><strong>Performance:</strong>
                    <ul>
                        <li>Access: O(n) - Linear time</li>
                        <li>Search: O(n) - Linear time</li>
                        <li>Insertion/Deletion: O(1) - Constant time (once position is found)</li>
                    </ul>
                </li>
            </ul>
            
            <h4>When to Use Each</h4>
            <p><strong>Choose Arrays When:</strong></p>
            <ul>
                <li>You need random access to elements</li>
                <li>Size is known and fixed</li>
                <li>Memory usage is a concern</li>
                <li>Iterating through all elements frequently</li>
            </ul>
            
            <p><strong>Choose Linked Lists When:</strong></p>
            <ul>
                <li>Size changes frequently</li>
                <li>Frequent insertions/deletions</li>
                <li>Random access is not needed</li>
                <li>Memory fragmentation is a concern</li>
            </ul>"""
        }
    ],
    "Database Systems": [
        {
            "title": "1. SQL Join Operations",
            "content": """<h3>SQL JOIN Operations</h3>
            <p>JOINs in SQL combine rows from two or more tables based on a related column between them.</p>
            
            <h4>Types of JOINs</h4>
            
            <h5>INNER JOIN</h5>
            <p>Returns records with matching values in both tables.</p>
            <pre><code>SELECT orders.order_id, customers.name
FROM orders
INNER JOIN customers ON orders.customer_id = customers.id;</code></pre>
            
            <h5>LEFT JOIN (or LEFT OUTER JOIN)</h5>
            <p>Returns all records from the left table and matched records from the right table. Results include NULL for right table columns when no match exists.</p>
            <pre><code>SELECT customers.name, orders.order_id
FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id;</code></pre>
            
            <h5>RIGHT JOIN (or RIGHT OUTER JOIN)</h5>
            <p>Returns all records from the right table and matched records from the left table. Results include NULL for left table columns when no match exists.</p>
            <pre><code>SELECT customers.name, orders.order_id
FROM customers
RIGHT JOIN orders ON customers.id = orders.customer_id;</code></pre>
            
            <h5>FULL JOIN (or FULL OUTER JOIN)</h5>
            <p>Returns all records when there is a match in either the left or right table. Results include NULL for columns when no match exists.</p>
            <pre><code>SELECT customers.name, orders.order_id
FROM customers
FULL JOIN orders ON customers.id = orders.customer_id;</code></pre>
            
            <h5>CROSS JOIN</h5>
            <p>Returns the Cartesian product of both tables (all possible combinations of all rows).</p>
            <pre><code>SELECT *
FROM customers
CROSS JOIN products;</code></pre>
            
            <h5>Self JOIN</h5>
            <p>Joins a table to itself, treating it as two separate tables.</p>
            <pre><code>SELECT e1.name AS 'Employee', e2.name AS 'Manager'
FROM employees e1
JOIN employees e2 ON e1.manager_id = e2.id;</code></pre>"""
        },
        {
            "title": "2. Database Normalization",
            "content": """<h3>Database Normalization</h3>
            <p>Normalization is the process of organizing database tables to minimize redundancy and dependency by dividing larger tables into smaller ones and defining relationships.</p>
            
            <h4>Benefits of Normalization</h4>
            <ul>
                <li>Reduces data redundancy</li>
                <li>Improves data integrity</li>
                <li>Smaller, more efficient tables</li>
                <li>More flexible database design</li>
                <li>Eliminates certain types of update anomalies</li>
            </ul>
            
            <h4>Normal Forms</h4>
            
            <h5>First Normal Form (1NF)</h5>
            <ul>
                <li>Each table has a primary key</li>
                <li>Each column contains atomic (indivisible) values</li>
                <li>No repeating groups</li>
            </ul>
            
            <h5>Second Normal Form (2NF)</h5>
            <ul>
                <li>Meets all 1NF criteria</li>
                <li>All non-key attributes are fully dependent on the primary key</li>
                <li>No partial dependencies (dependencies on only part of the primary key)</li>
            </ul>
            
            <h5>Third Normal Form (3NF)</h5>
            <ul>
                <li>Meets all 2NF criteria</li>
                <li>No transitive dependencies (non-key attributes depend on other non-key attributes)</li>
            </ul>
            
            <h5>Boyce-Codd Normal Form (BCNF)</h5>
            <ul>
                <li>Stricter version of 3NF</li>
                <li>For every dependency X → Y, X is a superkey (can uniquely identify all tuples)</li>
            </ul>
            
            <h5>Fourth Normal Form (4NF)</h5>
            <ul>
                <li>Meets BCNF criteria</li>
                <li>No multi-valued dependencies</li>
            </ul>
            
            <h5>Fifth Normal Form (5NF)</h5>
            <ul>
                <li>Meets 4NF criteria</li>
                <li>No join dependencies that aren't implied by candidate keys</li>
            </ul>
            
            <h4>Denormalization</h4>
            <p>Sometimes selective denormalization is used to improve performance by adding redundant data, particularly in data warehousing and OLAP systems.</p>"""
        }
    ],
    "Algorithms": [
        {
            "title": "1. Sorting Algorithms",
            "content": """<h3>Common Sorting Algorithms</h3>
            <p>Sorting algorithms arrange elements of a list in a specific order (usually ascending or descending).</p>
            
            <h4>Bubble Sort</h4>
            <ul>
                <li><strong>Time Complexity:</strong> O(n²)</li>
                <li><strong>Space Complexity:</strong> O(1)</li>
                <li><strong>Approach:</strong> Repeatedly steps through the list, compares adjacent elements and swaps them if they're in the wrong order</li>
                <li><strong>Stability:</strong> Stable</li>
                <li><strong>Best For:</strong> Small datasets or nearly sorted data</li>
            </ul>
            
            <h4>Selection Sort</h4>
            <ul>
                <li><strong>Time Complexity:</strong> O(n²)</li>
                <li><strong>Space Complexity:</strong> O(1)</li>
                <li><strong>Approach:</strong> Finds the minimum element and places it at the beginning, then repeats for the remaining elements</li>
                <li><strong>Stability:</strong> Not stable</li>
                <li><strong>Best For:</strong> Small datasets with expensive element moves</li>
            </ul>
            
            <h4>Insertion Sort</h4>
            <ul>
                <li><strong>Time Complexity:</strong> O(n²)</li>
                <li><strong>Space Complexity:</strong> O(1)</li>
                <li><strong>Approach:</strong> Builds a sorted array one item at a time, like sorting playing cards in your hand</li>
                <li><strong>Stability:</strong> Stable</li>
                <li><strong>Best For:</strong> Small datasets or nearly sorted data</li>
            </ul>
            
            <h4>Merge Sort</h4>
            <ul>
                <li><strong>Time Complexity:</strong> O(n log n)</li>
                <li><strong>Space Complexity:</strong> O(n)</li>
                <li><strong>Approach:</strong> Divide and conquer - divides input array into two halves, recursively sorts them, then merges</li>
                <li><strong>Stability:</strong> Stable</li>
                <li><strong>Best For:</strong> General-purpose sorting with guaranteed performance</li>
            </ul>
            
            <h4>Quick Sort</h4>
            <ul>
                <li><strong>Time Complexity:</strong> Average O(n log n), Worst O(n²)</li>
                <li><strong>Space Complexity:</strong> O(log n)</li>
                <li><strong>Approach:</strong> Divide and conquer - selects a 'pivot' and partitions the array around it</li>
                <li><strong>Stability:</strong> Not stable</li>
                <li><strong>Best For:</strong> General-purpose in-place sorting</li>
            </ul>
            
            <h4>Heap Sort</h4>
            <ul>
                <li><strong>Time Complexity:</strong> O(n log n)</li>
                <li><strong>Space Complexity:</strong> O(1)</li>
                <li><strong>Approach:</strong> Builds a heap data structure from the array and repeatedly extracts the maximum element</li>
                <li><strong>Stability:</strong> Not stable</li>
                <li><strong>Best For:</strong> Memory-constrained systems needing guaranteed performance</li>
            </ul>
            
            <h4>Radix Sort</h4>
            <ul>
                <li><strong>Time Complexity:</strong> O(n·k) where k is the number of digits</li>
                <li><strong>Space Complexity:</strong> O(n+k)</li>
                <li><strong>Approach:</strong> Non-comparative integer sorting, processes digits from least to most significant</li>
                <li><strong>Stability:</strong> Stable</li>
                <li><strong>Best For:</strong> Sorting integers or strings with fixed-length</li>
            </ul>"""
        },
        {
            "title": "2. Graph Algorithms",
            "content": """<h3>Fundamental Graph Algorithms</h3>
            <p>Graphs represent relationships between objects and are used in countless applications from social networks to maps.</p>
            
            <h4>Graph Representations</h4>
            <ul>
                <li><strong>Adjacency Matrix:</strong> A 2D array where matrix[i][j] = 1 if there is an edge from vertex i to j</li>
                <li><strong>Adjacency List:</strong> An array of lists where each list contains the neighbors of a vertex</li>
            </ul>
            
            <h4>Breadth-First Search (BFS)</h4>
            <ul>
                <li><strong>Time Complexity:</strong> O(V + E) where V is vertices and E is edges</li>
                <li><strong>Space Complexity:</strong> O(V)</li>
                <li><strong>Approach:</strong> Explores all neighbors at the current depth before moving to nodes at the next depth</li>
                <li><strong>Uses:</strong> Finding shortest paths in unweighted graphs, connected components</li>
            </ul>
            <pre><code>function BFS(graph, start):
    queue = [start]
    visited = set(start)
    
    while queue is not empty:
        vertex = queue.dequeue()
        process(vertex)
        
        for each neighbor of vertex:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.enqueue(neighbor)</code></pre>
            
            <h4>Depth-First Search (DFS)</h4>
            <ul>
                <li><strong>Time Complexity:</strong> O(V + E)</li>
                <li><strong>Space Complexity:</strong> O(V)</li>
                <li><strong>Approach:</strong> Explores as far as possible along a branch before backtracking</li>
                <li><strong>Uses:</strong> Topological sorting, cycle detection, connected components</li>
            </ul>
            <pre><code>function DFS(graph, start):
    visited = set()
    
    function DFS_recursive(vertex):
        visited.add(vertex)
        process(vertex)
        
        for each neighbor of vertex:
            if neighbor not in visited:
                DFS_recursive(neighbor)
    
    DFS_recursive(start)</code></pre>
            
            <h4>Dijkstra's Algorithm</h4>
            <ul>
                <li><strong>Time Complexity:</strong> O((V + E) log V) with binary heap</li>
                <li><strong>Space Complexity:</strong> O(V)</li>
                <li><strong>Approach:</strong> Greedy algorithm for finding shortest paths in weighted graphs</li>
                <li><strong>Limitation:</strong> Cannot handle negative edge weights</li>
            </ul>
            
            <h4>Bellman-Ford Algorithm</h4>
            <ul>
                <li><strong>Time Complexity:</strong> O(V·E)</li>
                <li><strong>Space Complexity:</strong> O(V)</li>
                <li><strong>Approach:</strong> Dynamic programming approach for shortest paths</li>
                <li><strong>Advantage:</strong> Can handle negative edge weights (and detect negative cycles)</li>
            </ul>
            
            <h4>Minimum Spanning Tree (MST) Algorithms</h4>
            <ul>
                <li><strong>Kruskal's Algorithm:</strong> Greedy approach that adds the next smallest edge that doesn't create a cycle</li>
                <li><strong>Prim's Algorithm:</strong> Builds MST by adding the nearest vertex not yet in the tree</li>
            </ul>"""
        }
    ],
    "Software Engineering": [
        {
            "title": "1. Software Development Lifecycle",
            "content": """<h3>Software Development Lifecycle (SDLC)</h3>
            <p>The SDLC provides a structured approach to software development, dividing the process into phases to improve design, development, and management.</p>
            
            <h4>Common SDLC Models</h4>
            
            <h5>Waterfall Model</h5>
            <p>A linear sequential approach where each phase must be completed before the next begins.</p>
            <ol>
                <li><strong>Requirements Analysis</strong>: Gathering complete requirements</li>
                <li><strong>System Design</strong>: Creating the system architecture</li>
                <li><strong>Implementation</strong>: Writing the code</li>
                <li><strong>Testing</strong>: Verifying the system works</li>
                <li><strong>Deployment</strong>: Delivering to customers</li>
                <li><strong>Maintenance</strong>: Fixing issues and updates</li>
            </ol>
            <p><strong>Best for</strong>: Projects with well-defined, stable requirements</p>
            
            <h5>Agile Methodology</h5>
            <p>An iterative approach emphasizing flexibility, customer collaboration, and rapid delivery.</p>
            <ul>
                <li>Works in short iterations (sprints) typically 1-4 weeks</li>
                <li>Continuous customer feedback and adaptation</li>
                <li>Self-organizing, cross-functional teams</li>
                <li>Common frameworks: Scrum, Kanban, XP (Extreme Programming)</li>
            </ul>
            <p><strong>Best for</strong>: Projects with evolving requirements or when rapid delivery is prioritized</p>
            
            <h5>DevOps</h5>
            <p>Combines software development (Dev) and IT operations (Ops) to shorten the development lifecycle.</p>
            <ul>
                <li>Continuous Integration (CI)</li>
                <li>Continuous Delivery/Deployment (CD)</li>
                <li>Automated testing and deployment</li>
                <li>Infrastructure as Code (IaC)</li>
                <li>Monitoring and feedback loops</li>
            </ul>
            <p><strong>Best for</strong>: Products requiring frequent updates and high reliability</p>
            
            <h5>Spiral Model</h5>
            <p>Combines iterative development with systematic aspects of waterfall, emphasizing risk analysis.</p>
            <ul>
                <li>Four phases: Planning, Risk Analysis, Engineering, Evaluation</li>
                <li>Repeatedly cycles through these phases with increasing detail</li>
            </ul>
            <p><strong>Best for</strong>: Large, complex projects with significant risks</p>
            
            <h5>V-Model</h5>
            <p>Extension of waterfall where each development phase has a corresponding testing phase.</p>
            <ul>
                <li>Emphasizes verification and validation</li>
                <li>Development and testing plans are developed simultaneously</li>
            </ul>
            <p><strong>Best for</strong>: Projects with strict quality requirements and limited resources</p>"""
        },
        {
            "title": "2. Design Patterns",
            "content": """<h3>Software Design Patterns</h3>
            <p>Design patterns are reusable solutions to common problems in software design. They represent best practices evolved over time by experienced software developers.</p>
            
            <h4>Creational Patterns</h4>
            <p>These patterns deal with object creation mechanisms, trying to create objects in a manner suitable to the situation.</p>
            
            <h5>Singleton Pattern</h5>
            <p>Ensures a class has only one instance and provides a global point of access to it.</p>
            <pre><code>public class Singleton {
    private static Singleton instance;
    
    private Singleton() {
        // Private constructor prevents instantiation
    }
    
    public static synchronized Singleton getInstance() {
        if (instance == null) {
            instance = new Singleton();
        }
        return instance;
    }
}</code></pre>
            <p><strong>Use cases</strong>: Database connections, logging, configuration</p>
            
            <h5>Factory Method Pattern</h5>
            <p>Defines an interface for creating an object, but lets subclasses decide which class to instantiate.</p>
            <p><strong>Use cases</strong>: When a class can't anticipate the type of objects it must create</p>
            
            <h4>Structural Patterns</h4>
            <p>These patterns concern class and object composition.</p>
            
            <h5>Adapter Pattern</h5>
            <p>Allows incompatible interfaces to work together by wrapping an object in an adapter to make it compatible with another class.</p>
            <p><strong>Use cases</strong>: Integrating new with legacy systems, third-party libraries</p>
            
            <h5>Decorator Pattern</h5>
            <p>Attaches additional responsibilities to an object dynamically, providing a flexible alternative to subclassing.</p>
            <p><strong>Use cases</strong>: Adding features to objects without modifying their structure</p>
            
            <h4>Behavioral Patterns</h4>
            <p>These patterns focus on communication between objects.</p>
            
            <h5>Observer Pattern</h5>
            <p>Defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified.</p>
            <p><strong>Use cases</strong>: Event handling systems, MVC architectures</p>
            
            <h5>Strategy Pattern</h5>
            <p>Defines a family of algorithms, encapsulates each one, and makes them interchangeable.</p>
            <pre><code>// Strategy interface
interface SortStrategy {
    void sort(int[] array);
}

// Concrete strategies
class QuickSort implements SortStrategy {
    public void sort(int[] array) {
        // QuickSort implementation
    }
}

class MergeSort implements SortStrategy {
    public void sort(int[] array) {
        // MergeSort implementation
    }
}

// Context
class Sorter {
    private SortStrategy strategy;
    
    public void setStrategy(SortStrategy strategy) {
        this.strategy = strategy;
    }
    
    public void sortArray(int[] array) {
        strategy.sort(array);
    }
}</code></pre>
            <p><strong>Use cases</strong>: When you need different variants of an algorithm</p>"""
        }
    ]
}

# Rubric criteria that will be linked to sections
RUBRIC_CRITERIA = {
    "Accuracy": "Correctly identifies and explains key concepts without factual errors",
    "Completeness": "Covers all essential aspects of the topic in sufficient detail",
    "Technical Precision": "Uses appropriate terminology and technical language",
    "Complexity Analysis": "Correctly analyzes and compares algorithm complexity",
    "Algorithm Understanding": "Demonstrates comprehension of algorithm mechanics and operation",
    "OOP Principles": "Accurately describes and applies object-oriented programming concepts",
    "Data Structure Knowledge": "Shows understanding of data structure operations and implementations",
    "Database Concepts": "Correctly applies database theory and practices",
    "Code Quality": "Writes clean, efficient, and well-structured code",
    "Problem Solving": "Demonstrates effective analytical thinking and solution development"
}

def create_rubric_node(name, description):
    """Create a rubric node or return existing one."""
    # Check if rubric with this name already exists
    rubrics = db.collection('rubrics')
    existing = list(rubrics.find({"name": name, "description": description}))
    
    if existing:
        logger.info(f"Found existing rubric: {name}")
        return existing[0]
    
    # Create new rubric node
    rubric_data = {
        "name": name,
        "description": description,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    rubric_id = rubrics.insert(rubric_data)
    logger.info(f"Created new rubric: {name} with ID {rubric_id}")
    return rubrics.get(rubric_id["_id"])

def create_section(title, content, class_code, material_id=None):
    """Create a section in the database."""
    sections = db.collection('sections')
    
    # Check if section with this title already exists for the class
    existing = list(sections.find({"title": title, "class_code": class_code}))
    if existing:
        logger.info(f"Section already exists: {title} for {class_code}")
        return existing[0]
    
    # Create section
    section_data = {
        "title": title,
        "content": content,
        "class_code": class_code,
        "material_id": material_id or "materials/default",
        "section_number": title.split(".")[0] if "." in title else "0",
        "created_at": datetime.datetime.utcnow().isoformat(),
        "is_simulated": True
    }
    
    section_id = sections.insert(section_data)
    logger.info(f"Created new section: {title} with ID {section_id}")
    return sections.get(section_id["_id"])

def link_section_to_rubric(section_id, rubric_id):
    """Create a link between a section and a rubric."""
    # Check if edge collection exists
    if not db.has_collection("covers_topic"):
        db.create_collection("covers_topic", edge=True)
    
    covers_topic = db.collection("covers_topic")
    
    # Check if link already exists
    existing_query = """
    FOR edge IN covers_topic
        FILTER edge._from == @section_id AND edge._to == @rubric_id
        RETURN edge
    """
    existing = list(db.aql.execute(existing_query, bind_vars={
        "section_id": section_id,
        "rubric_id": rubric_id
    }))
    
    if existing:
        logger.info(f"Link already exists between {section_id} and {rubric_id}")
        return existing[0]
    
    # Create link
    edge_data = {
        "_from": section_id,
        "_to": rubric_id,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "weight": random.uniform(0.5, 1.0)
    }
    
    edge_id = covers_topic.insert(edge_data)
    logger.info(f"Created new link between {section_id} and {rubric_id}")
    return covers_topic.get(edge_id["_id"])

def link_section_to_mistakes(section_id, class_code, limit=3):
    """Link a section to relevant mistake nodes."""
    # Find mistake nodes for the course
    mistake_query = """
    FOR submission IN submission
        FILTER submission.class_code == @class_code
        FOR edge IN has_feedback_on
            FILTER edge._from == submission._id
            FOR mistake IN mistakes
                FILTER mistake._id == edge._to
                LIMIT @limit
                RETURN mistake
    """
    
    mistakes = list(db.aql.execute(mistake_query, bind_vars={
        "class_code": class_code,
        "limit": limit
    }))
    
    # If no mistakes found, return
    if not mistakes:
        logger.info(f"No mistakes found for class {class_code}, skipping links")
        return []
    
    # Ensure edge collection exists
    if not db.has_collection("related_to"):
        db.create_collection("related_to", edge=True)
    
    related_to = db.collection("related_to")
    links = []
    
    # Create links between section and mistakes
    for mistake in mistakes:
        # Check if link already exists
        existing_query = """
        FOR edge IN related_to
            FILTER edge._from == @section_id AND edge._to == @mistake_id
            RETURN edge
        """
        existing = list(db.aql.execute(existing_query, bind_vars={
            "section_id": section_id,
            "mistake_id": mistake["_id"]
        }))
        
        if existing:
            logger.info(f"Link already exists between {section_id} and {mistake['_id']}")
            links.append(existing[0])
            continue
        
        # Create link
        edge_data = {
            "_from": section_id,
            "_to": mistake["_id"],
            "created_at": datetime.datetime.utcnow().isoformat(),
            "relevance": random.uniform(0.7, 0.98),
            "is_simulated": True
        }
        
        edge_id = related_to.insert(edge_data)
        logger.info(f"Created link between section and mistake: {mistake['_id']}")
        links.append(related_to.get(edge_id["_id"]))
    
    return links

def populate_sections():
    """Main function to populate sections and create relationships."""
    # First check if we already have sections
    sections = db.collection('sections')
    existing_count = sections.count()
    
    if existing_count > 0:
        logger.info(f"Found {existing_count} existing sections")
    
    # Get active course codes from database
    course_query = """
    FOR course IN courses
        RETURN {
            code: course.class_code,
            title: course.class_title
        }
    """
    
    courses = list(db.aql.execute(course_query))
    logger.info(f"Found {len(courses)} courses in database")
    
    # Map course codes to subjects
    course_subjects = {}
    for i, course in enumerate(courses):
        if i % 5 == 0:
            subject = "Introduction to Computer Science"
        elif i % 5 == 1:
            subject = "Data Structures"
        elif i % 5 == 2:
            subject = "Database Systems"
        elif i % 5 == 3:
            subject = "Algorithms"
        else:
            subject = "Software Engineering"
        
        course_subjects[course["code"]] = subject
    
    # Create rubric criteria nodes
    rubric_nodes = {}
    for name, description in RUBRIC_CRITERIA.items():
        rubric_nodes[name] = create_rubric_node(name, description)
    
    # Create sections and link to rubrics and mistakes
    sections_created = 0
    links_created = 0
    
    for course_code, subject in course_subjects.items():
        if subject in SECTIONS:
            for section_data in SECTIONS[subject]:
                # Create section
                section = create_section(
                    section_data["title"],
                    section_data["content"],
                    course_code
                )
                sections_created += 1
                
                # Link to relevant rubrics (2-3 per section)
                rubric_names = list(RUBRIC_CRITERIA.keys())
                random.shuffle(rubric_names)
                selected_rubrics = rubric_names[:random.randint(2, 3)]
                
                for rubric_name in selected_rubrics:
                    link_section_to_rubric(section["_id"], rubric_nodes[rubric_name]["_id"])
                    links_created += 1
                
                # Link to relevant mistakes
                mistake_links = link_section_to_mistakes(section["_id"], course_code)
                links_created += len(mistake_links)
    
    logger.info(f"Populated {sections_created} sections with {links_created} links")
    return {
        "sections_created": sections_created,
        "links_created": links_created
    }

if __name__ == "__main__":
    populate_sections()