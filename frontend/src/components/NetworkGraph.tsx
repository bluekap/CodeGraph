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
  selectedNodeId?: string;
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({
  theme = 'light',
  nodes,
  edges,
  onNodeClick,
  searchTerm = '',
  selectedNodeId
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

    // --- Premium Visuals: Definitions (Glows, Gradients) ---
    const defs = svg.append('defs');

    // 1. Neon Glow Filter
    const filter = defs.append('filter')
      .attr('id', 'glow')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    filter.append('feGaussianBlur')
      .attr('stdDeviation', '2.5')
      .attr('result', 'coloredBlur');

    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // 3. Arrow Marker
    defs.append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 22)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', graphTheme.arrowFill)
      .attr('opacity', 0.8);

    // --- Simulation Setup ---
    const g = svg.append('g');

    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 5])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);
    svg.call(zoom.transform, d3.zoomIdentity.translate(width / 2, height / 2).scale(0.8).translate(-width / 2, -height / 2));

    const simulation = d3.forceSimulation<NodeData>(nodes)
      .force('link', d3.forceLink<NodeData, EdgeData>(edges)
        .id(d => d.id)
        .distance(d => Math.min(120, 80 + (d.source as NodeData).imports?.length * 2))
        .strength(0.3)
      )
      .force('charge', d3.forceManyBody()
        .strength(d => -200 - (d as NodeData).size * 3)
        .distanceMax(400)
      )
      .force('center', d3.forceCenter(width / 2, height / 2).strength(0.3))
      .force('forceX', d3.forceX(width / 2).strength(0.1))
      .force('forceY', d3.forceY(height / 2).strength(0.1))
      .force('collision', d3.forceCollide().radius(d => (d as NodeData).size + 10).iterations(3))
      .velocityDecay(0.6)
      .alphaDecay(0.02);

    // Links
    const link = g.append('g')
      .attr('stroke', graphTheme.linkStroke)
      .attr('stroke-opacity', 0.4)
      .selectAll('line')
      .data(edges)
      .join('line')
      .attr('stroke-width', 1.2)
      .attr('class', 'link')
      .attr('marker-end', 'url(#arrow)')
      .style('transition', 'stroke-opacity 0.3s, stroke-width 0.3s');

    // Nodes
    const node = g.append('g')
      .selectAll<SVGCircleElement, NodeData>('circle')
      .data(nodes)
      .join('circle')
      .attr('r', d => Math.max(d.size, 8))
      .attr('fill', d => graphTheme.getComplexityColor(d.complexity))
      .attr('stroke', theme === 'dark' ? '#ffffff' : '#fff')
      .attr('stroke-width', 1.5)
      .attr('stroke-opacity', 0.8)
      .style('cursor', 'pointer')
      .style('filter', theme === 'dark' ? 'url(#glow)' : 'none')
      .style('transition', 'all 0.3s ease');

    // Labels
    const label = g.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .text(d => d.name)
      .attr('font-size', d => Math.min(14, Math.max(10, d.size / 2 + 4)))
      .attr('font-weight', 600)
      .attr('dx', d => d.size + 6)
      .attr('dy', 4)
      .attr('fill', graphTheme.labelColor)
      .style('pointer-events', 'none')
      .style('font-family', '"Inter", sans-serif')
      .style('opacity', 0.8)
      .style('text-shadow', theme === 'dark' ? '0 2px 4px rgba(0,0,0,0.9)' : '0 1px 2px rgba(255,255,255,0.8)');

    // Tooltip
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'graph-tooltip')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background', theme === 'dark' ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)')
      .style('color', theme === 'dark' ? '#e2e8f0' : '#1e293b')
      .style('padding', '12px 16px')
      .style('border-radius', '8px')
      .style('font-size', '13px')
      .style('border', `1px solid ${graphTheme.graphBorder}`)
      .style('backdrop-filter', 'blur(4px)')
      .style('box-shadow', '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)')
      .style('pointer-events', 'none')
      .style('z-index', '1000')
      .style('transform', 'translateY(-100%) translateY(-12px)');

    const highlightConnections = (d: NodeData | null) => {
      const activeId = d?.id || selectedNodeId;
      if (!activeId) {
        node.style('opacity', 1).style('filter', theme === 'dark' ? 'url(#glow)' : 'none').attr('stroke-width', 1.5);
        link.style('stroke-opacity', 0.4).attr('stroke-width', 1.2).attr('stroke', graphTheme.linkStroke);
        label.style('opacity', 0.8).attr('font-weight', 600);
        return;
      }

      const connectedNodeIds = new Set<string>();
      connectedNodeIds.add(activeId);
      const connectedLinks = new Set<EdgeData>();

      edges.forEach(edge => {
        const sourceId = typeof edge.source === 'string' ? edge.source : (edge.source as NodeData).id;
        const targetId = typeof edge.target === 'string' ? edge.target : (edge.target as NodeData).id;
        if (sourceId === activeId || targetId === activeId) {
          connectedNodeIds.add(sourceId === activeId ? targetId : sourceId);
          connectedLinks.add(edge);
        }
      });

      node
        .style('opacity', n => connectedNodeIds.has(n.id) ? 1 : 0.1)
        .style('filter', n => n.id === activeId && theme === 'dark' ? 'url(#glow)' : 'none')
        .attr('stroke-width', n => n.id === activeId ? 3 : 1.5);

      link
        .style('stroke-opacity', l => connectedLinks.has(l) ? 0.8 : 0.05)
        .attr('stroke-width', l => connectedLinks.has(l) ? 2 : 1)
        .attr('stroke', l => connectedLinks.has(l) ? graphTheme.highlightStroke : graphTheme.linkStroke);

      label
        .style('opacity', n => connectedNodeIds.has(n.id) ? 1 : 0.1)
        .attr('font-weight', n => n.id === activeId ? 800 : 600);
    };

    node.on('mouseover', function (event, d) {
      d3.select(this).attr('stroke', graphTheme.highlightStroke).attr('stroke-width', 3).transition().duration(200).attr('r', d.size + 4);
      highlightConnections(d);
      tooltip.style('visibility', 'visible').html(`
        <div style="font-weight: 600; margin-bottom: 4px; font-size: 14px;">${d.name}</div>
        <div style="opacity: 0.8; font-size: 11px; margin-bottom: 8px;">${d.path}</div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px;">
          <div>Lines: <strong>${d.loc}</strong></div>
          <div>Complexity: <strong style="color: ${graphTheme.getComplexityColor(d.complexity)}">${d.complexity.toFixed(1)}</strong></div>
        </div>
      `);
    })
      .on('mousemove', function (event) {
        tooltip.style('top', (event.pageY) + 'px').style('left', (event.pageX) + 'px');
      })
      .on('mouseout', function (event, d) {
        d3.select(this).attr('stroke', theme === 'dark' ? '#ffffff' : '#fff').attr('stroke-width', 1.5).transition().duration(300).attr('r', d.size);
        highlightConnections(null);
        tooltip.style('visibility', 'hidden');
      })
      .on('click', function (this: SVGCircleElement, event, d) {
        event.stopPropagation();
        if (onNodeClick) {
          onNodeClick(selectedNodeId === d.id ? null as any : d);
        }
      });

    svg.on('click', () => {
      if (onNodeClick) onNodeClick(null as any);
    });

    highlightConnections(null);

    if (searchTerm) {
      const match = nodes.find(n => n.name.toLowerCase().includes(searchTerm.toLowerCase()));
      if (match) highlightConnections(match);
    }

    simulation.on('tick', () => {
      link.attr('x1', d => (d.source as NodeData).x!)
        .attr('y1', d => (d.source as NodeData).y!)
        .attr('x2', d => (d.target as NodeData).x!)
        .attr('y2', d => (d.target as NodeData).y!);
      node.attr('cx', d => d.x!).attr('cy', d => d.y!);
      label.attr('x', d => d.x!).attr('y', d => d.y!);
    });

    function drag(simulation: d3.Simulation<NodeData, undefined>) {
      function dragstarted(this: SVGCircleElement, event: any, d: NodeData) {
        if (!event.active) simulation.alphaTarget(0.1).restart();
        d.fx = d.x; d.fy = d.y;
        d3.select(this).style('cursor', 'grabbing');
      }
      function dragged(event: any, d: NodeData) { d.fx = event.x; d.fy = event.y; }
      function dragended(this: SVGCircleElement, event: any, d: NodeData) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null; d.fy = null;
        d3.select(this).style('cursor', 'pointer');
      }
      return d3.drag<SVGCircleElement, NodeData>().on('start', dragstarted).on('drag', dragged).on('end', dragended);
    }
    node.call(drag(simulation));

    return () => {
      simulation.stop();
      tooltip.remove();
    };
  }, [nodes, edges, dimensions, searchTerm, theme, onNodeClick, graphTheme, selectedNodeId]);

  return (
    <div ref={containerRef} className="network-graph-container" style={{ width: '100%', height: '100%' }}>
      <svg
        ref={svgRef}
        width={dimensions.width}
        height={dimensions.height}
        style={{
          display: 'block',
          borderRadius: '12px',
          background: theme === 'dark'
            ? 'radial-gradient(circle at center, #1e293b 0%, #0f172a 100%)'
            : 'radial-gradient(circle at center, #ffffff 0%, #eff6ff 100%)',
          boxShadow: theme === 'dark' ? 'inset 0 0 40px rgba(0,0,0,0.5)' : 'inset 0 0 20px rgba(0,0,0,0.05)',
          overflow: 'hidden'
        }}
      />
    </div>
  );
};
