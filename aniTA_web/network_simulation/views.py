from django.shortcuts import render
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

def index(request):
    """Network simulation landing page"""
    return render(request, 'network_simulation/index.html', {
        'title': 'Network Analysis Dashboard'
    })

def network_dashboard(request):
    """Main dashboard for network analytics"""
    # Create a sample network graph
    G = nx.erdos_renyi_graph(50, 0.1)
    
    # Convert graph to visualization
    plt.figure(figsize=(10, 8))
    nx.draw(G, with_labels=False, node_color='lightblue', 
            node_size=50, alpha=0.8, edgecolors='gray')
    
    # Save plot to a base64 encoded image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    return render(request, 'network_simulation/dashboard.html', {
        'title': 'Network Dashboard',
        'graph_image': graph_image,
        'node_count': G.number_of_nodes(),
        'edge_count': G.number_of_edges()
    })

def student_network(request):
    """Visualize student interactions network"""
    # Placeholder for actual student network logic
    return render(request, 'network_simulation/student_network.html', {
        'title': 'Student Interaction Network'
    })

def course_network(request):
    """Visualize course relationships network"""
    # Placeholder for actual course network logic
    return render(request, 'network_simulation/course_network.html', {
        'title': 'Course Relationship Network'
    })