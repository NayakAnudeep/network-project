"""
Realistic data generator for educational data.

This module creates realistic educational questions, answers, feedback, and rubrics
for simulation purposes. It generates data that mimics authentic assessment scenarios.
"""

import random
import datetime
import json
import os
from collections import defaultdict
from users.arangodb import db

# Course subjects with authentic questions and answers
SUBJECTS = {
    "Introduction to Computer Science": [
        {
            "question": "Explain the difference between a compiler and an interpreter.",
            "answer": "A compiler translates the entire source code into machine code before execution, while an interpreter executes the code line by line. Compilers produce standalone executable files and generally result in faster program execution, whereas interpreters provide better debugging capabilities and platform independence.",
            "rubric_criteria": [
                {"name": "Accuracy", "description": "Correctly distinguishes between compilers and interpreters"},
                {"name": "Completeness", "description": "Covers translation process, execution model, and performance implications"},
                {"name": "Technical Precision", "description": "Uses appropriate technical terminology"}
            ],
            "source_materials": ["Compiler Design Principles", "Programming Language Implementation"]
        },
        {
            "question": "What is the time complexity of binary search and why is it efficient?",
            "answer": "Binary search has a time complexity of O(log n). It's efficient because it repeatedly divides the search interval in half, eliminating half of the remaining elements at each step. This logarithmic behavior makes it significantly faster than linear search (O(n)) for large datasets.",
            "rubric_criteria": [
                {"name": "Complexity Analysis", "description": "Correctly identifies the time complexity"},
                {"name": "Algorithm Understanding", "description": "Explains the divide-and-conquer approach"},
                {"name": "Comparative Analysis", "description": "Compares efficiency with other search algorithms"}
            ],
            "source_materials": ["Algorithm Analysis", "Search Algorithms"]
        },
        {
            "question": "Describe the concept of encapsulation in object-oriented programming.",
            "answer": "Encapsulation is bundling data and methods that operate on that data within a single unit or class. It allows for data hiding by restricting direct access to the object's components and exposing functionality through well-defined interfaces. This promotes information hiding, modularity, and code maintainability.",
            "rubric_criteria": [
                {"name": "OOP Principles", "description": "Accurately describes encapsulation as an OOP concept"},
                {"name": "Data Hiding", "description": "Explains the protection and access control aspects"},
                {"name": "Benefits", "description": "Discusses advantages like modularity and maintenance"}
            ],
            "source_materials": ["Object-Oriented Design", "Software Engineering Principles"]
        },
        {
            "question": "What is the difference between a stack and a queue data structure?",
            "answer": "A stack is a LIFO (Last-In-First-Out) data structure where elements are added and removed from the same end (top). A queue is a FIFO (First-In-First-Out) data structure where elements are added at one end (rear) and removed from the other end (front). Stacks are typically used for function calls and backtracking, while queues are used for breadth-first searches and scheduling.",
            "rubric_criteria": [
                {"name": "Data Structure Properties", "description": "Clearly identifies LIFO vs FIFO characteristics"},
                {"name": "Operation Description", "description": "Explains insertion and deletion operations"},
                {"name": "Application Examples", "description": "Provides relevant usage scenarios"}
            ],
            "source_materials": ["Data Structures Fundamentals", "Abstract Data Types"]
        },
        {
            "question": "Explain the concept of recursion and provide an example.",
            "answer": "Recursion is a programming technique where a function calls itself to solve a problem. The function contains a base case to terminate recursion and a recursive case that moves toward the base case. For example, computing factorial: factorial(n) = n * factorial(n-1) with factorial(0) = 1 as the base case. Recursive solutions can often provide elegant implementations for problems that exhibit self-similar structure.",
            "rubric_criteria": [
                {"name": "Concept Definition", "description": "Accurately defines recursion"},
                {"name": "Base and Recursive Cases", "description": "Identifies both essential components"},
                {"name": "Example Implementation", "description": "Provides a clear, working example"}
            ],
            "source_materials": ["Recursive Algorithms", "Algorithm Design Paradigms"]
        }
    ],
    "Data Structures and Algorithms": [
        {
            "question": "Compare and contrast depth-first search (DFS) and breadth-first search (BFS).",
            "answer": "DFS explores as far as possible along each branch before backtracking, often implemented with a stack or recursion. BFS explores all neighbors at the present depth before moving to vertices at the next depth level, typically implemented with a queue. DFS is better for problems like topological sorting or maze generation, while BFS is preferred for finding shortest paths in unweighted graphs or level-order traversals.",
            "rubric_criteria": [
                {"name": "Algorithm Characteristics", "description": "Correctly describes the traversal patterns"},
                {"name": "Implementation Details", "description": "Explains the data structures used"},
                {"name": "Application Scenarios", "description": "Identifies appropriate use cases"}
            ],
            "source_materials": ["Graph Algorithms", "Search Strategies"]
        },
        {
            "question": "Explain the quicksort algorithm and analyze its time complexity.",
            "answer": "Quicksort is a divide-and-conquer sorting algorithm that selects a pivot element, partitions the array around the pivot, and recursively sorts the sub-arrays. Its average time complexity is O(n log n), but worst-case complexity is O(n²) when the pivot selections consistently create unbalanced partitions. Despite this, quicksort is often faster in practice than other O(n log n) algorithms due to its cache efficiency and low overhead.",
            "rubric_criteria": [
                {"name": "Algorithm Description", "description": "Accurately describes the quicksort process"},
                {"name": "Complexity Analysis", "description": "Correctly analyzes both average and worst cases"},
                {"name": "Performance Factors", "description": "Discusses practical efficiency considerations"}
            ],
            "source_materials": ["Sorting Algorithms", "Algorithm Analysis"]
        },
        {
            "question": "What is a balanced binary search tree and why is it important?",
            "answer": "A balanced binary search tree is a BST where the height difference between left and right subtrees is limited (typically to 1 in AVL trees or bounded by a constant in Red-Black trees). Balance is important because it ensures O(log n) time complexity for operations like search, insert, and delete. Without balancing, a BST can degenerate into a linked list with O(n) operation time in worst cases.",
            "rubric_criteria": [
                {"name": "Tree Properties", "description": "Correctly defines balanced BSTs"},
                {"name": "Balance Mechanisms", "description": "Explains how balance is maintained"},
                {"name": "Efficiency Analysis", "description": "Discusses performance improvements"}
            ],
            "source_materials": ["Advanced Data Structures", "Self-balancing Trees"]
        },
        {
            "question": "Describe dynamic programming and how it differs from divide-and-conquer.",
            "answer": "Dynamic programming is an optimization technique that solves complex problems by breaking them down into simpler overlapping subproblems and storing their solutions to avoid redundant computation. Unlike divide-and-conquer, which divides problems into non-overlapping subproblems, dynamic programming specifically addresses problems with overlapping subproblems and optimal substructure, using techniques like memoization or tabulation to improve efficiency.",
            "rubric_criteria": [
                {"name": "Technique Definition", "description": "Accurately describes dynamic programming"},
                {"name": "Comparative Analysis", "description": "Clearly contrasts with divide-and-conquer"},
                {"name": "Implementation Approaches", "description": "Explains memoization and tabulation"}
            ],
            "source_materials": ["Algorithm Design Paradigms", "Optimization Techniques"]
        },
        {
            "question": "Explain the concept of hashing and how hash collisions are managed.",
            "answer": "Hashing is a technique that maps data of arbitrary size to fixed-size values using a hash function. Hash collisions occur when different inputs produce the same hash value. Common collision resolution techniques include chaining (where each bucket contains a linked list of entries) and open addressing (where alternative positions are sought within the table using methods like linear probing, quadratic probing, or double hashing).",
            "rubric_criteria": [
                {"name": "Hashing Fundamentals", "description": "Correctly explains hash functions and their purpose"},
                {"name": "Collision Understanding", "description": "Identifies why collisions occur"},
                {"name": "Resolution Techniques", "description": "Describes multiple collision handling methods"}
            ],
            "source_materials": ["Hash Tables", "Collision Resolution Strategies"]
        }
    ],
    "Database Systems": [
        {
            "question": "Explain the concept of database normalization and its benefits.",
            "answer": "Database normalization is the process of structuring a relational database to minimize redundancy and dependency by organizing fields and tables. It involves dividing large tables into smaller ones and defining relationships between them. The benefits include reduced data redundancy, improved data integrity, smaller database size, and more efficient data maintenance. Normal forms (1NF, 2NF, 3NF, BCNF, etc.) provide guidelines for the normalization process.",
            "rubric_criteria": [
                {"name": "Normalization Definition", "description": "Accurately explains the concept"},
                {"name": "Normal Forms", "description": "Mentions progressive normalization levels"},
                {"name": "Advantage Analysis", "description": "Describes practical benefits"}
            ],
            "source_materials": ["Database Design", "Normalization Theory"]
        },
        {
            "question": "Compare and contrast SQL and NoSQL databases.",
            "answer": "SQL databases are relational, use structured query language, follow ACID properties, and have predefined schemas. NoSQL databases are non-relational, use various query languages, often prioritize BASE properties (Basically Available, Soft state, Eventually consistent), and typically have flexible schemas. SQL databases excel in complex queries and transactions, while NoSQL databases offer better horizontal scalability, schema flexibility, and performance for specific data models like document, key-value, column-family, or graph data.",
            "rubric_criteria": [
                {"name": "Database Paradigms", "description": "Distinguishes relational vs non-relational"},
                {"name": "Technical Differences", "description": "Compares structure, consistency models, and querying"},
                {"name": "Use Case Analysis", "description": "Identifies appropriate scenarios for each"}
            ],
            "source_materials": ["Database Management Systems", "Modern Database Technologies"]
        },
        {
            "question": "What are database transactions and why are ACID properties important?",
            "answer": "A database transaction is a sequence of operations performed as a single logical unit of work. ACID properties (Atomicity, Consistency, Isolation, Durability) ensure transaction reliability. Atomicity guarantees that all operations complete or none do. Consistency ensures the database remains in a valid state. Isolation prevents concurrent transactions from interfering with each other. Durability ensures that committed transactions persist even in system failure.",
            "rubric_criteria": [
                {"name": "Transaction Definition", "description": "Correctly defines database transactions"},
                {"name": "ACID Properties", "description": "Explains all four properties accurately"},
                {"name": "Practical Importance", "description": "Discusses why these guarantees matter"}
            ],
            "source_materials": ["Transaction Processing", "Database Reliability Engineering"]
        },
        {
            "question": "Describe database indexing and how it improves query performance.",
            "answer": "Database indexing is a data structure technique that improves the speed of data retrieval operations by creating pointers to data locations based on indexed columns. Common index types include B-trees, hash indexes, and bitmap indexes. Indexing improves query performance by reducing I/O operations and the amount of data that needs to be scanned. However, indexes increase storage requirements and can slow down write operations, so they must be strategically implemented based on query patterns.",
            "rubric_criteria": [
                {"name": "Index Functionality", "description": "Accurately explains how indexes work"},
                {"name": "Index Types", "description": "Identifies different indexing structures"},
                {"name": "Performance Tradeoffs", "description": "Discusses benefits and costs"}
            ],
            "source_materials": ["Query Optimization", "Database Performance Tuning"]
        },
        {
            "question": "Explain the concept of database sharding and its implementation challenges.",
            "answer": "Database sharding is a horizontal partitioning technique that splits a database across multiple servers based on a shard key. Each shard contains a subset of the database with its own compute, storage, and memory resources. Implementation challenges include choosing appropriate shard keys, handling cross-shard queries, maintaining data consistency, implementing distributed transactions, and managing schema changes across shards. Sharding is critical for scalability but introduces significant complexity to the database architecture.",
            "rubric_criteria": [
                {"name": "Sharding Concept", "description": "Correctly defines horizontal partitioning"},
                {"name": "Implementation Strategy", "description": "Explains shard key selection and distribution"},
                {"name": "Challenge Analysis", "description": "Identifies technical difficulties"}
            ],
            "source_materials": ["Distributed Databases", "Scalability Patterns"]
        }
    ],
    "Computer Networks": [
        {
            "question": "Explain the TCP/IP protocol stack and the function of each layer.",
            "answer": "The TCP/IP protocol stack consists of four layers: Application layer (HTTP, FTP, DNS) provides user services and network applications. Transport layer (TCP, UDP) handles end-to-end communication and data flow control. Internet/Network layer (IP, ICMP) manages packet routing through multiple networks. Link layer (Ethernet, Wi-Fi) deals with physical addressing and media access. Each layer encapsulates data from the layer above and provides services to it, creating a modular network architecture.",
            "rubric_criteria": [
                {"name": "Layer Identification", "description": "Correctly identifies all four layers"},
                {"name": "Protocol Examples", "description": "Provides relevant protocols for each layer"},
                {"name": "Encapsulation Understanding", "description": "Explains the layering process"}
            ],
            "source_materials": ["TCP/IP Architecture", "Network Protocols"]
        },
        {
            "question": "Compare connection-oriented (TCP) and connectionless (UDP) protocols.",
            "answer": "TCP is connection-oriented, providing reliable, ordered, and error-checked delivery through handshaking, acknowledgments, and retransmissions. It guarantees delivery but with higher overhead. UDP is connectionless, offering simple, unacknowledged transmission without flow control or reliability guarantees. It provides lower latency and overhead but no delivery guarantees. TCP is suitable for applications requiring reliability (web, email), while UDP is better for real-time applications where speed outweighs reliability (streaming, gaming, VoIP).",
            "rubric_criteria": [
                {"name": "Protocol Characteristics", "description": "Accurately describes both protocols"},
                {"name": "Reliability Mechanisms", "description": "Explains how TCP ensures delivery"},
                {"name": "Application Suitability", "description": "Identifies appropriate use cases"}
            ],
            "source_materials": ["Transport Layer Protocols", "Network Performance"]
        },
        {
            "question": "What is the purpose of DNS and how does it work?",
            "answer": "The Domain Name System (DNS) translates human-readable domain names into IP addresses. When a user enters a URL, a DNS resolver queries a series of nameservers hierarchically: root servers, TLD servers, domain nameservers, and potentially subdomain servers. The process typically involves recursive and iterative queries, with extensive caching to improve performance. DNS also provides additional services like mail server records (MX), service records (SRV), and text records (TXT).",
            "rubric_criteria": [
                {"name": "DNS Purpose", "description": "Correctly explains name resolution function"},
                {"name": "Resolution Process", "description": "Describes the hierarchical query flow"},
                {"name": "Record Types", "description": "Identifies different DNS record functions"}
            ],
            "source_materials": ["DNS Architecture", "Internet Infrastructure"]
        },
        {
            "question": "Explain how routing protocols like OSPF and BGP work and their differences.",
            "answer": "OSPF (Open Shortest Path First) is an interior gateway protocol using link-state algorithms to calculate shortest paths within an autonomous system. It creates a topological database of the network and runs Dijkstra's algorithm to find optimal routes. BGP (Border Gateway Protocol) is an exterior gateway protocol that connects autonomous systems across the internet. It uses path-vector routing with policy-based decisions rather than just metrics. OSPF focuses on technical efficiency within domains, while BGP handles inter-domain routing with political and economic considerations.",
            "rubric_criteria": [
                {"name": "Protocol Classification", "description": "Distinguishes interior vs exterior protocols"},
                {"name": "Routing Mechanisms", "description": "Explains algorithms and decision processes"},
                {"name": "Practical Application", "description": "Describes where each is deployed"}
            ],
            "source_materials": ["Routing Protocols", "Internet Architecture"]
        },
        {
            "question": "Describe how HTTPS secures web communication.",
            "answer": "HTTPS secures web communication by combining HTTP with encryption protocols (TLS/SSL). The process begins with a TLS handshake where the client verifies the server's identity through certificates, followed by key exchange to establish a shared secret. This enables encrypted data transmission that prevents eavesdropping and tampering. HTTPS provides authentication (verifying server identity), encryption (protecting data confidentiality), and integrity (ensuring data hasn't been modified in transit).",
            "rubric_criteria": [
                {"name": "Security Components", "description": "Identifies authentication, encryption, and integrity"},
                {"name": "Handshake Process", "description": "Explains certificate validation and key exchange"},
                {"name": "Protection Scope", "description": "Describes what threats are mitigated"}
            ],
            "source_materials": ["Web Security", "Cryptographic Protocols"]
        }
    ],
    "Machine Learning": [
        {
            "question": "Compare supervised, unsupervised, and reinforcement learning paradigms.",
            "answer": "Supervised learning uses labeled training data to learn a mapping from inputs to outputs (e.g., classification, regression). Unsupervised learning discovers patterns or structures in unlabeled data (e.g., clustering, dimensionality reduction). Reinforcement learning involves an agent learning optimal actions through trial and error by receiving rewards or penalties (e.g., game playing, robotics). Supervised learning requires labeled data and clear target outputs, unsupervised learning works with unstructured data, while reinforcement learning needs a defined reward system and environment.",
            "rubric_criteria": [
                {"name": "Paradigm Definitions", "description": "Accurately describes all three learning types"},
                {"name": "Example Algorithms", "description": "Provides relevant examples for each paradigm"},
                {"name": "Application Domains", "description": "Identifies suitable use cases"}
            ],
            "source_materials": ["ML Fundamentals", "Learning Paradigms"]
        },
        {
            "question": "Explain the bias-variance tradeoff in machine learning.",
            "answer": "The bias-variance tradeoff represents the balance between underfitting (high bias) and overfitting (high variance). High bias models are too simple and make strong assumptions about the data, missing underlying patterns. High variance models are too complex, capturing noise and failing to generalize. Total error equals bias² + variance + irreducible error. Techniques to manage this tradeoff include cross-validation, regularization, and ensemble methods. Finding the optimal model complexity minimizes the combined error components.",
            "rubric_criteria": [
                {"name": "Concept Definition", "description": "Correctly explains both bias and variance"},
                {"name": "Error Components", "description": "Describes how they contribute to total error"},
                {"name": "Mitigation Strategies", "description": "Provides methods to manage the tradeoff"}
            ],
            "source_materials": ["Statistical Learning Theory", "Model Complexity"]
        },
        {
            "question": "Describe how neural networks learn through backpropagation.",
            "answer": "Backpropagation is the algorithm that allows neural networks to learn by efficiently calculating gradients. The process involves: forward pass (computing predictions), calculating loss, backward pass (computing gradients of the loss with respect to each parameter using the chain rule), and parameter updates (adjusting weights and biases using gradient descent). This process propagates the error backward through the network, assigning responsibility to each parameter proportional to its contribution to the error, allowing the network to iteratively improve its predictions.",
            "rubric_criteria": [
                {"name": "Algorithm Steps", "description": "Correctly outlines the backpropagation process"},
                {"name": "Gradient Calculation", "description": "Explains how errors propagate backward"},
                {"name": "Update Mechanism", "description": "Describes how parameters are adjusted"}
            ],
            "source_materials": ["Neural Network Training", "Gradient-based Optimization"]
        },
        {
            "question": "What is feature engineering and why is it important in machine learning?",
            "answer": "Feature engineering is the process of using domain knowledge to extract and transform relevant features from raw data to improve model performance. It includes techniques like normalization, one-hot encoding, binning, and creating interaction terms. Feature engineering is crucial because machine learning algorithms learn from features rather than raw data. Good features capture meaningful patterns, reduce dimensionality, address missing values, and often have greater impact on model performance than algorithm selection or hyperparameter tuning.",
            "rubric_criteria": [
                {"name": "Process Description", "description": "Accurately explains feature transformation"},
                {"name": "Technique Examples", "description": "Provides relevant engineering methods"},
                {"name": "Performance Impact", "description": "Explains why it affects model quality"}
            ],
            "source_materials": ["Data Preprocessing", "Feature Selection"]
        },
        {
            "question": "Explain how decision trees work and their advantages and limitations.",
            "answer": "Decision trees recursively partition data based on feature values to create a tree-like model that predicts target values. Nodes represent features, branches represent decision rules, and leaves represent outcomes. Trees work by selecting optimal splitting criteria (e.g., Gini impurity, information gain) at each step. Advantages include interpretability, handling mixed data types, and requiring minimal preprocessing. Limitations include tendency to overfit, instability to small data changes, and difficulty capturing complex relationships. Ensemble methods like random forests address many of these limitations.",
            "rubric_criteria": [
                {"name": "Algorithm Mechanics", "description": "Correctly explains tree construction process"},
                {"name": "Splitting Criteria", "description": "Identifies how optimal splits are determined"},
                {"name": "Tradeoff Analysis", "description": "Balances pros and cons accurately"}
            ],
            "source_materials": ["Decision Tree Algorithms", "Tree-based Models"]
        }
    ],
    "Software Engineering": [
        {
            "question": "Explain the Agile software development methodology and its principles.",
            "answer": "Agile is an iterative approach to software development that emphasizes flexibility, customer collaboration, and rapid delivery of functional software. Its core principles include customer satisfaction through early and continuous delivery, welcoming changing requirements, frequent delivery of working software, close cooperation between business stakeholders and developers, motivated individuals, face-to-face communication, working software as progress measure, sustainable development pace, technical excellence, simplicity, self-organizing teams, and regular reflection for improvement. Common Agile frameworks include Scrum, Kanban, and Extreme Programming.",
            "rubric_criteria": [
                {"name": "Methodology Definition", "description": "Accurately describes the Agile approach"},
                {"name": "Core Principles", "description": "Identifies key values from the Agile Manifesto"},
                {"name": "Implementation Frameworks", "description": "Mentions specific Agile methodologies"}
            ],
            "source_materials": ["Agile Manifesto", "Software Development Methodologies"]
        },
        {
            "question": "What is continuous integration and continuous deployment (CI/CD) and why is it important?",
            "answer": "CI/CD is a set of practices that automates the building, testing, and deployment of applications. Continuous Integration involves frequently merging code changes into a shared repository with automated testing to detect issues early. Continuous Deployment automatically deploys code changes to production after passing all tests. CI/CD reduces integration problems, improves code quality, accelerates delivery, provides faster feedback, minimizes manual errors, and enables more frequent releases. It's implemented through pipelines that automate the software delivery process from commit to production.",
            "rubric_criteria": [
                {"name": "Practice Definition", "description": "Distinguishes between CI and CD components"},
                {"name": "Automation Process", "description": "Explains how the pipeline works"},
                {"name": "Business Value", "description": "Describes benefits to development teams"}
            ],
            "source_materials": ["DevOps Practices", "Deployment Automation"]
        },
        {
            "question": "Describe the SOLID principles of object-oriented design.",
            "answer": "SOLID is an acronym for five design principles: Single Responsibility Principle (a class should have only one reason to change), Open/Closed Principle (entities should be open for extension but closed for modification), Liskov Substitution Principle (derived classes must be substitutable for their base classes), Interface Segregation Principle (clients shouldn't depend on interfaces they don't use), and Dependency Inversion Principle (depend on abstractions, not concretions). These principles promote code that's maintainable, extensible, and robust by addressing key aspects of object-oriented design and dependency management.",
            "rubric_criteria": [
                {"name": "Principle Identification", "description": "Correctly defines all five SOLID principles"},
                {"name": "Design Implications", "description": "Explains how each affects software structure"},
                {"name": "Practical Benefits", "description": "Describes advantages of following these principles"}
            ],
            "source_materials": ["Object-Oriented Design", "Design Patterns"]
        },
        {
            "question": "What is technical debt and how should it be managed?",
            "answer": "Technical debt is the implied cost of future rework caused by choosing expedient solutions now instead of better approaches that would take longer. It accumulates when shortcuts are taken, requirements change, or technology evolves. Managing technical debt involves: identification (code reviews, static analysis), measurement (quantifying impact), prioritization (based on business value and risk), systematic reduction (refactoring, rewrites), and prevention (coding standards, automated testing). The key is balancing short-term delivery needs with long-term codebase health through deliberate planning and regular debt reduction.",
            "rubric_criteria": [
                {"name": "Concept Definition", "description": "Accurately explains the debt metaphor"},
                {"name": "Debt Sources", "description": "Identifies how technical debt accumulates"},
                {"name": "Management Strategy", "description": "Provides a comprehensive approach"}
            ],
            "source_materials": ["Software Maintenance", "Code Quality"]
        },
        {
            "question": "Explain the concept of microservices architecture and its tradeoffs.",
            "answer": "Microservices architecture is an approach where an application is built as a collection of small, independently deployable services, each running in its own process and communicating via lightweight mechanisms (typically HTTP APIs). Advantages include independent development and deployment, technology diversity, resilience, and scalability. Challenges include increased operational complexity, distributed system problems, complicated testing, and potential data consistency issues. Microservices are well-suited for large, complex applications needing rapid evolution but introduce significant overhead compared to monolithic designs for simpler applications.",
            "rubric_criteria": [
                {"name": "Architecture Definition", "description": "Correctly describes microservice structure"},
                {"name": "Service Characteristics", "description": "Explains properties of individual services"},
                {"name": "Tradeoff Analysis", "description": "Balances advantages against challenges"}
            ],
            "source_materials": ["System Architecture", "Distributed Systems"]
        }
    ]
}

