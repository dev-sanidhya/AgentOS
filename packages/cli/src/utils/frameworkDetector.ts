import fs from 'fs';
import path from 'path';

export interface FrameworkDetectionResult {
  framework: 'langchain' | 'crewai' | 'raw' | 'unknown';
  language: 'python' | 'typescript' | 'unknown';
  confidence: number; // 0-1 score
  detectedFeatures: string[];
  recommendedTemplate: string;
}

export interface ProjectFiles {
  packageJson?: any;
  requirementsTxt?: string;
  pythonFiles: string[];
  typescriptFiles: string[];
}

export class FrameworkDetector {
  private projectPath: string;

  constructor(projectPath: string) {
    this.projectPath = projectPath;
  }

  async detectFramework(): Promise<FrameworkDetectionResult> {
    const files = await this.scanProjectFiles();
    const language = this.detectLanguage(files);
    const framework = this.detectFrameworkFromFiles(files, language);
    const confidence = this.calculateConfidence(files, framework, language);
    const detectedFeatures = this.getDetectedFeatures(files, framework);
    const recommendedTemplate = this.getRecommendedTemplate(framework, language);

    return {
      framework,
      language,
      confidence,
      detectedFeatures,
      recommendedTemplate
    };
  }

  private async scanProjectFiles(): Promise<ProjectFiles> {
    const files: ProjectFiles = {
      pythonFiles: [],
      typescriptFiles: []
    };

    // Check for package.json
    try {
      const packageJsonPath = path.join(this.projectPath, 'package.json');
      if (fs.existsSync(packageJsonPath)) {
        const packageJsonContent = fs.readFileSync(packageJsonPath, 'utf-8');
        files.packageJson = JSON.parse(packageJsonContent);
      }
    } catch (error) {
      // Ignore errors reading package.json
    }

    // Check for requirements.txt
    try {
      const requirementsPath = path.join(this.projectPath, 'requirements.txt');
      if (fs.existsSync(requirementsPath)) {
        files.requirementsTxt = fs.readFileSync(requirementsPath, 'utf-8');
      }
    } catch (error) {
      // Ignore errors reading requirements.txt
    }

    // Scan for Python and TypeScript files
    const scanDirectory = (dirPath: string, maxDepth: number = 2, currentDepth: number = 0) => {
      if (currentDepth >= maxDepth) return;

      try {
        const entries = fs.readdirSync(dirPath, { withFileTypes: true });

        for (const entry of entries) {
          if (entry.name.startsWith('.') || entry.name === 'node_modules') continue;

          const fullPath = path.join(dirPath, entry.name);

          if (entry.isDirectory()) {
            scanDirectory(fullPath, maxDepth, currentDepth + 1);
          } else if (entry.isFile()) {
            if (entry.name.endsWith('.py')) {
              files.pythonFiles.push(fullPath);
            } else if (entry.name.endsWith('.ts') || entry.name.endsWith('.tsx')) {
              files.typescriptFiles.push(fullPath);
            }
          }
        }
      } catch (error) {
        // Ignore errors reading directories
      }
    };

    scanDirectory(this.projectPath);
    return files;
  }

  private detectLanguage(files: ProjectFiles): 'python' | 'typescript' | 'unknown' {
    const hasPython = files.pythonFiles.length > 0 || files.requirementsTxt;
    const hasTypeScript = files.typescriptFiles.length > 0 || files.packageJson;

    if (hasPython && !hasTypeScript) return 'python';
    if (hasTypeScript && !hasPython) return 'typescript';
    if (hasPython && hasTypeScript) {
      // Both exist, prefer the one with more files
      return files.pythonFiles.length >= files.typescriptFiles.length ? 'python' : 'typescript';
    }

    return 'unknown';
  }

  private detectFrameworkFromFiles(
    files: ProjectFiles,
    language: 'python' | 'typescript' | 'unknown'
  ): 'langchain' | 'crewai' | 'raw' | 'unknown' {

    if (language === 'python') {
      return this.detectPythonFramework(files);
    } else if (language === 'typescript') {
      return this.detectTypeScriptFramework(files);
    }

    return 'unknown';
  }

