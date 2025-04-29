/**
 * Network Visualizations using D3.js
 * 
 * This file provides D3-based visualizations for the network simulation module.
 */

/**
 * Creates a student-instructor network visualization
 * @param {string} containerId - The ID of the container element
 * @param {Object} data - The network data with nodes and edges
 */
function createStudentInstructorNetwork(containerId, data) {
    // Clear existing content
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (!data || !data.nodes || !data.edges || data.nodes.length === 0) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                No network data available.
            </div>
        `;
        return;
    }
    
    // Set up SVG container
    const width = container.clientWidth;
    const height = 500;
    
    const svg = d3.select('#' + containerId)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'network-svg');
    
    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.edges).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(50));
    
    // Add links
    const link = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(data.edges)
        .enter()
        .append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', d => Math.sqrt(d.weight || 1));
    
    // Create node groups
    const node = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('.node')
        .data(data.nodes)
        .enter()
        .append('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragging)
            .on('end', dragEnded));
    
    // Add circles for nodes
    node.append('circle')
        .attr('r', d => (d.type === 'instructor' ? 15 : 8))
        .attr('fill', d => (d.type === 'instructor' ? '#ff6347' : '#4682b4'))
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5);
    
    // Add labels
    node.append('text')
        .attr('dx', d => (d.type === 'instructor' ? 18 : 12))
        .attr('dy', '.35em')
        .attr('font-size', d => (d.type === 'instructor' ? '12px' : '10px'))
        .text(d => d.name);
    
    // Add tooltips
    node.append('title')
        .text(d => `${d.name} (${d.type})`);
    
    // Update positions on each tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('transform', d => `translate(${d.x},${d.y})`);
    });
    
    // Drag functions
    function dragStarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragging(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragEnded(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    return simulation;
}

/**
 * Creates a course network visualization
 * @param {string} containerId - The ID of the container element
 * @param {Object} data - The network data with nodes and edges
 */
function createCourseNetwork(containerId, data) {
    // Clear existing content
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (!data || !data.nodes || !data.edges || data.nodes.length === 0) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                No network data available.
            </div>
        `;
        return;
    }
    
    // Set up SVG container
    const width = container.clientWidth;
    const height = 500;
    
    const svg = d3.select('#' + containerId)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'network-svg');
    
    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.edges).id(d => d.id).distance(150))
        .force('charge', d3.forceManyBody().strength(-400))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(60));
    
    // Add links
    const link = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(data.edges)
        .enter()
        .append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', d => Math.sqrt(d.weight || 1) * 2);
    
    // Create node groups
    const node = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('.node')
        .data(data.nodes)
        .enter()
        .append('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragging)
            .on('end', dragEnded));
    
    // Add circles for nodes
    node.append('circle')
        .attr('r', 20)
        .attr('fill', '#8bc34a')
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5);
    
    // Add labels
    node.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '.35em')
        .attr('font-size', '10px')
        .text(d => d.name);
    
    // Add tooltips
    node.append('title')
        .text(d => d.name);
    
    // Update positions on each tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('transform', d => `translate(${d.x},${d.y})`);
    });
    
    // Drag functions
    function dragStarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragging(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragEnded(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    return simulation;
}