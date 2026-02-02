/**
 * TypeScript type definitions for CodeGraph
 */

export interface NodeData {
  id: string;
  name: string;
  path: string;
  loc: number;
  complexity: number;
  language: string;
  imports: string[];
  size: number;
  // D3 adds these during simulation
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface EdgeData {
  source: string | NodeData;
  target: string | NodeData;
  weight: number;
}

export interface RepositoryMetrics {
  total_files: number;
  total_loc: number;
  avg_complexity: number;
  max_complexity: number;
  languages: Record<string, number>;
  most_connected: string[];
}

export interface AnalyzeResponse {
  nodes: NodeData[];
  edges: EdgeData[];
  metrics: RepositoryMetrics;
  repo_name: string;
  repo_url: string;
}

export interface AnalyzeRequest {
  repo_url: string;
  max_files?: number;
  include_tests?: boolean;
}

export interface GraphState {
  nodes: NodeData[];
  edges: EdgeData[];
  selectedNode: NodeData | null;
  highlightedNodes: Set<string>;
  searchTerm: string;
}