  private detectPythonFramework(files: ProjectFiles): 'langchain' | 'crewai' | 'raw' | 'unknown' {
    // Check requirements.txt
    if (files.requirementsTxt) {
      const requirements = files.requirementsTxt.toLowerCase();
      if (requirements.includes('crewai')) return 'crewai';
      if (requirements.includes('langchain')) return 'langchain';
    }

    // Check Python file imports
    const imports = this.extractPythonImports(files.pythonFiles);
    if (imports.some(imp => imp.includes('crewai'))) return 'crewai';
    if (imports.some(imp => imp.includes('langchain'))) return 'langchain';

    // If Python files exist but no framework detected, it's raw Python
    if (files.pythonFiles.length > 0) return 'raw';

    return 'unknown';
  }

  private detectTypeScriptFramework(files: ProjectFiles): 'langchain' | 'raw' | 'unknown' {
    // Check package.json dependencies
    if (files.packageJson) {
      const allDeps = {
        ...files.packageJson.dependencies,
        ...files.packageJson.devDependencies
      };

      const depNames = Object.keys(allDeps);
      if (depNames.some(dep => dep.includes('langchain'))) return 'langchain';
    }

    // Check TypeScript file imports
    const imports = this.extractTypeScriptImports(files.typescriptFiles);
    if (imports.some(imp => imp.includes('langchain'))) return 'langchain';

    // If TypeScript files exist but no framework detected, it's raw
    if (files.typescriptFiles.length > 0) return 'raw';

    return 'unknown';
  }

  private extractPythonImports(pythonFiles: string[]): string[] {
    const imports: string[] = [];

    for (const filePath of pythonFiles.slice(0, 5)) { // Limit to first 5 files
      try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const lines = content.split('\n').slice(0, 20); // Check first 20 lines

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('import ') || trimmed.startsWith('from ')) {
            imports.push(trimmed);
          }
        }
      } catch (error) {
        // Ignore file reading errors
      }
    }

    return imports;
  }

  private extractTypeScriptImports(typescriptFiles: string[]): string[] {
    const imports: string[] = [];

    for (const filePath of typescriptFiles.slice(0, 5)) { // Limit to first 5 files
      try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const lines = content.split('\n').slice(0, 20); // Check first 20 lines

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('import ') || trimmed.startsWith('export ')) {
            imports.push(trimmed);
          }
        }
      } catch (error) {
        // Ignore file reading errors
      }
    }

    return imports;
  }

  private calculateConfidence(
    files: ProjectFiles,
    framework: 'langchain' | 'crewai' | 'raw' | 'unknown',
    language: 'python' | 'typescript' | 'unknown'
  ): number {
    let confidence = 0.1; // Base confidence

    // Language detection confidence
    if (language !== 'unknown') {
      confidence += 0.3;

      // More files = higher confidence
      const fileCount = language === 'python'
        ? files.pythonFiles.length
        : files.typescriptFiles.length;
      confidence += Math.min(fileCount * 0.1, 0.3);
    }

    // Framework detection confidence
    if (framework !== 'unknown') {
      confidence += 0.4;

      // Dependencies file adds confidence
      const hasDepsFile = language === 'python'
        ? !!files.requirementsTxt
        : !!files.packageJson;
      if (hasDepsFile) confidence += 0.2;
    }

    return Math.min(confidence, 1.0);
  }

  private getDetectedFeatures(
    files: ProjectFiles,
    framework: 'langchain' | 'crewai' | 'raw' | 'unknown'
  ): string[] {
    const features: string[] = [];

    if (files.packageJson) features.push('package.json');
    if (files.requirementsTxt) features.push('requirements.txt');
    if (files.pythonFiles.length > 0) features.push(`${files.pythonFiles.length} Python files`);
    if (files.typescriptFiles.length > 0) features.push(`${files.typescriptFiles.length} TypeScript files`);

    if (framework === 'langchain') features.push('LangChain framework');
    if (framework === 'crewai') features.push('CrewAI framework');
    if (framework === 'raw') features.push('No framework (raw implementation)');

    return features;
  }

  private getRecommendedTemplate(
    framework: 'langchain' | 'crewai' | 'raw' | 'unknown',
    language: 'python' | 'typescript' | 'unknown'
  ): string {
    if (framework === 'unknown' || language === 'unknown') {
      return 'langchain-python'; // Default fallback
    }

    if (framework === 'crewai') return 'crewai';
    if (framework === 'raw') {
      return language === 'typescript' ? 'raw-typescript' : 'raw-python';
    }

    // LangChain
    return language === 'typescript' ? 'langchain-typescript' : 'langchain-python';
  }
}

// Convenience function for quick detection
export async function detectProjectFramework(projectPath: string): Promise<FrameworkDetectionResult> {
  const detector = new FrameworkDetector(projectPath);
  return await detector.detectFramework();
}