# Feedback types for different score ranges
FEEDBACK_TYPES = {
    (0, 50): [
        "The answer demonstrates fundamental misunderstandings of {concept}. Key issues include {issue1} and {issue2}.",
        "This response lacks basic comprehension of {concept}. Critical problems are {issue1} and {issue2}.",
        "The answer shows significant conceptual errors regarding {concept}, particularly {issue1} and {issue2}."
    ],
    (50, 70): [
        "The answer shows partial understanding of {concept}, but has weaknesses in {issue1} and {issue2}.",
        "While there is some grasp of {concept}, the response needs improvement in {issue1} and {issue2}.",
        "The answer demonstrates incomplete knowledge of {concept}, missing key aspects like {issue1} and {issue2}."
    ],
    (70, 85): [
        "The answer correctly addresses {concept}, but could be strengthened by improving {issue1} and adding {issue2}.",
        "There's good understanding of {concept}, though the response would benefit from more detail on {issue1} and {issue2}.",
        "The answer is mostly accurate regarding {concept}, but lacks depth in explaining {issue1} and {issue2}."
    ],
    (85, 100): [
        "The answer demonstrates excellent comprehension of {concept}, with minor room for improvement in {issue1}.",
        "This is a strong response that thoroughly explains {concept}, though could be enhanced slightly by addressing {issue1}.",
        "The answer shows comprehensive understanding of {concept}, with just a small gap in {issue1}."
    ]
}

