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
    
    // Convert links/nodes format to edges/nodes if needed
    if (data.links && !data.edges) {
        data.edges = data.links;
    }
    
    console.log("Creating student-instructor network with data:", data);
    console.log("Nodes:", data.nodes);
    console.log("Edges:", data.edges);
    
    try {
        // Make deep copies to avoid modifying original data
        const nodes = JSON.parse(JSON.stringify(data.nodes));
        const edges = JSON.parse(JSON.stringify(data.edges));
        
        // Ensure nodes have id property
        nodes.forEach(node => {
            if (!node.id && node.name) {
                // If no id but has name, use name as id
                node.id = node.name;
            }
        });
        
        // Fix source/target references if they're not IDs but indices
        edges.forEach(edge => {
            // If source/target are numbers, treat as indices
            if (typeof edge.source === 'number') {
                edge.source = nodes[edge.source].id;
            }
            if (typeof edge.target === 'number') {
                edge.target = nodes[edge.target].id;
            }
            
            // If source/target are objects, extract id
            if (typeof edge.source === 'object' && edge.source !== null) {
                edge.source = edge.source.id;
            }
            if (typeof edge.target === 'object' && edge.target !== null) {
                edge.target = edge.target.id;
            }
        });
        
        const svg = d3.select('#' + containerId)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('class', 'network-svg');
        
        // Create force simulation
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(edges).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(50));
    
    // Add links
    const link = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(edges)
        .enter()
        .append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', d => Math.sqrt(d.weight || 1));
    
    // Create node groups
    const node = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('.node')
        .data(nodes)
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
    
    // Return the simulation object
    return simulation;
    
    } catch (error) {
        console.error("Error creating student-instructor network visualization:", error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error creating visualization: ${error.message}
            </div>
            <div class="text-center">
                <svg width="100%" height="400" viewBox="0 0 800 400">
                    <g transform="translate(400, 200)">
                        <!-- Simplified network visualization -->
                        <circle cx="-250" cy="-100" r="15" fill="#ff6347" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="-232" y="-100" font-size="12px">Instructor 1</text>
                        
                        <circle cx="-150" cy="-150" r="15" fill="#ff6347" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="-132" y="-150" font-size="12px">Instructor 2</text>
                        
                        <circle cx="-50" cy="-120" r="15" fill="#ff6347" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="-32" y="-120" font-size="12px">Instructor 3</text>
                        
                        <circle cx="50" cy="-150" r="15" fill="#ff6347" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="68" y="-150" font-size="12px">Instructor 4</text>
                        
                        <circle cx="150" cy="-100" r="15" fill="#ff6347" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="168" y="-100" font-size="12px">Instructor 5</text>
                        
                        <circle cx="-200" cy="0" r="8" fill="#4682b4" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="-188" y="0" font-size="10px">Student 1</text>
                        
                        <circle cx="-100" cy="50" r="8" fill="#4682b4" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="-88" y="50" font-size="10px">Student 2</text>
                        
                        <circle cx="0" cy="0" r="8" fill="#4682b4" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="12" y="0" font-size="10px">Student 3</text>
                        
                        <circle cx="100" cy="50" r="8" fill="#4682b4" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="112" y="50" font-size="10px">Student 4</text>
                        
                        <circle cx="200" cy="0" r="8" fill="#4682b4" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="212" y="0" font-size="10px">Student 5</text>
                        
                        <circle cx="-180" cy="100" r="8" fill="#4682b4" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="-168" y="100" font-size="10px">Student 6</text>
                        
                        <circle cx="-60" cy="120" r="8" fill="#4682b4" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="-48" y="120" font-size="10px">Student 7</text>
                        
                        <circle cx="60" cy="120" r="8" fill="#4682b4" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="72" y="120" font-size="10px">Student 8</text>
                        
                        <circle cx="180" cy="100" r="8" fill="#4682b4" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="192" y="100" font-size="10px">Student 9</text>
                        
                        <!-- Connections -->
                        <line x1="-250" y1="-100" x2="-200" y2="0" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="-250" y1="-100" x2="-100" y2="50" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="-150" y1="-150" x2="-200" y2="0" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="-150" y1="-150" x2="0" y2="0" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="-50" y1="-120" x2="-100" y2="50" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="-50" y1="-120" x2="0" y2="0" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="50" y1="-150" x2="0" y2="0" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="50" y1="-150" x2="100" y2="50" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="150" y1="-100" x2="100" y2="50" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="150" y1="-100" x2="200" y2="0" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="-50" y1="-120" x2="-180" y2="100" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="-150" y1="-150" x2="-60" y2="120" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="50" y1="-150" x2="60" y2="120" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        <line x1="150" y1="-100" x2="180" y2="100" stroke="#999" stroke-width="1" stroke-opacity="0.6"></line>
                        
                        <!-- Legend -->
                        <g transform="translate(-350, -180)">
                            <circle cx="0" cy="0" r="15" fill="#ff6347" stroke="#fff" stroke-width="1.5"></circle>
                            <text x="25" y="5" font-size="12px">Instructor</text>
                            <circle cx="0" cy="30" r="8" fill="#4682b4" stroke="#fff" stroke-width="1.5"></circle>
                            <text x="25" y="35" font-size="10px">Student</text>
                        </g>
                    </g>
                </svg>
            </div>
        `;
        
        // Still return a dummy object to avoid errors
        return { stop: () => {} };
    }
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
    
    // Convert links/nodes format to edges/nodes if needed
    if (data.links && !data.edges) {
        data.edges = data.links;
    }
    
    console.log("Creating course network with data:", data);
    console.log("Nodes:", data.nodes);
    console.log("Edges:", data.edges);
    
    try {
        // Make deep copies to avoid modifying original data
        const nodes = JSON.parse(JSON.stringify(data.nodes));
        const edges = JSON.parse(JSON.stringify(data.edges));
        
        // Ensure nodes have id property
        nodes.forEach(node => {
            if (!node.id && node.name) {
                // If no id but has name, use name as id
                node.id = node.name;
            }
        });
        
        // Fix source/target references if they're not IDs but indices
        edges.forEach(edge => {
            // If source/target are numbers, treat as indices
            if (typeof edge.source === 'number') {
                edge.source = nodes[edge.source].id;
            }
            if (typeof edge.target === 'number') {
                edge.target = nodes[edge.target].id;
            }
            
            // If source/target are objects, extract id
            if (typeof edge.source === 'object' && edge.source !== null) {
                edge.source = edge.source.id;
            }
            if (typeof edge.target === 'object' && edge.target !== null) {
                edge.target = edge.target.id;
            }
        });
        
        const svg = d3.select('#' + containerId)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .attr('class', 'network-svg');
        
        // Create force simulation
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(edges).id(d => d.id).distance(150))
            .force('charge', d3.forceManyBody().strength(-400))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(60));
    
    // Add links
    const link = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(edges)
        .enter()
        .append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', d => Math.sqrt(d.weight || 1) * 2);
    
    // Create node groups
    const node = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('.node')
        .data(nodes)
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
    
    // Return the simulation object
    return simulation;
    
    } catch (error) {
        console.error("Error creating course network visualization:", error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error creating visualization: ${error.message}
            </div>
            <div class="text-center">
                <svg width="100%" height="400" viewBox="0 0 800 400">
                    <g transform="translate(400, 200)">
                        <!-- Simplified network visualization -->
                        <circle cx="-200" cy="-100" r="20" fill="#8bc34a" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="-200" y="-100" text-anchor="middle" dy=".35em" font-size="10px">Course 1</text>
                        
                        <circle cx="-100" cy="-150" r="20" fill="#8bc34a" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="-100" y="-150" text-anchor="middle" dy=".35em" font-size="10px">Course 2</text>
                        
                        <circle cx="0" cy="-100" r="20" fill="#8bc34a" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="0" y="-100" text-anchor="middle" dy=".35em" font-size="10px">Course 3</text>
                        
                        <circle cx="100" cy="-150" r="20" fill="#8bc34a" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="100" y="-150" text-anchor="middle" dy=".35em" font-size="10px">Course 4</text>
                        
                        <circle cx="200" cy="-100" r="20" fill="#8bc34a" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="200" y="-100" text-anchor="middle" dy=".35em" font-size="10px">Course 5</text>
                        
                        <circle cx="-200" cy="50" r="20" fill="#8bc34a" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="-200" y="50" text-anchor="middle" dy=".35em" font-size="10px">Course 6</text>
                        
                        <circle cx="-100" cy="100" r="20" fill="#8bc34a" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="-100" y="100" text-anchor="middle" dy=".35em" font-size="10px">Course 7</text>
                        
                        <circle cx="0" cy="50" r="20" fill="#8bc34a" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="0" y="50" text-anchor="middle" dy=".35em" font-size="10px">Course 8</text>
                        
                        <circle cx="100" cy="100" r="20" fill="#8bc34a" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="100" y="100" text-anchor="middle" dy=".35em" font-size="10px">Course 9</text>
                        
                        <circle cx="200" cy="50" r="20" fill="#8bc34a" stroke="#fff" stroke-width="1.5"></circle>
                        <text x="200" y="50" text-anchor="middle" dy=".35em" font-size="10px">Course 10</text>
                        
                        <!-- Connections -->
                        <line x1="-200" y1="-100" x2="-100" y2="-150" stroke="#999" stroke-width="2" stroke-opacity="0.6"></line>
                        <line x1="-100" y1="-150" x2="200" y2="50" stroke="#999" stroke-width="2" stroke-opacity="0.6"></line>
                        <line x1="0" y1="-100" x2="100" y2="-150" stroke="#999" stroke-width="2" stroke-opacity="0.6"></line>
                        <line x1="0" y1="-100" x2="0" y2="50" stroke="#999" stroke-width="2" stroke-opacity="0.6"></line>
                        <line x1="0" y1="-100" x2="-200" y2="50" stroke="#999" stroke-width="2" stroke-opacity="0.6"></line>
                        <line x1="100" y1="-150" x2="100" y2="100" stroke="#999" stroke-width="2" stroke-opacity="0.6"></line>
                        <line x1="200" y1="-100" x2="200" y2="50" stroke="#999" stroke-width="2" stroke-opacity="0.6"></line>
                        <line x1="-200" y1="50" x2="-100" y2="100" stroke="#999" stroke-width="2" stroke-opacity="0.6"></line>
                        <line x1="-100" y1="100" x2="0" y2="50" stroke="#999" stroke-width="2" stroke-opacity="0.6"></line>
                        <line x1="0" y1="50" x2="200" y2="50" stroke="#999" stroke-width="2" stroke-opacity="0.6"></line>
                        <line x1="100" y1="100" x2="200" y2="50" stroke="#999" stroke-width="2" stroke-opacity="0.6"></line>
                    </g>
                </svg>
            </div>
        `;
        
        // Still return a dummy object to avoid errors
        return { stop: () => {} };
    }
    
    return simulation;
}