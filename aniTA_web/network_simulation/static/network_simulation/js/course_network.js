// Course Network Visualization with D3.js and Chart.js
document.addEventListener('DOMContentLoaded', function() {
    // Charts for course data
    let courseEnrollmentChart = null;
    let courseGradesChart = null;
    
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
        
        fetch('/network/api/course-network/')
            .then(response => response.json())
            .then(data => {
                // Update metrics
                updateNetworkMetrics(data.network_metrics);
                
                // Update charts
                updateCourseEnrollmentChart(data.course_enrollment);
                updateCourseGradesChart(data.course_grades);
                
                // Update course connections table
                updateCourseConnectionsTable(data.course_connections);
                
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
            { label: 'Total Courses', value: metrics.node_count },
            { label: 'Total Connections', value: metrics.edge_count },
            { label: 'Avg. Connections per Course', value: metrics.avg_connections_per_course.toFixed(1) },
            { label: 'Most Connected Course', value: metrics.most_connected_course }
        ];
        
        metricItems.forEach(item => {
            const li = document.createElement('li');
            li.className = 'd-flex justify-content-between';
            li.innerHTML = `<span>${item.label}</span><strong>${item.value}</strong>`;
            metricsContainer.appendChild(li);
        });
    }
    
    // Update course enrollment chart
    function updateCourseEnrollmentChart(enrollmentData) {
        const ctx = document.getElementById('courseEnrollmentChart').getContext('2d');
        
        // Sort by student count (descending)
        enrollmentData.sort((a, b) => b.student_count - a.student_count);
        
        // Prepare data for chart
        const labels = enrollmentData.map(item => item.name);
        const data = enrollmentData.map(item => item.student_count);
        
        // Destroy previous chart if it exists
        if (courseEnrollmentChart) {
            courseEnrollmentChart.destroy();
        }
        
        // Create new chart
        courseEnrollmentChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Student Enrollment',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Students'
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Students: ${context.raw}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Update course grades chart
    function updateCourseGradesChart(gradesData) {
        const ctx = document.getElementById('courseGradesChart').getContext('2d');
        
        // Sort by average grade (descending)
        gradesData.sort((a, b) => b.avg_grade - a.avg_grade);
        
        // Prepare data for chart
        const labels = gradesData.map(item => item.name);
        const data = gradesData.map(item => item.avg_grade);
        
        // Destroy previous chart if it exists
        if (courseGradesChart) {
            courseGradesChart.destroy();
        }
        
        // Create new chart
        courseGradesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Average Grade',
                    data: data,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Average Grade'
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Avg. Grade: ${context.raw.toFixed(1)}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Update course connections table
    function updateCourseConnectionsTable(connections) {
        const tableBody = document.getElementById('courseConnectionsTable');
        tableBody.innerHTML = '';
        
        // Sort by shared students count (descending)
        connections.sort((a, b) => b.shared_students - a.shared_students);
        
        // Take top 10 connections
        connections.slice(0, 10).forEach(connection => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><a href="/network/dashboard/course/${connection.source}">${connection.source_name}</a></td>
                <td><a href="/network/dashboard/course/${connection.target}">${connection.target_name}</a></td>
                <td>${connection.shared_students}</td>
                <td>
                    <div class="progress" style="height: 10px;">
                        <div class="progress-bar" role="progressbar" style="width: ${Math.min(connection.shared_students * 5, 100)}%;" 
                            aria-valuenow="${connection.shared_students}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                </td>
            `;
            tableBody.appendChild(tr);
        });
        
        if (connections.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="4" class="text-center">No course connections found</td>';
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
        
        // Create simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(150))
            .force('charge', d3.forceManyBody().strength(-800))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collide', d3.forceCollide().radius(40).iterations(2));
        
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
        
        // Add rectangles to each node (courses are represented as rectangles)
        node.append('rect')
            .attr('width', 120)
            .attr('height', 40)
            .attr('x', -60)
            .attr('y', -20)
            .attr('rx', 5)
            .attr('ry', 5)
            .attr('fill', '#0d6efd')
            .attr('stroke', '#0a58ca')
            .attr('stroke-width', 2);
        
        // Add text labels to nodes
        node.append('text')
            .attr('dy', 5)
            .attr('text-anchor', 'middle')
            .attr('font-size', '12px')
            .text(d => d.name)
            .attr('fill', '#fff');
        
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
                    d.x = Math.max(60, Math.min(width - 60, d.x));
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
            a.download = 'course_network.png';
            a.href = canvas.toDataURL('image/png');
            a.click();
        };
        
        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    }
    
    // Export network data as JSON
    function exportNetworkData() {
        fetch('/network/api/course-network/')
            .then(response => response.json())
            .then(data => {
                const exportData = {
                    nodes: data.nodes,
                    links: data.links
                };
                
                const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(exportData, null, 2));
                const a = document.createElement('a');
                a.href = dataStr;
                a.download = 'course_network.json';
                a.click();
            })
            .catch(error => {
                console.error('Error exporting network data:', error);
                alert('Failed to export network data. Please try again later.');
            });
    }
    
    // Export metrics as CSV
    function exportMetricsCSV() {
        fetch('/network/api/course-network/')
            .then(response => response.json())
            .then(data => {
                const metrics = data.network_metrics;
                const csv = 'Metric,Value\n' +
                    `Total Courses,${metrics.node_count}\n` +
                    `Total Connections,${metrics.edge_count}\n` +
                    `Avg. Connections per Course,${metrics.avg_connections_per_course.toFixed(1)}\n` +
                    `Most Connected Course,${metrics.most_connected_course}`;
                
                const dataStr = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
                const a = document.createElement('a');
                a.href = dataStr;
                a.download = 'course_network_metrics.csv';
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
        
        document.getElementById('courseConnectionsTable').innerHTML = `
            <tr>
                <td colspan="4" class="text-center">
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
        
        document.getElementById('courseConnectionsTable').innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger">${message}</td>
            </tr>
        `;
    }
    
    // Helper function to hide loading indicators
    function hideLoading() {
        // This is handled by the data update functions
    }
});