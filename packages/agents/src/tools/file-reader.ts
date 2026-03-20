import * as fs from "fs";
import * as path from "path";
import { AgentTool } from "../types";

const MAX_FILE_SIZE = 100_000; // 100KB

/**
 * Tool for reading file contents from the local filesystem.
 */
export const fileReaderTool: AgentTool = {
  name: "read_file",
  description:
    "Read the contents of a file from the local filesystem. Returns the file content as text. Supports code files, text files, CSV, JSON, and more.",
  input_schema: {
    type: "object" as const,
    properties: {
      path: {
        type: "string",
        description: "The file path to read (relative to current working directory or absolute)",
      },
    },
    required: ["path"],
  },
  async execute(input: Record<string, unknown>): Promise<string> {
    const filePath = input.path as string;
    const resolved = path.resolve(filePath);

    try {
      const stats = fs.statSync(resolved);

      if (stats.isDirectory()) {
        // List directory contents instead
        const entries = fs.readdirSync(resolved, { withFileTypes: true });
        const listing = entries
          .map((e) => `${e.isDirectory() ? "[dir]" : "[file]"} ${e.name}`)
          .join("\n");
        return `Directory listing for ${resolved}:\n\n${listing}`;
      }

      if (stats.size > MAX_FILE_SIZE) {
        return `File ${resolved} is too large (${(stats.size / 1024).toFixed(1)}KB). Maximum supported size is ${MAX_FILE_SIZE / 1024}KB.`;
      }

      const content = fs.readFileSync(resolved, "utf-8");
      const ext = path.extname(resolved).toLowerCase();
      const language = getLanguage(ext);

      return `File: ${resolved} (${stats.size} bytes, ${language})\n\n${content}`;
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      return `Error reading file ${resolved}: ${message}`;
    }
  },
};

/**
 * Tool for listing files in a directory.
 */
export const listFilesTool: AgentTool = {
  name: "list_files",
  description:
    "List files in a directory. Returns file names, sizes, and types. Optionally recurse into subdirectories.",
  input_schema: {
    type: "object" as const,
    properties: {
      path: {
        type: "string",
        description: "Directory path to list (relative or absolute)",
      },
      recursive: {
        type: "boolean",
        description: "Whether to list files recursively (default: false)",
      },
      pattern: {
        type: "string",
        description: "File extension filter, e.g. '.ts' or '.py'",
      },
    },
    required: ["path"],
  },
  async execute(input: Record<string, unknown>): Promise<string> {
    const dirPath = path.resolve(input.path as string);
    const recursive = (input.recursive as boolean) ?? false;
    const pattern = input.pattern as string | undefined;

    try {
      const files = listDir(dirPath, recursive, pattern, dirPath);

      if (files.length === 0) {
        return `No files found in ${dirPath}${pattern ? ` matching ${pattern}` : ""}.`;
      }

      return `Files in ${dirPath}:\n\n${files.join("\n")}`;
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      return `Error listing ${dirPath}: ${message}`;
    }
  },
};

function listDir(
  dir: string,
  recursive: boolean,
  pattern: string | undefined,
  root: string
): string[] {
  const results: string[] = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const relPath = path.relative(root, fullPath);

    if (entry.name.startsWith(".") || entry.name === "node_modules") continue;

    if (entry.isDirectory()) {
      results.push(`[dir] ${relPath}/`);
      if (recursive) {
        results.push(...listDir(fullPath, true, pattern, root));
      }
    } else {
      if (pattern && !entry.name.endsWith(pattern)) continue;
      const stats = fs.statSync(fullPath);
      results.push(
        `[file] ${relPath} (${formatSize(stats.size)})`
      );
    }
  }

  return results;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

function getLanguage(ext: string): string {
  const map: Record<string, string> = {
    ".ts": "TypeScript",
    ".tsx": "TypeScript (JSX)",
    ".js": "JavaScript",
    ".jsx": "JavaScript (JSX)",
    ".py": "Python",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown",
    ".html": "HTML",
    ".css": "CSS",
    ".sql": "SQL",
    ".sh": "Shell",
    ".csv": "CSV",
    ".xml": "XML",
    ".toml": "TOML",
  };
  return map[ext] ?? "Text";
}
