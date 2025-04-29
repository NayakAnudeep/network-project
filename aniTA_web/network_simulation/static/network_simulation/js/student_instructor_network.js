// Student-Instructor Network Visualization with D3.js
document.addEventListener('DOMContentLoaded', function() {
    // Load network data
    loadNetworkData();
    
    // Set up refresh button
    document.getElementById('refreshData').addEventListener('click', function() {
        loadNetworkData();
    });
    
    // Setup export buttons
    document.getElementById('exportPNG').addEventListener('click', exportAsPNG);
    document.getElementById('exportData').addEventListener('click', exportNetworkData);
    document.getElementById('exportMetrics').addEventListener('click', exportMetricsCSV);
    
    // Fetch and display network data
    function loadNetworkData() {
        showLoading();
        
        fetch('/network/api/student-instructor-network/')
            .then(response => response.json())
            .then(data => {
                // Update metrics
                updateNetworkMetrics(data.network_metrics);
                
                // Update tables
                updateTopInstructorsTable(data.top_instructors);
                updateTopStudentsTable(data.top_students);
                
                // Initialize or update the network visualization
                initNetworkGraph(data);
                
                hideLoading();
            })
            .catch(error => {
                console.error('Error fetching network data:', error);
                showError('Failed to load network data. Please try again later.');
                hideLoading();
            });
    }
    
    // Update network metrics display
    function updateNetworkMetrics(metrics) {
        const metricsContainer = document.getElementById('networkMetrics');
        metricsContainer.innerHTML = '';
        
        const metricItems = [
            { label: 'Total Nodes', value: metrics.node_count },
            { label: 'Total Connections', value: metrics.edge_count },
            { label: 'Student Count', value: metrics.student_count },
            { label: 'Instructor Count', value: metrics.instructor_count },
            { label: 'Avg. Connections per Student', value: metrics.avg_connections_per_student.toFixed(1) },
            { label: 'Avg. Connections per Instructor', value: metrics.avg_connections_per_instructor.toFixed(1) }
        ];
        
        metricItems.forEach(item => {
            const li = document.createElement('li');
            li.className = 'd-flex justify-content-between';
            li.innerHTML = `<span>${item.label}</span><strong>${item.value}</strong>`;
            metricsContainer.appendChild(li);
        });
    }
    
    // Update top instructors table
    function updateTopInstructorsTable(instructors) {
        const tableBody = document.getElementById('topInstructorsTable');
        tableBody.innerHTML = '';
        
        instructors.forEach(instructor => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><a href="/network/dashboard/instructor/${instructor.id}">${instructor.name}</a></td>
                <td>${instructor.student_count}</td>
                <td>${instructor.avg_grade ? instructor.avg_grade.toFixed(1) : 'N/A'}</td>
            `;
            tableBody.appendChild(tr);
        });
        
        if (instructors.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="3" class="text-center">No data available</td>';
            tableBody.appendChild(tr);
        }
    }
    
    // Update top students table
    function updateTopStudentsTable(students) {
        const tableBody = document.getElementById('topStudentsTable');
        tableBody.innerHTML = '';
        
        students.forEach(student => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><a href="/network/dashboard/student/${student.id}">${student.name}</a></td>
                <td>${student.instructor_count}</td>
                <td>${student.gpa ? student.gpa.toFixed(2) : 'N/A'}</td>
            `;
            tableBody.appendChild(tr);
        });
        
        if (students.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="3" class="text-center">No data available</td>';
            tableBody.appendChild(tr);
        }
    }
    
    // Initialize or update D3 network graph
    function initNetworkGraph(data) {
        // Network container dimensions
        const container = document.getElementById('networkGraph');
        const containerRect = container.getBoundingClientRect();
        const width = containerRect.width;
        const height = 600;
        
        // Clear previous graph
        container.innerHTML = '';
        
        // Create SVG element
        const svg = d3.select('#networkGraph')
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        // Define color scale for node types
        const color = d3.scaleOrdinal()
            .domain([1, 2])  // 1 = instructor, 2 = student
            .range(['#9c4dcc', '#48BFE3']);
        
        // Create simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-400))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collide', d3.forceCollide().radius(d => d.group === 1 ? 25 : 10).iterations(2));
        
        // Create links
        const link = svg.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(data.links)
            .enter().append('line')
            .attr('stroke-width', d => Math.sqrt(d.weight))
            .attr('stroke', '#aaa');
        
        // Create node groups
        const node = svg.append('g')
            .attr('class', 'nodes')
            .selectAll('g')
            .data(data.nodes)
            .enter().append('g')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        // Add circle to each node
        node.append('circle')
            .attr('r', d => d.group === 1 ? 15 : 8)  // Instructors larger than students
            .attr('fill', d => color(d.group))
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5);
        
        // Add text labels to nodes
        node.append('text')
            .attr('dy', d => d.group === 1 ? -20 : -10)
            .attr('text-anchor', 'middle')
            .attr('font-size', d => d.group === 1 ? '12px' : '10px')
            .text(d => d.name)
            .attr('fill', '#333');
        
        // Add interactivity
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
                .attr('transform', d => {
                    // Keep nodes within bounds
                    d.x = Math.max(20, Math.min(width - 20, d.x));
                    d.y = Math.max(20, Math.min(height - 20, d.y));
                    return `translate(${d.x},${d.y})`;
                });
        });
        
        // Drag functions
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
    }
    
    // Export as PNG
    function exportAsPNG() {
        const svg = document.querySelector('#networkGraph svg');
        if (!svg) {
            alert('No network graph available to export.');
            return;
        }
        
        const svgData = new XMLSerializer().serializeToString(svg);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = svg.width.baseVal.value;
        canvas.height = svg.height.baseVal.value;
        
        const img = new Image();
        img.onload = function() {
            ctx.drawImage(img, 0, 0);
            const a = document.createElement('a');
            a.download = 'student_instructor_network.png';
            a.href = canvas.toDataURL('image/png');
            a.click();
        };
        
        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    }
    
    // Export network data as JSON
    function exportNetworkData() {
        fetch('/network/api/student-instructor-network/')
            .then(response => response.json())
            .then(data => {
                const exportData = {
                    nodes: data.nodes,
                    links: data.links
                };
                
                const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(exportData, null, 2));
                const a = document.createElement('a');
                a.href = dataStr;
                a.download = 'student_instructor_network.json';
                a.click();
            })
            .catch(error => {
                console.error('Error exporting network data:', error);
                alert('Failed to export network data. Please try again later.');
            });
    }
    
    // Export metrics as CSV
    function exportMetricsCSV() {
        fetch('/network/api/student-instructor-network/')
            .then(response => response.json())
            .then(data => {
                const metrics = data.network_metrics;
                const csv = 'Metric,Value\n' +
                    `Total Nodes,${metrics.node_count}\n` +
                    `Total Connections,${metrics.edge_count}\n` +
                    `Student Count,${metrics.student_count}\n` +
                    `Instructor Count,${metrics.instructor_count}\n` +
                    `Avg. Connections per Student,${metrics.avg_connections_per_student.toFixed(1)}\n` +
                    `Avg. Connections per Instructor,${metrics.avg_connections_per_instructor.toFixed(1)}`;
                
                const dataStr = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
                const a = document.createElement('a');
                a.href = dataStr;
                a.download = 'student_instructor_network_metrics.csv';
                a.click();
            })
            .catch(error => {
                console.error('Error exporting metrics data:', error);
                alert('Failed to export metrics data. Please try again later.');
            });
    }
    
    // Helper function to show loading indicators
    function showLoading() {
        document.getElementById('networkMetrics').innerHTML = `
            <li class="d-flex justify-content-between">
                <span>Loading metrics...</span>
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </li>
        `;
        
        document.getElementById('topInstructorsTable').innerHTML = `
            <tr>
                <td colspan="3" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </td>
            </tr>
        `;
        
        document.getElementById('topStudentsTable').innerHTML = `
            <tr>
                <td colspan="3" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </td>
            </tr>
        `;
    }
    
    // Helper function to hide loading indicators and show error
    function showError(message) {
        document.getElementById('networkMetrics').innerHTML = `
            <li class="d-flex justify-content-between">
                <span class="text-danger">${message}</span>
                <button class="btn btn-sm btn-outline-danger" onclick="loadNetworkData()">
                    <i class="fas fa-sync-alt"></i> Retry
                </button>
            </li>
        `;
        
        document.getElementById('topInstructorsTable').innerHTML = `
            <tr>
                <td colspan="3" class="text-center text-danger">${message}</td>
            </tr>
        `;
        
        document.getElementById('topStudentsTable').innerHTML = `
            <tr>
                <td colspan="3" class="text-center text-danger">${message}</td>
            </tr>
        `;
    }
    
    // Helper function to hide loading indicators
    function hideLoading() {
        // This is handled by the data update functions
    }
});