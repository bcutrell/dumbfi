import * as d3 from 'd3';

// Sample visualization
const svg = d3.select('#app')
    .append('svg')
    .attr('width', 400)
    .attr('height', 300);

svg.append('circle')
    .attr('cx', 200)
    .attr('cy', 150)
    .attr('r', 50)
    .style('fill', 'steelblue');
