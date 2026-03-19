export { fileAnalyzer, FileAnalyzerTool } from './fileAnalyzer.js';
export { securityScanner, SecurityScannerTool } from './securityScanner.js';
export type {
  FileAnalysisResult,
  SecurityScanResult,
  SecurityVulnerability
} from './fileAnalyzer.js';
export type {
  SecurityScanResult as SecurityScannerResult
} from './securityScanner.js';

// Re-export all tools as an array for easy registration
export const allTools = [fileAnalyzer, securityScanner];