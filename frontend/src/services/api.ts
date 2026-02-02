/**
 * API service for communicating with CodeGraph backend
 */
import axios from 'axios';
import { AnalyzeRequest, AnalyzeResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for cloning repos
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function analyzeRepository(repoUrl: string): Promise<AnalyzeResponse> {
  try {
    const request: AnalyzeRequest = {
      repo_url: repoUrl,
      max_files: 100,
      include_tests: false,
    };

    const response = await api.post<AnalyzeResponse>('/api/analyze', request);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      // Server responded with error
      throw new Error(error.response.data.detail || 'Analysis failed');
    } else if (error.request) {
      // No response received
      throw new Error('No response from server. Please check if backend is running.');
    } else {
      // Other errors
      throw new Error('Failed to send request: ' + error.message);
    }
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    await api.get('/health');
    return true;
  } catch {
    return false;
  }
}
