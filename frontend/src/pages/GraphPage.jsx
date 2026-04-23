import React, { useEffect, useRef } from 'react';
import { Box, Typography, CircularProgress } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import * as d3 from 'd3';
import { api } from '../api/client';

export default function GraphPage() {
  const svgRef = useRef(null);
  const containerRef = useRef(null);

  const { data: graphData, isLoading, isError } = useQuery({
    queryKey: ['graph'],
    queryFn: () => api.getGraph(),
  });

  useEffect(() => {
    if (!graphData || !svgRef.current || !containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = 600;

    // Clear previous SVG contents
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3.select(svgRef.current)
      .attr("width", width)
      .attr("height", height)
      .call(d3.zoom().on("zoom", (event) => {
        g.attr("transform", event.transform);
      }));

    const g = svg.append("g");

    // Initialize simulation
    const simulation = d3.forceSimulation(graphData.nodes)
      .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    // Draw links
    const link = g.append("g")
      .selectAll("line")
      .data(graphData.links)
      .join("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", d => Math.sqrt(d.weight));

    // Draw nodes
    const node = g.append("g")
      .selectAll("circle")
      .data(graphData.nodes)
      .join("circle")
      .attr("r", d => 10 + Math.sqrt(d.face_count || 1) * 2)
      .attr("fill", "#8ab4f8")
      .call(drag(simulation));

    // Draw labels
    const label = g.append("g")
      .selectAll("text")
      .data(graphData.nodes)
      .join("text")
      .text(d => d.label)
      .attr("font-size", 12)
      .attr("dx", 15)
      .attr("dy", 4)
      .attr("fill", "currentColor"); // Adapt to theme

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      label
        .attr("x", d => d.x)
        .attr("y", d => d.y);
    });

    // Drag behavior
    function drag(simulation) {
      function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }
      
      function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }
      
      function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }
      
      return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }

    return () => {
      simulation.stop();
    };
  }, [graphData]);

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', p: 2 }}>
      <Typography variant="h5" fontWeight="500" sx={{ mb: 3 }}>Social Graph</Typography>
      
      {isLoading && <CircularProgress />}
      {isError && <Typography color="error">Failed to load graph data.</Typography>}
      
      <Box ref={containerRef} sx={{ width: '100%', border: '1px solid', borderColor: 'divider', borderRadius: 2, overflow: 'hidden', bgcolor: 'background.paper' }}>
        <svg ref={svgRef}></svg>
      </Box>
    </Box>
  );
}
