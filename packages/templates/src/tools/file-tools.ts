import { Tool, AgentContext } from '@agent-platform/core';
import { promises as fs } from 'fs';
import path from 'path';
import { z } from 'zod';

/**
 * Read File Tool
 * Read contents of a file
 */
export const readFileTool: Tool = {
  name: 'read-file',
  description: 'Read the contents of a file',
  parameters: z.object({
    filePath: z.string().describe('Path to the file to read'),
    encoding: z.string().optional().default('utf-8').describe('File encoding'),
  }),

  async execute(params: { filePath: string; encoding?: string }, context: AgentContext) {
    const { filePath, encoding = 'utf-8' } = params;

    try {
      context.emit?.('tool:log', {
        message: `Reading file: ${filePath}`,
      });

      const content = await fs.readFile(filePath, encoding as BufferEncoding);

      return {
        filePath,
        content,
        size: content.length,
      };
    } catch (error) {
      throw new Error(`Failed to read file ${filePath}: ${error}`);
    }
  },
};

/**
 * Write File Tool
 * Write content to a file
 */
export const writeFileTool: Tool = {
  name: 'write-file',
  description: 'Write content to a file',
  parameters: z.object({
    filePath: z.string().describe('Path to the file to write'),
    content: z.string().describe('Content to write'),
    encoding: z.string().optional().default('utf-8').describe('File encoding'),
  }),

  async execute(
    params: { filePath: string; content: string; encoding?: string },
    context: AgentContext
  ) {
    const { filePath, content, encoding = 'utf-8' } = params;

    try {
      context.emit?.('tool:log', {
        message: `Writing to file: ${filePath}`,
      });

      // Ensure directory exists
      const dir = path.dirname(filePath);
      await fs.mkdir(dir, { recursive: true });

      await fs.writeFile(filePath, content, encoding as BufferEncoding);

      return {
        filePath,
        size: content.length,
        success: true,
      };
    } catch (error) {
      throw new Error(`Failed to write file ${filePath}: ${error}`);
    }
  },
};

/**
 * List Files Tool
 * List files in a directory
 */
export const listFilesTool: Tool = {
  name: 'list-files',
  description: 'List files in a directory',
  parameters: z.object({
    dirPath: z.string().describe('Path to the directory'),
    recursive: z.boolean().optional().default(false).describe('List files recursively'),
    pattern: z.string().optional().describe('File pattern to match (e.g., *.js)'),
  }),

  async execute(
    params: { dirPath: string; recursive?: boolean; pattern?: string },
    context: AgentContext
  ) {
    const { dirPath, recursive = false, pattern } = params;

    try {
      context.emit?.('tool:log', {
        message: `Listing files in: ${dirPath}`,
      });

      const files: string[] = [];

      async function scanDir(currentPath: string) {
        const entries = await fs.readdir(currentPath, { withFileTypes: true });

        for (const entry of entries) {
          const fullPath = path.join(currentPath, entry.name);

          if (entry.isDirectory()) {
            if (recursive) {
              await scanDir(fullPath);
            }
          } else {
            if (!pattern || new RegExp(pattern).test(entry.name)) {
              files.push(fullPath);
            }
          }
        }
      }

      await scanDir(dirPath);

      return {
        dirPath,
        files,
        count: files.length,
      };
    } catch (error) {
      throw new Error(`Failed to list files in ${dirPath}: ${error}`);
    }
  },
};

/**
 * File Stats Tool
 * Get file statistics and metadata
 */
export const fileStatsTool: Tool = {
  name: 'file-stats',
  description: 'Get file statistics and metadata',
  parameters: z.object({
    filePath: z.string().describe('Path to the file'),
  }),

  async execute(params: { filePath: string }, context: AgentContext) {
    const { filePath } = params;

    try {
      const stats = await fs.stat(filePath);

      return {
        filePath,
        size: stats.size,
        created: stats.birthtime,
        modified: stats.mtime,
        isFile: stats.isFile(),
        isDirectory: stats.isDirectory(),
      };
    } catch (error) {
      throw new Error(`Failed to get stats for ${filePath}: ${error}`);
    }
  },
};