# Common issues by rubric criteria
COMMON_ISSUES = {
    "Accuracy": ["factual errors", "misconceptions", "outdated information", "oversimplifications", "inaccurate definitions"],
    "Completeness": ["missing key components", "insufficient examples", "incomplete explanations", "overlooked implications", "omitted context"],
    "Technical Precision": ["imprecise terminology", "vague descriptions", "informal language", "ambiguous statements", "incorrect technical terms"],
    "Complexity Analysis": ["incorrect big-O notation", "missed worst-case analysis", "neglected space complexity", "inaccurate efficiency claims", "simplified complexity assessment"],
    "Algorithm Understanding": ["flawed algorithm description", "missing algorithm steps", "incorrect execution sequence", "misunderstood algorithm purpose", "confusing key algorithmic concepts"],
    "Comparative Analysis": ["insufficient comparison points", "one-sided analysis", "overlooked tradeoffs", "missed key differences", "inaccurate relative performance claims"],
    "OOP Principles": ["misinterpreted inheritance", "confused polymorphism", "misunderstood encapsulation", "poorly explained abstraction", "incorrect relationship between principles"],
    "Data Hiding": ["confused visibility modifiers", "misunderstood encapsulation boundaries", "inaccurate access control explanations", "exposed implementation details", "broken information hiding"],
    "Benefits": ["missed practical advantages", "theoretical-only focus", "unsubstantiated benefit claims", "overlooked contextual benefits", "exaggerated advantages"],
    "Data Structure Properties": ["incorrect structural definition", "misunderstood invariants", "confused operation guarantees", "wrong memory layout", "inaccurate traversal patterns"],
    "Operation Description": ["misunderstood insertion process", "incorrect deletion mechanism", "confused update operations", "imprecise access pattern description", "missing edge case handling"],
    "Application Examples": ["irrelevant use cases", "theoretical-only examples", "missing real-world applications", "incorrect usage scenarios", "limited example diversity"],
    "Concept Definition": ["vague definition", "circular reasoning", "incorrect fundamental concept", "confused core principles", "misleading conceptualization"],
    "Base and Recursive Cases": ["missing termination condition", "infinite recursion risk", "poorly defined base case", "inefficient recursive relation", "incorrect recursive step"],
    "Example Implementation": ["non-working example", "inefficient implementation", "overly complex solution", "missing key implementation details", "inappropriate implementation choice"],
    "Algorithm Characteristics": ["mistaken algorithmic properties", "incorrect traversal order", "missed algorithm guarantees", "confused algorithm invariants", "inaccurate runtime behavior"],
    "Implementation Details": ["imprecise data structure usage", "missing implementation steps", "incorrect implementation approach", "inefficient mechanism", "overcomplicated solution"],
    "Application Scenarios": ["inappropriate use cases", "missed key applications", "incorrect best-use scenarios", "incomplete situation analysis", "overlooked limitations"],
    "Algorithm Description": ["incorrect algorithm steps", "incomplete process description", "missing key algorithm phases", "confused operational sequence", "incorrectly ordered steps"],
    "Performance Factors": ["overlooked performance aspects", "incorrect efficiency analysis", "missed bottlenecks", "inaccurate comparative performance", "unaddressed overhead"],
    "Tree Properties": ["misunderstood tree invariants", "incorrect node relationship", "confused tree type properties", "missing structural guarantees", "wrong balance conditions"],
    "Balance Mechanisms": ["incorrect rotation description", "misunderstood rebalancing triggers", "incomplete rebalancing process", "confused balance factor calculation", "inaccurate self-balancing mechanism"],
    "Efficiency Analysis": ["incorrect time complexity", "missed best/worst case scenarios", "overlooked amortized analysis", "flawed performance comparison", "unsubstantiated efficiency claims"],
    "Technique Definition": ["misunderstood fundamental approach", "confused with similar techniques", "vague methodological description", "incorrect process characterization", "imprecise definition"],
    "Implementation Approaches": ["missing key implementation patterns", "confused implementation strategies", "inefficient approach selection", "overlooked optimization techniques", "incorrect tradeoff analysis"],
    "Hashing Fundamentals": ["misunderstood hash function properties", "confused hash table structure", "incorrect hashing principles", "inaccurate description of hash calculation", "flawed hash distribution explanation"],
    "Collision Understanding": ["incorrect collision cause", "confused collision frequency factors", "missed collision probability analysis", "inaccurate collision impact", "overlooked collision patterns"],
    "Resolution Techniques": ["incomplete resolution method description", "confused resolution strategy selection", "incorrect implementation of resolution techniques", "missed performance implications", "inaccurate comparison of approaches"],
    "Normalization Definition": ["misunderstood normalization purpose", "incorrect normalization process", "confused dependency types", "inaccurate redundancy explanation", "flawed normalization reasoning"],
    "Normal Forms": ["incorrect normal form progression", "confused normal form requirements", "incomplete normal form descriptions", "mixed up normalization levels", "missed key normal form properties"],
    "Advantage Analysis": ["unsubstantiated benefits", "missed key advantages", "overlooked practical benefits", "incomplete tradeoff analysis", "exaggerated advantage claims"],
    "Database Paradigms": ["confused database models", "incorrect paradigm characteristics", "misunderstood fundamental approaches", "inaccurate paradigm comparison", "oversimplified model distinctions"],
    "Technical Differences": ["missed key technical distinctions", "incorrect technical comparison", "oversimplified differences", "confused capabilities", "inaccurate feature comparison"],
    "Use Case Analysis": ["inappropriate use case recommendations", "mismatched scenarios", "overlooked ideal applications", "incomplete situation analysis", "wrong use case prioritization"],
    "Transaction Definition": ["misunderstood transaction boundaries", "incorrect transaction properties", "confused transaction states", "incomplete transaction lifecycle", "inaccurate transaction context"],
    "ACID Properties": ["misinterpreted ACID component", "confused property guarantees", "incomplete property explanation", "incorrect property relationship", "mixed up ACID components"],
    "Practical Importance": ["missed real-world relevance", "theoretical-only focus", "unsubstantiated importance claims", "overlooked business implications", "incomplete impact analysis"],
    "Index Functionality": ["incorrect index operation", "misunderstood index structure", "confused lookup mechanism", "inaccurate index utility", "flawed index purpose explanation"],
    "Index Types": ["missed key index varieties", "confused index type properties", "incorrect index selection guidance", "incomplete index type comparison", "wrong index structure description"],
    "Sharding Concept": ["misunderstood horizontal partitioning", "confused with vertical partitioning", "incorrect sharding purpose", "flawed sharding benefit explanation", "inaccurate sharding mechanism"],
    "Implementation Strategy": ["poor strategy selection", "missed key implementation considerations", "incorrect approach to distribution", "flawed partition scheme", "inadequate distribution logic"],
    "Challenge Analysis": ["overlooked key challenges", "underestimated difficulty", "missed critical implementation hurdles", "incomplete problem assessment", "inaccurate difficulty evaluation"],
    "Layer Identification": ["incorrect layer ordering", "missed key layers", "confused layer responsibilities", "inaccurate layer boundaries", "mixed up layer functions"],
    "Protocol Examples": ["incorrect protocol categorization", "missed major protocols", "confused protocol purposes", "inaccurate protocol descriptions", "wrong layer assignments"],
    "Encapsulation Understanding": ["misunderstood data wrapping", "incorrect encapsulation mechanism", "confused protocol field relationships", "inaccurate header description", "flawed encapsulation model"],
    "Protocol Characteristics": ["incorrect protocol behavior", "confused protocol properties", "missed key protocol features", "inaccurate protocol comparison", "wrong protocol guarantees"],
    "Reliability Mechanisms": ["misunderstood reliability features", "incorrect acknowledgment process", "confused flow control", "inaccurate timeout mechanism", "flawed reliability guarantees"],
    "DNS Purpose": ["incorrect name resolution description", "confused DNS role", "incomplete DNS functionality", "inaccurate purpose statement", "misunderstood name system"],
    "Resolution Process": ["incorrect query sequence", "confused resolution steps", "incomplete lookup process", "inaccurate caching behavior", "wrong hierarchy traversal"],
    "Record Types": ["missed important record types", "confused record type purposes", "incorrect record format", "incomplete record function explanation", "mixed up record usages"],
    "Protocol Classification": ["incorrect categorization", "confused protocol types", "inaccurate protocol hierarchy", "misplaced protocols", "wrong classification criteria"],
    "Routing Mechanisms": ["incorrect routing algorithm", "confused route selection process", "incomplete routing decision factors", "inaccurate metric usage", "flawed path determination"],
    "Security Components": ["missed security elements", "confused security layers", "incomplete protection mechanisms", "inaccurate security feature descriptions", "overlooked security aspects"],
    "Handshake Process": ["incorrect handshake sequence", "confused key exchange", "incomplete certificate validation", "inaccurate cipher negotiation", "wrong handshake component order"],
    "Protection Scope": ["misunderstood threat model", "incorrect protection guarantees", "incomplete security coverage", "exaggerated security claims", "overlooked security limitations"],
    "Paradigm Definitions": ["incorrect learning type", "confused learning approaches", "incomplete paradigm description", "mixed up learning categories", "mischaracterized learning methods"],
    "Example Algorithms": ["incorrect algorithm classification", "confused algorithm purposes", "inappropriate algorithm examples", "incomplete algorithm description", "wrong algorithm paradigm"],
    "Error Components": ["incorrect error formula", "confused error sources", "incomplete error breakdown", "misunderstood error relationship", "wrong error contribution"],
    "Mitigation Strategies": ["ineffective strategy selection", "confused mitigation approaches", "incomplete solution set", "inappropriate technique application", "flawed strategy reasoning"],
    "Algorithm Steps": ["incorrect algorithmic sequence", "confused process steps", "incomplete algorithm description", "misordered operations", "missing critical steps"],
    "Gradient Calculation": ["incorrect gradient derivation", "confused partial derivatives", "incomplete chain rule application", "inaccurate backpropagation description", "flawed gradient flow"],
    "Update Mechanism": ["incorrect parameter update", "confused optimization algorithm", "incomplete weight adjustment", "inaccurate learning rate usage", "wrong update direction"],
    "Process Description": ["incorrect transformation process", "confused feature manipulation", "incomplete processing pipeline", "inaccurate feature creation", "wrong methodology description"],
    "Technique Examples": ["inappropriate technique selection", "confused transformation methods", "incomplete technique description", "inaccurate technique application", "wrong technique effect"],
    "Splitting Criteria": ["incorrect impurity measure", "confused split selection", "incomplete criteria explanation", "inaccurate gain calculation", "wrong splitting mechanism"],
    "Tradeoff Analysis": ["missed key tradeoffs", "unbalanced analysis", "incomplete consideration of alternatives", "inaccurate advantage/disadvantage weighting", "oversimplified tradeoff discussion"],
    "Methodology Definition": ["mischaracterized methodology", "confused process framework", "incomplete methodology description", "inaccurate approach characterization", "wrong methodology purpose"],
    "Core Principles": ["missed fundamental principles", "confused value prioritization", "incomplete principle explanation", "inaccurate principle application", "misunderstood guiding values"],
    "Implementation Frameworks": ["incorrect framework classification", "confused methodology implementations", "incomplete framework description", "inaccurate framework comparison", "wrong framework selection"],
    "Practice Definition": ["incorrect practice characterization", "confused practice scope", "incomplete practice description", "inaccurate process definition", "misunderstood practice purpose"],
    "Automation Process": ["incorrect automation sequence", "confused toolchain integration", "incomplete pipeline description", "inaccurate trigger mechanism", "wrong automation flow"],
    "Business Value": ["missed key benefits", "unsubstantiated value claims", "incomplete ROI analysis", "inaccurate benefit attribution", "exaggerated value proposition"],
    "Principle Identification": ["incorrect principle naming", "confused principle boundaries", "incomplete principle explanation", "mixed up principles", "mischaracterized design rules"],
    "Design Implications": ["missed architectural impact", "confused design consequences", "incomplete implication analysis", "inaccurate structure prediction", "wrong design outcome"],
    "Concept Definition": ["vague definition", "circular reasoning", "incorrect fundamental concept", "confused core principles", "misleading conceptualization"],
    "Debt Sources": ["missed common debt causes", "confused technical vs. business debt", "incomplete debt categorization", "inaccurate debt attribution", "wrong debt origination"],
    "Management Strategy": ["ineffective strategy selection", "confused debt priorities", "incomplete management approach", "inappropriate technique application", "flawed strategic reasoning"],
    "Architecture Definition": ["incorrect architectural pattern", "confused architectural style", "incomplete architecture description", "inaccurate structure characterization", "wrong architectural model"],
    "Service Characteristics": ["incorrect service properties", "confused service boundaries", "incomplete service description", "inaccurate service interaction", "wrong service responsibility"]
}

