import { Tool } from '@langchain/core/tools';
import { z } from 'zod';

export interface SecurityScanResult {
  vulnerabilities: SecurityVulnerability[];
  riskScore: number;
  summary: string;
  recommendations: string[];
  compliance: {
    owasp: string[];
    cwe: string[];
  };
}

export interface SecurityVulnerability {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  line: number;
  column?: number;
  description: string;
  cwe?: string;
  owaspCategory?: string;
  recommendation: string;
  references?: string[];
}

export class SecurityScannerTool extends Tool {
  name = 'security_scanner';
  description = 'Scans code for security vulnerabilities and compliance issues';

  schema = z.object({
    code: z.string().describe('The source code to scan for security issues'),
    language: z.string().describe('The programming language of the code'),
    framework: z.string().optional().describe('The framework being used (optional)'),
  });

  async _call(input: z.infer<typeof this.schema>): Promise<string> {
    try {
      const scanResult = await this.scanSecurity(input.code, input.language, input.framework);
      return JSON.stringify(scanResult, null, 2);
    } catch (error) {
      return `Security scan failed: ${error instanceof Error ? error.message : String(error)}`;
    }
  }

  private async scanSecurity(
    code: string,
    language: string,
    framework?: string
  ): Promise<SecurityScanResult> {
    const vulnerabilities: SecurityVulnerability[] = [];
    const lines = code.split('\n');

    // Run all security checks
    vulnerabilities.push(...this.checkInjectionVulnerabilities(lines, language));
    vulnerabilities.push(...this.checkXSS(lines, language, framework));
    vulnerabilities.push(...this.checkAuthenticationIssues(lines, language));
    vulnerabilities.push(...this.checkCryptographyIssues(lines, language));
    vulnerabilities.push(...this.checkInputValidation(lines, language));
    vulnerabilities.push(...this.checkSecretExposure(lines, language));
    vulnerabilities.push(...this.checkAccessControl(lines, language));
    vulnerabilities.push(...this.checkErrorHandling(lines, language));

    const riskScore = this.calculateRiskScore(vulnerabilities);
    const summary = this.generateSummary(vulnerabilities, riskScore);
    const recommendations = this.generateRecommendations(vulnerabilities, language);
    const compliance = this.mapToCompliance(vulnerabilities);

    return {
      vulnerabilities,
      riskScore,
      summary,
      recommendations,
      compliance,
    };
  }

