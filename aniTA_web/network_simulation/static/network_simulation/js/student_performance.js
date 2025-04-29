// Student Performance Visualization with Chart.js
document.addEventListener('DOMContentLoaded', function() {
    // Charts for student performance data
    let gpaDistributionChart = null;
    let gradeDistributionChart = null;
    let assessmentTypeChart = null;
    let yearPerformanceChart = null;
    let timeSeriesChart = null;
    
    // Load performance data
    loadPerformanceData();
    
    // Set up refresh button
    document.getElementById('refreshData').addEventListener('click', function() {
        loadPerformanceData();
    });
    
    // Setup export buttons
    document.getElementById('exportCharts').addEventListener('click', exportChartsAsPNG);
    document.getElementById('exportData').addEventListener('click', exportPerformanceData);
    
    // Setup course filter for top students
    document.getElementById('topStudentsFilter').addEventListener('change', function() {
        // In a full implementation, this would filter the top students table by course
        // For now, we'll just reload the data
        loadPerformanceData();
    });
    
    // Fetch and display performance data
    function loadPerformanceData() {
        showLoading();
        
        fetch('/network/api/student-performance/')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Received data:", data);
                
                // Check if there's an error in the response
                if (data.error) {
                    console.error("API Error:", data.error);
                    throw new Error(data.error);
                }
                
                // Update all visualizations with the fetched data
                if (data.gpa_distribution) {
                    updateGPADistributionChart(data.gpa_distribution);
                } else {
                    console.warn("No GPA distribution data");
                    // Create mock data if needed
                    updateGPADistributionChart({
                        labels: ["2.0-2.5", "2.5-3.0", "3.0-3.5", "3.5-4.0"],
                        data: [15, 25, 35, 25]
                    });
                }
                
                if (data.grade_distribution) {
                    updateGradeDistributionChart(data.grade_distribution);
                } else {
                    console.warn("No grade distribution data");
                    // Create mock data if needed
                    updateGradeDistributionChart({
                        labels: ["F (0-60)", "D (60-70)", "C (70-80)", "B (80-90)", "A (90-100)"],
                        data: [5, 10, 25, 40, 20]
                    });
                }
                
                if (data.top_students) {
                    updateTopStudentsTable(data.top_students);
                } else {
                    console.warn("No top students data");
                    // Create mock data if needed
                    updateTopStudentsTable([
                        {id: "1", name: "Student 1", year: 3, gpa: 3.95},
                        {id: "2", name: "Student 2", year: 4, gpa: 3.92},
                        {id: "3", name: "Student 3", year: 3, gpa: 3.89}
                    ]);
                }
                
                if (data.assessment_types) {
                    updateAssessmentTypeChart(data.assessment_types);
                } else {
                    console.warn("No assessment types data");
                    // Create mock data if needed
                    updateAssessmentTypeChart({
                        labels: ["Quiz", "Exam", "Homework", "Project"],
                        scores: [85, 78, 90, 92],
                        counts: [20, 10, 35, 5]
                    });
                }
                
                if (data.time_series) {
                    updateTimeSeriesChart(data.time_series);
                } else {
                    console.warn("No time series data");
                    // Create mock data if needed
                    updateTimeSeriesChart({
                        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                        data: [75, 80, 82, 78, 85, 88]
                    });
                }
                
                // Update year performance chart (this uses simulated data for now)
                updateYearPerformanceChart();
                
                hideLoading();
            })
            .catch(error => {
                console.error('Error fetching performance data:', error);
                showError('Failed to load performance data: ' + error.message);
                
                // Create all charts with mock data on error
                updateGPADistributionChart({
                    labels: ["2.0-2.5", "2.5-3.0", "3.0-3.5", "3.5-4.0"],
                    data: [15, 25, 35, 25]
                });
                updateGradeDistributionChart({
                    labels: ["F (0-60)", "D (60-70)", "C (70-80)", "B (80-90)", "A (90-100)"],
                    data: [5, 10, 25, 40, 20]
                });
                updateAssessmentTypeChart({
                    labels: ["Quiz", "Exam", "Homework", "Project"],
                    scores: [85, 78, 90, 92],
                    counts: [20, 10, 35, 5]
                });
                updateTimeSeriesChart({
                    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                    data: [75, 80, 82, 78, 85, 88]
                });
                updateYearPerformanceChart();
                
                hideLoading();
            });
    }
    
    // Update GPA distribution chart
    function updateGPADistributionChart(distributionData) {
        const ctx = document.getElementById('gpaDistributionChart').getContext('2d');
        
        // Destroy previous chart if it exists
        if (gpaDistributionChart) {
            gpaDistributionChart.destroy();
        }
        
        // Create new chart
        gpaDistributionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: distributionData.labels,
                datasets: [{
                    label: 'Number of Students',
                    data: distributionData.data,
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
                        title: {
                            display: true,
                            text: 'GPA Range'
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
    
    // Update grade distribution chart
    function updateGradeDistributionChart(distributionData) {
        const ctx = document.getElementById('gradeDistributionChart').getContext('2d');
        
        // Destroy previous chart if it exists
        if (gradeDistributionChart) {
            gradeDistributionChart.destroy();
        }
        
        // Create new chart
        gradeDistributionChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: distributionData.labels,
                datasets: [{
                    data: distributionData.data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',   // F
                        'rgba(255, 159, 64, 0.7)',   // D
                        'rgba(255, 205, 86, 0.7)',   // C
                        'rgba(75, 192, 192, 0.7)',   // B
                        'rgba(54, 162, 235, 0.7)'    // A
                    ],
                    borderColor: [
                        'rgb(255, 99, 132)',
                        'rgb(255, 159, 64)',
                        'rgb(255, 205, 86)',
                        'rgb(75, 192, 192)',
                        'rgb(54, 162, 235)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((context.raw / total) * 100);
                                return `${context.label}: ${context.raw} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Update top students table
    function updateTopStudentsTable(students) {
        const tableBody = document.getElementById('topStudentsTable');
        tableBody.innerHTML = '';
        
        students.forEach((student, index) => {
            const tr = document.createElement('tr');
            
            // Create performance progress bar
            const performancePercentage = (student.gpa / 4) * 100;
            const performanceColor = getPerformanceColor(student.gpa);
            
            tr.innerHTML = `
                <td>${index + 1}</td>
                <td><a href="/network/dashboard/student/${student.id}">${student.name}</a></td>
                <td>${student.year}</td>
                <td>${student.gpa.toFixed(2)}</td>
                <td>
                    <div class="progress" style="height: 10px;">
                        <div class="progress-bar ${performanceColor}" role="progressbar" 
                            style="width: ${performancePercentage}%;" 
                            aria-valuenow="${student.gpa}" aria-valuemin="0" aria-valuemax="4"></div>
                    </div>
                </td>
            `;
            tableBody.appendChild(tr);
        });
        
        if (students.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="5" class="text-center">No student data available</td>';
            tableBody.appendChild(tr);
        }
    }
    
    // Update assessment type chart
    function updateAssessmentTypeChart(assessmentData) {
        const ctx = document.getElementById('assessmentTypeChart').getContext('2d');
        
        // Destroy previous chart if it exists
        if (assessmentTypeChart) {
            assessmentTypeChart.destroy();
        }
        
        // Create new chart
        assessmentTypeChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: assessmentData.labels,
                datasets: [{
                    label: 'Average Score',
                    data: assessmentData.scores,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    yAxisID: 'y'
                }, {
                    label: 'Number of Assessments',
                    data: assessmentData.counts,
                    backgroundColor: 'rgba(153, 102, 255, 0.7)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Average Score'
                        },
                        max: 100
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Number of Assessments'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    }
    
    // Update time series chart
    function updateTimeSeriesChart(timeData) {
        const ctx = document.getElementById('timeSeriesChart').getContext('2d');
        
        // Destroy previous chart if it exists
        if (timeSeriesChart) {
            timeSeriesChart.destroy();
        }
        
        // Return if we don't have a valid canvas context or data
        if (!ctx || !timeData || !timeData.labels || !timeData.data) {
            console.error('Missing time series data or canvas context');
            return;
        }
        
        // Create new chart
        timeSeriesChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timeData.labels,
                datasets: [{
                    label: 'Average Score',
                    data: timeData.data,
                    fill: false,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    tension: 0.2,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
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
                            text: 'Average Score'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time Period'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Student Performance Over Time'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Average Score: ${context.raw.toFixed(1)}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Update year performance chart (freshmen, sophomore, junior, senior)
    function updateYearPerformanceChart() {
        const ctx = document.getElementById('yearPerformanceChart').getContext('2d');
        
        // Destroy previous chart if it exists
        if (yearPerformanceChart) {
            yearPerformanceChart.destroy();
        }
        
        // Return if we don't have a valid canvas context
        if (!ctx) {
            console.error('Missing canvas context for year performance chart');
            return;
        }
        
        // Query ArangoDB for year data via API, or use simulated data if not available
        // For now, using simulated data since we don't have this in the current API
        const years = ['Freshman', 'Sophomore', 'Junior', 'Senior'];
        const gpaData = [3.1, 3.3, 3.5, 3.7]; // Simulated average GPA by year
        
        // Create new chart
        yearPerformanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: years,
                datasets: [{
                    label: 'Average GPA',
                    data: gpaData,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 2.0,
                        max: 4.0,
                        title: {
                            display: true,
                            text: 'Average GPA'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Average GPA by Student Year'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Average GPA: ${context.raw.toFixed(2)}`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Export charts as PNG
    function exportChartsAsPNG() {
        // List of charts to export
        const chartIds = [
            { id: 'gpaDistributionChart', name: 'gpa_distribution' },
            { id: 'gradeDistributionChart', name: 'grade_distribution' },
            { id: 'assessmentTypeChart', name: 'assessment_type' },
            { id: 'yearPerformanceChart', name: 'year_performance' },
            { id: 'timeSeriesChart', name: 'performance_over_time' }
        ];
        
        // Export each chart
        chartIds.forEach(chartInfo => {
            const canvas = document.getElementById(chartInfo.id);
            if (!canvas) return;
            
            const a = document.createElement('a');
            a.href = canvas.toDataURL('image/png');
            a.download = `student_performance_${chartInfo.name}.png`;
            a.click();
        });
    }
    
    // Export performance data as CSV
    function exportPerformanceData() {
        fetch('/network/api/student-performance/')
            .then(response => response.json())
            .then(data => {
                // Create CSV for GPA distribution
                let csv = 'GPA Distribution\nRange,Count\n';
                data.gpa_distribution.labels.forEach((label, index) => {
                    csv += `${label},${data.gpa_distribution.data[index]}\n`;
                });
                
                // Add grade distribution
                csv += '\nGrade Distribution\nGrade,Count\n';
                data.grade_distribution.labels.forEach((label, index) => {
                    csv += `${label},${data.grade_distribution.data[index]}\n`;
                });
                
                // Add top students
                csv += '\nTop Students\nRank,Name,Year,GPA\n';
                data.top_students.forEach((student, index) => {
                    csv += `${index + 1},${student.name},${student.year},${student.gpa.toFixed(2)}\n`;
                });
                
                // Export CSV
                const dataStr = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
                const a = document.createElement('a');
                a.href = dataStr;
                a.download = 'student_performance_data.csv';
                a.click();
            })
            .catch(error => {
                console.error('Error exporting performance data:', error);
                alert('Failed to export performance data. Please try again later.');
            });
    }
    
    // Helper function to determine performance color based on GPA
    function getPerformanceColor(gpa) {
        if (gpa >= 3.5) {
            return 'bg-success';
        } else if (gpa >= 3.0) {
            return 'bg-info';
        } else if (gpa >= 2.5) {
            return 'bg-warning';
        } else {
            return 'bg-danger';
        }
    }
    
    // Helper function to show loading indicators
    function showLoading() {
        // Show loading indicator in the top students table
        const topStudentsTable = document.getElementById('topStudentsTable');
        if (topStudentsTable) {
            topStudentsTable.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </td>
                </tr>
            `;
        }
        
        // Disable refresh button while loading
        const refreshButton = document.getElementById('refreshData');
        if (refreshButton) {
            refreshButton.disabled = true;
            refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        }
    }
    
    // Helper function to hide loading indicators and show error
    function showError(message) {
        document.getElementById('topStudentsTable').innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-danger">${message}</td>
            </tr>
        `;
    }
    
    // Helper function to hide loading indicators
    function hideLoading() {
        // Re-enable refresh button
        const refreshButton = document.getElementById('refreshData');
        if (refreshButton) {
            refreshButton.disabled = false;
            refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Data';
        }
    }
});