def get_feedback_for_score(score, question, criteria):
    """Generate realistic feedback based on score and question content."""
    # Get appropriate feedback template based on score range
    for score_range, templates in FEEDBACK_TYPES.items():
        if score_range[0] <= score < score_range[1]:
            template = random.choice(templates)
            break
    else:
        # Default to highest range if score is perfect
        template = random.choice(FEEDBACK_TYPES[(85, 100)])
    
    # Extract key concept from question
    words = question.split()
    if len(words) > 5:
        concept = " ".join(words[1:4])  # Use a few key words from question
    else:
        concept = question
    
    # Select issues based on criteria
    if len(criteria) >= 2:
        criteria_names = [c["name"] for c in criteria]
        # Get issues related to the rubric criteria
        potential_issues = []
        for criterion in criteria_names:
            if criterion in COMMON_ISSUES:
                potential_issues.extend(COMMON_ISSUES[criterion])
        
        # Select random issues
        if len(potential_issues) >= 2:
            issue1, issue2 = random.sample(potential_issues, 2)
        else:
            # Fallback to generic issues
            issue1 = "insufficient explanation"
            issue2 = "lack of examples"
    else:
        issue1 = "insufficient explanation"
        issue2 = "lack of examples"
    
    # Format the feedback
    if score >= 85:
        # For high scores, only mention one issue
        feedback = template.format(concept=concept, issue1=issue1)
    else:
        feedback = template.format(concept=concept, issue1=issue1, issue2=issue2)
    
    return feedback

