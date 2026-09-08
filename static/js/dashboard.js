/**
 * dashboard.js
 * Renders charts for the Todo dashboard.
 * Reads data from the JSON script tag with id "dashboard-data".
 * Uses Chart.js for rendering.
 */
'use strict';

document.addEventListener('DOMContentLoaded', function() {
    // 1. Retrieve the JSON data from the script tag
    const dataScript = document.getElementById('dashboard-data');
    if (!dataScript) {
        console.warn('dashboard-data script element not found.');
        return;
    }

    let dashboardData;
    try {
        dashboardData = JSON.parse(dataScript.textContent);
    } catch (e) {
        console.error('Failed to parse dashboard data:', e);
        return;
    }

    // 2. Helper function to safely get arrays
    const safeArray = (arr) => Array.isArray(arr) ? arr : [];

    // 3. Priority Chart (Bar)
    const priorityCtx = document.getElementById('priorityChart');
    if (priorityCtx) {
        const priority = dashboardData.priority || {};
        const labels = safeArray(priority.labels);
        const counts = safeArray(priority.counts);
        const colors = safeArray(priority.colors);
        const borderColors = safeArray(priority.borderColors);

        new Chart(priorityCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Tasks',
                    data: counts,
                    backgroundColor: colors.length ? colors : 'rgba(0,123,255,0.6)',
                    borderColor: borderColors.length ? borderColors : 'rgba(0,123,255,1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        stepSize: 1,
                        ticks: { precision: 0 }
                    }
                }
            }
        });
    } else {
        console.warn('Priority chart canvas not found.');
    }

    // 4. Category Chart (Bar)
    const categoryCtx = document.getElementById('categoryChart');
    if (categoryCtx) {
        const category = dashboardData.category || {};
        const labels = safeArray(category.labels);
        const counts = safeArray(category.counts);
        const colors = safeArray(category.colors);

        new Chart(categoryCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Tasks per Category',
                    data: counts,
                    backgroundColor: colors.length ? colors : 'rgba(0,123,255,0.6)',
                    borderColor: colors.length ? colors : 'rgba(0,123,255,1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        stepSize: 1,
                        ticks: { precision: 0 }
                    }
                }
            }
        });
    } else {
        console.warn('Category chart canvas not found.');
    }
});