  private checkInjectionVulnerabilities(lines: string[], language: string): SecurityVulnerability[] {
    const vulnerabilities: SecurityVulnerability[] = [];

    lines.forEach((line, index) => {
      const lineNum = index + 1;
      const trimmed = line.trim();

      // SQL Injection patterns
      const sqlPatterns = [
        /\$\{.*\}.*SELECT/i,
        /\+.*SELECT.*FROM/i,
        /concat\(.*SELECT/i,
        /query.*\+.*\$\{/i,
        /execute\(.*\+.*\)/i,
      ];

      sqlPatterns.forEach(pattern => {
        if (pattern.test(trimmed)) {
          vulnerabilities.push({
            id: `sql-injection-${lineNum}`,
            type: 'SQL Injection',
            severity: 'critical',
            line: lineNum,
            description: 'Potential SQL injection vulnerability detected',
            cwe: 'CWE-89',
            owaspCategory: 'A03:2021 – Injection',
            recommendation: 'Use parameterized queries or prepared statements',
            references: ['https://owasp.org/Top10/A03_2021-Injection/'],
          });
        }
      });

      // Command Injection patterns
      const commandPatterns = [
        /exec\(.*\$\{.*\}\)/i,
        /system\(.*\+.*\)/i,
        /Runtime\.getRuntime\(\)\.exec/i,
        /subprocess.*shell=True/i,
        /os\.system\(/i,
      ];

      commandPatterns.forEach(pattern => {
        if (pattern.test(trimmed)) {
          vulnerabilities.push({
            id: `command-injection-${lineNum}`,
            type: 'Command Injection',
            severity: 'critical',
            line: lineNum,
            description: 'Potential command injection vulnerability detected',
            cwe: 'CWE-78',
            owaspCategory: 'A03:2021 – Injection',
            recommendation: 'Avoid executing system commands with user input. Use safe alternatives.',
            references: ['https://owasp.org/Top10/A03_2021-Injection/'],
          });
        }
      });
    });

    return vulnerabilities;
  }

  private checkXSS(lines: string[], language: string, framework?: string): SecurityVulnerability[] {
    const vulnerabilities: SecurityVulnerability[] = [];

    lines.forEach((line, index) => {
      const lineNum = index + 1;
      const trimmed = line.trim();

      // XSS patterns
      const xssPatterns = [
        /innerHTML.*\+.*\$\{/i,
        /document\.write\(/i,
        /\.html\(.*\+.*\)/i,
        /dangerouslySetInnerHTML/i,
        /v-html.*\$\{/i, // Vue.js
      ];

      xssPatterns.forEach(pattern => {
        if (pattern.test(trimmed)) {
          vulnerabilities.push({
            id: `xss-${lineNum}`,
            type: 'Cross-Site Scripting (XSS)',
            severity: 'high',
            line: lineNum,
            description: 'Potential XSS vulnerability detected',
            cwe: 'CWE-79',
            owaspCategory: 'A03:2021 – Injection',
            recommendation: 'Sanitize user input and use safe DOM manipulation methods',
            references: ['https://owasp.org/www-community/attacks/xss/'],
          });
        }
      });
    });

    return vulnerabilities;
  }

  private checkAuthenticationIssues(lines: string[], language: string): SecurityVulnerability[] {
    const vulnerabilities: SecurityVulnerability[] = [];

    lines.forEach((line, index) => {
      const lineNum = index + 1;
      const trimmed = line.trim();

      // Weak authentication patterns
      const authPatterns = [
        /password.*===.*['"]\w{1,7}['"]/i, // Short passwords
        /session.*httpOnly.*false/i,
        /secure.*false/i,
        /sameSite.*none/i,
        /jwt\.sign\(.*{.*algorithm.*none/i,
      ];

      authPatterns.forEach(pattern => {
        if (pattern.test(trimmed)) {
          vulnerabilities.push({
            id: `auth-issue-${lineNum}`,
            type: 'Weak Authentication',
            severity: 'medium',
            line: lineNum,
            description: 'Weak authentication configuration detected',
            cwe: 'CWE-287',
            owaspCategory: 'A07:2021 – Identification and Authentication Failures',
            recommendation: 'Implement strong authentication mechanisms',
            references: ['https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/'],
          });
        }
      });
    });

    return vulnerabilities;
  }

  private checkCryptographyIssues(lines: string[], language: string): SecurityVulnerability[] {
    const vulnerabilities: SecurityVulnerability[] = [];

    lines.forEach((line, index) => {
      const lineNum = index + 1;
      const trimmed = line.trim();

      // Weak cryptography patterns
      const cryptoPatterns = [
        /MD5|SHA1/i,
        /DES|3DES/i,
        /RC4/i,
        /Math\.random\(\)/i, // Weak random number generation
        /Random\(\)/i,
        /crypto\.createHash\(['"]md5['"]]/i,
      ];

      cryptoPatterns.forEach(pattern => {
        if (pattern.test(trimmed)) {
          let severity: 'low' | 'medium' | 'high' | 'critical' = 'medium';
          if (/MD5|SHA1|DES|RC4/i.test(trimmed)) {
            severity = 'high';
          }

          vulnerabilities.push({
            id: `crypto-weak-${lineNum}`,
            type: 'Weak Cryptography',
            severity,
            line: lineNum,
            description: 'Weak cryptographic algorithm or random number generation detected',
            cwe: 'CWE-326',
            owaspCategory: 'A02:2021 – Cryptographic Failures',
            recommendation: 'Use strong cryptographic algorithms (AES-256, SHA-256+)',
            references: ['https://owasp.org/Top10/A02_2021-Cryptographic_Failures/'],
          });
        }
      });
    });

    return vulnerabilities;
  }

  private checkInputValidation(lines: string[], language: string): SecurityVulnerability[] {
    const vulnerabilities: SecurityVulnerability[] = [];

    lines.forEach((line, index) => {
      const lineNum = index + 1;
      const trimmed = line.trim();

      // Input validation issues
      const validationPatterns = [
        /req\.body\.\w+.*without.*validation/i,
        /parseInt\(.*\).*without.*validation/i,
        /JSON\.parse\(.*\).*without.*try/i,
        /eval\(/i,
        /Function\(/i,
      ];

      validationPatterns.forEach(pattern => {
        if (pattern.test(trimmed)) {
          let severity: 'low' | 'medium' | 'high' | 'critical' = 'medium';
          if (/eval|Function\(/i.test(trimmed)) {
            severity = 'critical';
          }

          vulnerabilities.push({
            id: `input-validation-${lineNum}`,
            type: 'Insufficient Input Validation',
            severity,
            line: lineNum,
            description: 'Input validation issue detected',
            cwe: 'CWE-20',
            owaspCategory: 'A03:2021 – Injection',
            recommendation: 'Implement proper input validation and sanitization',
          });
        }
      });
    });

    return vulnerabilities;
  }

  private checkSecretExposure(lines: string[], language: string): SecurityVulnerability[] {
    const vulnerabilities: SecurityVulnerability[] = [];

    lines.forEach((line, index) => {
      const lineNum = index + 1;
      const trimmed = line.trim();

      // Secret exposure patterns
      const secretPatterns = [
        /(?:password|pwd|secret|key|token).*=.*['"]\w+['"]$/i,
        /(?:api_key|apikey).*=.*['"]\w+['"]$/i,
        /(?:private_key|privatekey).*=.*['"]/i,
        /console\.log\(.*(?:password|secret|key|token)/i,
        /print\(.*(?:password|secret|key|token)/i,
      ];

      secretPatterns.forEach(pattern => {
        if (pattern.test(trimmed)) {
          vulnerabilities.push({
            id: `secret-exposure-${lineNum}`,
            type: 'Secret Exposure',
            severity: 'high',
            line: lineNum,
            description: 'Potential secret or sensitive information exposure',
            cwe: 'CWE-200',
            owaspCategory: 'A01:2021 – Broken Access Control',
            recommendation: 'Move secrets to environment variables or secure configuration',
            references: ['https://owasp.org/Top10/A01_2021-Broken_Access_Control/'],
          });
        }
      });
    });

    return vulnerabilities;
  }

  private checkAccessControl(lines: string[], language: string): SecurityVulnerability[] {
    const vulnerabilities: SecurityVulnerability[] = [];

    lines.forEach((line, index) => {
      const lineNum = index + 1;
      const trimmed = line.trim();

      // Access control issues
      const accessPatterns = [
        /app\.get\(.*function.*{[^}]*}.*\)/i, // Routes without auth middleware
        /router\.\w+\(.*function.*{[^}]*}.*\)/i,
        /chmod.*777/i,
        /umask.*000/i,
      ];

      accessPatterns.forEach(pattern => {
        if (pattern.test(trimmed)) {
          vulnerabilities.push({
            id: `access-control-${lineNum}`,
            type: 'Broken Access Control',
            severity: 'medium',
            line: lineNum,
            description: 'Potential access control issue detected',
            cwe: 'CWE-285',
            owaspCategory: 'A01:2021 – Broken Access Control',
            recommendation: 'Implement proper authentication and authorization checks',
            references: ['https://owasp.org/Top10/A01_2021-Broken_Access_Control/'],
          });
        }
      });
    });

    return vulnerabilities;
  }

  private checkErrorHandling(lines: string[], language: string): SecurityVulnerability[] {
    const vulnerabilities: SecurityVulnerability[] = [];

    lines.forEach((line, index) => {
      const lineNum = index + 1;
      const trimmed = line.trim();

      // Error handling issues
      const errorPatterns = [
        /catch.*{.*console\.log\(.*error.*\)/i,
        /except.*:.*print\(/i,
        /res\.send\(.*error/i,
        /throw.*Error\(.*\+/i,
      ];

      errorPatterns.forEach(pattern => {
        if (pattern.test(trimmed)) {
          vulnerabilities.push({
            id: `error-handling-${lineNum}`,
            type: 'Information Disclosure',
            severity: 'low',
            line: lineNum,
            description: 'Potential information disclosure through error messages',
            cwe: 'CWE-209',
            owaspCategory: 'A09:2021 – Security Logging and Monitoring Failures',
            recommendation: 'Implement secure error handling that does not expose sensitive information',
          });
        }
      });
    });

    return vulnerabilities;
  }

  private calculateRiskScore(vulnerabilities: SecurityVulnerability[]): number {
    let score = 0;

    vulnerabilities.forEach(vuln => {
      switch (vuln.severity) {
        case 'critical':
          score += 10;
          break;
        case 'high':
          score += 7;
          break;
        case 'medium':
          score += 4;
          break;
        case 'low':
          score += 1;
          break;
      }
    });

    return Math.min(100, score);
  }

  private generateSummary(vulnerabilities: SecurityVulnerability[], riskScore: number): string {
    const critical = vulnerabilities.filter(v => v.severity === 'critical').length;
    const high = vulnerabilities.filter(v => v.severity === 'high').length;
    const medium = vulnerabilities.filter(v => v.severity === 'medium').length;
    const low = vulnerabilities.filter(v => v.severity === 'low').length;

    let riskLevel = 'Low';
    if (riskScore >= 30) riskLevel = 'High';
    else if (riskScore >= 15) riskLevel = 'Medium';

    return `Security scan completed. Risk Level: ${riskLevel} (Score: ${riskScore}/100). ` +
           `Found ${vulnerabilities.length} issues: ${critical} critical, ${high} high, ${medium} medium, ${low} low severity.`;
  }

  private generateRecommendations(vulnerabilities: SecurityVulnerability[], language: string): string[] {
    const recommendations = new Set<string>();

    // Add specific recommendations based on vulnerabilities found
    vulnerabilities.forEach(vuln => {
      recommendations.add(vuln.recommendation);
    });

    // Add general recommendations based on language
    switch (language.toLowerCase()) {
      case 'javascript':
      case 'typescript':
        recommendations.add('Use ESLint with security rules enabled');
        recommendations.add('Implement Content Security Policy (CSP) headers');
        recommendations.add('Use helmet.js for Express.js applications');
        break;
      case 'python':
        recommendations.add('Use bandit for automated security testing');
        recommendations.add('Implement proper exception handling');
        break;
      case 'java':
        recommendations.add('Use SpotBugs or SonarQube for static analysis');
        recommendations.add('Follow OWASP Java security guidelines');
        break;
    }

    return Array.from(recommendations);
  }

  private mapToCompliance(vulnerabilities: SecurityVulnerability[]): { owasp: string[]; cwe: string[] } {
    const owasp = new Set<string>();
    const cwe = new Set<string>();

    vulnerabilities.forEach(vuln => {
      if (vuln.owaspCategory) {
        owasp.add(vuln.owaspCategory);
      }
      if (vuln.cwe) {
        cwe.add(vuln.cwe);
      }
    });

    return {
      owasp: Array.from(owasp),
      cwe: Array.from(cwe),
    };
  }
}

export const securityScanner = new SecurityScannerTool();