/**
 * Interactive D3.js Network Graph Component
 */
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { NodeData, EdgeData } from '../types';
import { type ThemeId, graphThemes } from '../theme';

interface NetworkGraphProps {
  theme?: ThemeId;
  nodes: NodeData[];
  edges: EdgeData[];
  onNodeClick?: (node: NodeData) => void;
  searchTerm?: string;
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({
  theme = 'light',
  nodes,
  edges,
  onNodeClick,
  searchTerm = ''
}) => {
  const graphTheme = graphThemes[theme];
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 1200, height: 700 });

  // Use full container space and keep dimensions in sync on resize
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const updateSize = () => {
      const w = container.clientWidth;
      const h = container.clientHeight;
      if (w > 0 && h > 0) setDimensions({ width: w, height: h });
    };

    updateSize();
    const ro = new ResizeObserver(updateSize);
    ro.observe(container);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    // Clear previous graph
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current);
    const width = dimensions.width;
    const height = dimensions.height;

    // Create container group for zoom
    const g = svg.append('g');

    // Setup zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Keep nodes inside the visible area (with padding for labels)
    const padding = 80;
    const xMin = padding;
    const xMax = width - padding;
    const yMin = padding;
    const yMax = height - padding;

    function forceBound() {
      for (const node of nodes) {
        if (node.x != null) node.x = Math.max(xMin, Math.min(xMax, node.x));
        if (node.y != null) node.y = Math.max(yMin, Math.min(yMax, node.y));
      }
    }
    forceBound.initialize = () => {};

    // Scale layout by repo size so large graphs fit in the window
    const n = nodes.length;
    const linkDistance = Math.max(80, Math.min(220, 280 - n * 0.5));
    const chargeStrength = Math.max(-1200, -400 - n * 2);

    // Force simulation: spread-out but bounded to the graph window
    const simulation = d3.forceSimulation<NodeData>(nodes)
      .force('link', d3.forceLink<NodeData, EdgeData>(edges)
        .id(d => d.id)
        .distance(linkDistance)
        .strength(0.3)
      )
      .force('charge', d3.forceManyBody().strength(chargeStrength))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(d => Math.max((d as NodeData).size + 10, 16)))
      .force('bound', forceBound)
      .force('x', d3.forceX(width / 2).strength(0.02))
      .force('y', d3.forceY(height / 2).strength(0.02))
      .alphaDecay(0.05)
      .velocityDecay(0.4);

    // Create arrow markers for directed edges
    svg.append('defs').selectAll('marker')
      .data(['arrow'])
      .join('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', graphTheme.arrowFill)
      .attr('opacity', 0.7);

    // Create links (edges)
    const link = g.append('g')
      .selectAll('line')
      .data(edges)
      .join('line')
      .attr('stroke', graphTheme.linkStroke)
      .attr('stroke-opacity', 0.5)
      .attr('stroke-width', 1.5)
      .attr('marker-end', 'url(#arrow)');

    // Create nodes: ensure minimum radius for visibility and dragging
    const node = g.append('g')
      .selectAll<SVGCircleElement, NodeData>('circle')
      .data(nodes)
      .join('circle')
      .attr('r', d => Math.max(d.size, 10))
      .attr('fill', d => graphTheme.getComplexityColor(d.complexity))
      .attr('stroke', graphTheme.nodeStroke)
      .attr('stroke-width', 2.5)
      .style('cursor', 'grab')
      .style('transition', 'stroke-width 0.15s ease');
    node.call(drag(simulation));

    // Add labels (theme-aware color for readability)
    const label = g.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .text(d => d.name)
      .attr('font-size', 11)
      .attr('font-weight', 500)
      .attr('dx', 14)
      .attr('dy', 4)
      .attr('fill', graphTheme.labelColor)
      .style('pointer-events', 'none')
      .style('user-select', 'none')
      .style('text-shadow', theme === 'dark' ? '0 0 2px rgba(0,0,0,0.8)' : '0 0 1px rgba(255,255,255,0.9)');

    // Tooltip
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'graph-tooltip')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background-color', graphTheme.tooltipBg)
      .style('color', graphTheme.tooltipText)
      .style('padding', '12px 14px')
      .style('border-radius', '8px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('z-index', '1000')
      .style('box-shadow', '0 4px 12px rgba(0,0,0,0.15)');

    // Node interactions: hover and tooltip
    node
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('stroke', graphTheme.highlightStroke)
          .attr('stroke-width', 4)
          .style('cursor', 'grab');

        tooltip
          .style('visibility', 'visible')
          .html(`
            <strong>${d.name}</strong><br/>
            Path: ${d.path}<br/>
            Lines: ${d.loc} · Complexity: ${d.complexity}<br/>
            Language: ${d.language} · Imports: ${d.imports.length}
          `);
      })
      .on('mousemove', function(event) {
        tooltip
          .style('top', (event.pageY - 8) + 'px')
          .style('left', (event.pageX + 12) + 'px');
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('stroke', graphTheme.nodeStroke)
          .attr('stroke-width', 2.5);
        tooltip.style('visibility', 'hidden');
      })
      .on('click', function(event, d) {
        event.stopPropagation();
        
        // Highlight connected nodes
        const connectedNodeIds = new Set<string>();
        connectedNodeIds.add(d.id);
        
        edges.forEach(edge => {
          const source = typeof edge.source === 'string' ? edge.source : edge.source.id;
          const target = typeof edge.target === 'string' ? edge.target : edge.target.id;
          
          if (source === d.id) connectedNodeIds.add(target);
          if (target === d.id) connectedNodeIds.add(source);
        });

        // Update node styles
        node
          .attr('opacity', n => connectedNodeIds.has(n.id) ? 1 : 0.15)
          .attr('stroke', n => n.id === d.id ? graphTheme.highlightStroke : graphTheme.nodeStroke)
          .attr('stroke-width', n => n.id === d.id ? 4 : 2.5);

        // Update link styles: highlight connected edges
        link.attr('opacity', e => {
          const source = typeof e.source === 'string' ? e.source : e.source.id;
          const target = typeof e.target === 'string' ? e.target : e.target.id;
          return (source === d.id || target === d.id) ? 0.9 : 0.08;
        });

        // Call parent handler
        if (onNodeClick) onNodeClick(d);
      });

    // Click on background to reset highlight
    svg.on('click', () => {
      node
        .attr('opacity', 1)
        .attr('stroke', graphTheme.nodeStroke)
        .attr('stroke-width', 2.5);
      link.attr('opacity', 0.5);
    });

    // Search highlighting
    if (searchTerm) {
      const matchingNodes = nodes.filter(n => 
        n.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        n.path.toLowerCase().includes(searchTerm.toLowerCase())
      );
      const matchingIds = new Set(matchingNodes.map(n => n.id));

      node
        .attr('opacity', n => matchingIds.has(n.id) ? 1 : 0.15)
        .attr('stroke', n => matchingIds.has(n.id) ? graphTheme.highlightStroke : graphTheme.nodeStroke)
        .attr('stroke-width', n => matchingIds.has(n.id) ? 4 : 2.5);
    }

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => (d.source as NodeData).x!)
        .attr('y1', d => (d.source as NodeData).y!)
        .attr('x2', d => (d.target as NodeData).x!)
        .attr('y2', d => (d.target as NodeData).y!);

      node
        .attr('cx', d => d.x!)
        .attr('cy', d => d.y!);

      label
        .attr('x', d => d.x!)
        .attr('y', d => d.y!);
    });

    // Pre-run simulation so the graph appears in a more resolved, spread-out state
    for (let i = 0; i < 150; i++) simulation.tick();

    // Drag behavior: keep node fixed under cursor, minimal simulation during/after drag for stability
    function drag(simulation: d3.Simulation<NodeData, undefined>) {
      function dragstarted(this: SVGCircleElement, event: d3.D3DragEvent<SVGCircleElement, NodeData, NodeData>, d: NodeData) {
        if (!event.active) simulation.alphaTarget(0.08).restart();
        d.fx = d.x ?? event.x;
        d.fy = d.y ?? event.y;
        d3.select(this).style('cursor', 'grabbing');
      }

      function dragged(event: d3.D3DragEvent<SVGCircleElement, NodeData, NodeData>, d: NodeData) {
        d.fx = event.x;
        d.fy = event.y;
      }

      function dragended(this: SVGCircleElement, event: d3.D3DragEvent<SVGCircleElement, NodeData, NodeData>, d: NodeData) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
        d3.select(this).style('cursor', 'grab');
      }

      return d3.drag<SVGCircleElement, NodeData>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
    }

    // Cleanup
    return () => {
      simulation.stop();
      tooltip.remove();
    };
  }, [nodes, edges, dimensions, searchTerm, onNodeClick, theme]);

  return (
    <div ref={containerRef} className="network-graph-container">
      <svg
        ref={svgRef}
        width={dimensions.width}
        height={dimensions.height}
        style={{
          display: 'block',
          border: `1px solid ${graphThemes[theme].graphBorder}`,
          borderRadius: '8px',
          background: graphThemes[theme].graphBg,
        }}
      />
    </div>
  );
};