def create_rubric_node(name, description):
    """Create a rubric node or return existing one."""
    # Check if rubric with this name already exists
    rubrics = db.collection('rubrics')
    existing = list(rubrics.find({"name": name, "description": description}))
    
    if existing:
        return existing[0]
    
    # Create new rubric node
    rubric_data = {
        "name": name,
        "description": description,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    rubric_id = rubrics.insert(rubric_data)
    return rubrics.get(rubric_id["_id"])

def connect_feedback_to_rubric(feedback_id, rubric_id):
    """Create an edge between feedback and rubric."""
    affects_criteria = db.collection('affects_criteria')
    
    # Check if connection already exists
    existing = list(db.aql.execute(f"""
    FOR edge IN affects_criteria
        FILTER edge._from == "{feedback_id}" AND edge._to == "{rubric_id}"
        RETURN edge
    """))
    
    if existing:
        return
    
    # Create new edge
    edge_data = {
        "_from": feedback_id,
        "_to": rubric_id,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    affects_criteria.insert(edge_data)

def create_source_material(course_id, name, content):
    """Create a course material source document."""
    materials = db.collection('course_materials')
    
    # Check if material already exists
    existing = list(materials.find({"name": name, "course_id": course_id}))
    if existing:
        return existing[0]
    
    # Create new material
    material_data = {
        "name": name,
        "content": content,
        "course_id": course_id,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    
    material_id = materials.insert(material_data)
    return materials.get(material_id["_id"])

def connect_rubric_to_material(rubric_id, material_id):
    """Connect rubric criteria to relevant source material."""
    related_to = db.collection('related_to')
    
    # Check if connection already exists
    existing = list(db.aql.execute(f"""
    FOR edge IN related_to
        FILTER edge._from == "{rubric_id}" AND edge._to == "{material_id}"
        RETURN edge
    """))
    
    if existing:
        return
    
    # Create new edge
    edge_data = {
        "_from": rubric_id,
        "_to": material_id,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "strength": random.uniform(0.7, 1.0)  # Relevance strength
    }
    
    related_to.insert(edge_data)

def generate_realistic_submissions(course_codes):
    """Generate realistic submissions with questions, answers and feedback."""
    submissions = db.collection('submission')
    courses = db.collection('courses')
    mistakes = db.collection('mistakes')
    
    submission_count = 0
    
    for course_code in course_codes:
        # Get course
        course_list = list(courses.find({"class_code": course_code}))
        if not course_list:
            continue
        
        course = course_list[0]
        course_title = course.get("class_title", "Unknown Course")
        
        # Find matching subject in our data
        subject_data = None
        for subject, questions in SUBJECTS.items():
            if subject.lower() in course_title.lower() or course_title.lower() in subject.lower():
                subject_data = questions
                break
        
        if not subject_data:
            # Use a random subject if no match
            subject_data = random.choice(list(SUBJECTS.values()))
        
        # Get all enrolled students for this course
        user_query = f"""
        FOR user IN users
            FILTER "{course_code}" IN user.courses
            FILTER user.role == "student"
            RETURN user
        """
        students = list(db.aql.execute(user_query))
        
        # Get assignments for this course
        assignments = course.get('assignments', [])
        
        # Create source materials for this course
        materials = {}
        for question_data in subject_data:
            for source_name in question_data["source_materials"]:
                material_content = f"This is a comprehensive resource on {source_name} for {course_title}."
                material = create_source_material(course["_id"], source_name, material_content)
                materials[source_name] = material
        
        # For each student, create submissions
        for student in students:
            # Create 1-3 submissions per student
            for _ in range(random.randint(1, min(3, len(assignments)))):
                # Select a random assignment
                assignment = random.choice(assignments)
                assignment_id = assignment.get('id')
                
                # Check if student already has a submission for this assignment
                existing = list(submissions.find({
                    "user_id": student["_id"],
                    "class_code": course_code,
                    "assignment_id": assignment_id
                }))
                
                if existing:
                    continue
                
                # Select a random question and its data
                question_data = random.choice(subject_data)
                question = question_data["question"]
                answer = question_data["answer"]
                
                # Generate a random score (with more weight to higher scores)
                score_weights = [
                    (0, 50, 10),    # 10% chance of 0-50
                    (50, 70, 20),   # 20% chance of 50-70
                    (70, 85, 40),   # 40% chance of 70-85
                    (85, 100, 30)   # 30% chance of 85-100
                ]
                
                # Choose score range based on weights
                ranges, weights = zip(*[(r[:2], r[2]) for r in score_weights])
                selected_range = random.choices(ranges, weights=weights)[0]
                
                # Generate score within selected range
                score = random.uniform(selected_range[0], selected_range[1])
                
                # Generate feedback based on score
                feedback = get_feedback_for_score(score, question, question_data["rubric_criteria"])
                
                # Create submission
                submission_data = {
                    "user_id": student["_id"],
                    "class_code": course_code,
                    "assignment_id": assignment_id,
                    "file_name": f"submission_{assignment['name']}_{student['username']}.pdf",
                    "file_content": f"Question: {question}\n\nAnswer: {answer}",
                    "submission_date": datetime.datetime.utcnow().isoformat(),
                    "grade": score,
                    "feedback": feedback,
                    "graded": True,
                    "question": question,  # Store original question
                    "student_answer": answer  # Store student answer
                }
                
                submission_id = submissions.insert(submission_data)["_id"]
                submission_count += 1
                
                # Create mistake entry for each submission that scored below 95
                if score < 95:
                    # Create a different mistake for each rubric criterion
                    for criterion in question_data["rubric_criteria"]:
                        criterion_name = criterion["name"]
                        criterion_desc = criterion["description"]
                        
                        # Create the mistake
                        mistake_data = {
                            "question": question,
                            "justification": feedback,
                            "score_awarded": score,
                            "rubric_criteria_names": [criterion_name],
                            "course_code": course_code,
                            "assignment_id": assignment_id
                        }
                        
                        mistake_id = mistakes.insert(mistake_data)["_id"]
                        
                        # Connect student to mistake
                        made_mistake = db.collection('made_mistake')
                        made_mistake.insert({
                            "_from": student["_id"],
                            "_to": mistake_id,
                            "created_at": datetime.datetime.utcnow().isoformat()
                        })
                        
                        # Connect submission to mistake via feedback
                        has_feedback = db.collection('has_feedback_on')
                        has_feedback.insert({
                            "_from": submission_id,
                            "_to": mistake_id,
                            "created_at": datetime.datetime.utcnow().isoformat()
                        })
                        
                        # Create or get rubric node for this criterion
                        rubric = create_rubric_node(criterion_name, criterion_desc)
                        
                        # Connect mistake to rubric
                        connect_feedback_to_rubric(mistake_id, rubric["_id"])
                        
                        # Connect rubric to relevant source materials
                        for source_name in question_data["source_materials"]:
                            if source_name in materials:
                                connect_rubric_to_material(rubric["_id"], materials[source_name]["_id"])
    
    return submission_count

def clear_simulated_data():
    """Clear existing simulated data from the database."""
    collections = [
        'submission', 'mistakes', 'made_mistake', 'affects_criteria', 
        'related_to', 'has_feedback_on', 'course_materials', 'rubrics',
        'has_rubric', 'has_material'
    ]
    
    for collection_name in collections:
        if db.has_collection(collection_name):
            collection = db.collection(collection_name)
            
            # For regular collections, delete simulated documents
            if not collection.properties().get('edge'):
                try:
                    db.aql.execute(f"""
                    FOR doc IN {collection_name}
                        FILTER doc.is_simulated == true OR 
                              HAS(doc, "feedback") AND doc.feedback LIKE "Simulated feedback%"
                        REMOVE doc IN {collection_name}
                    """)
                except:
                    # If no is_simulated field exists, we can't safely delete
                    pass
            else:
                # For edge collections, delete edges connected to missing vertices
                try:
                    db.aql.execute(f"""
                    FOR edge IN {collection_name}
                        LET from_exists = DOCUMENT_EXISTS(edge._from)
                        LET to_exists = DOCUMENT_EXISTS(edge._to)
                        FILTER !from_exists OR !to_exists
                        REMOVE edge IN {collection_name}
                    """)
                except:
                    pass

def regenerate_data():
    """Main function to regenerate all data."""
    # First clear existing simulation data
    clear_simulated_data()
    
    # Get all course codes
    courses = db.collection('courses')
    course_docs = list(courses.all())
    course_codes = [doc["class_code"] for doc in course_docs if "class_code" in doc]
    
    # Generate new submissions with realistic data
    submission_count = generate_realistic_submissions(course_codes)
    
    return {
        "course_count": len(course_codes),
        "submission_count": submission_count
    }

if __name__ == "__main__":
    result = regenerate_data()
    print(f"Generated {result['submission_count']} realistic submissions for {result['course_count']} courses.")