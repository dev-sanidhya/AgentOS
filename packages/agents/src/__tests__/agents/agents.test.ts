import { configure } from "../../config";

// Mock the Claude Agent SDK for all agent tests
jest.mock("@anthropic-ai/claude-agent-sdk", () => ({
  query: jest.fn().mockReturnValue(
    (async function* () {
      yield {
        type: "assistant",
        message: {
          content: [{ type: "text", text: "Agent response" }],
        },
      };
      yield {
        type: "result",
        subtype: "success",
        result: "Agent response",
        total_cost_usd: 0.001,
        num_turns: 1,
        usage: { input_tokens: 100, output_tokens: 50 },
      };
    })()
  ),
}));

describe("Pre-built Agents", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    process.env.CLAUDE_CODE_OAUTH_TOKEN = "test-oauth-token";
    configure({});

    // Re-mock query for each test (since generators are consumed)
    const sdk = require("@anthropic-ai/claude-agent-sdk");
    sdk.query.mockReturnValue(
      (async function* () {
        yield {
          type: "assistant",
          message: {
            content: [{ type: "text", text: "Agent response" }],
          },
        };
        yield {
          type: "result",
          subtype: "success",
          result: "Agent response",
          total_cost_usd: 0.001,
          num_turns: 1,
          usage: { input_tokens: 100, output_tokens: 50 },
        };
      })()
    );
  });

  afterEach(() => {
    delete process.env.CLAUDE_CODE_OAUTH_TOKEN;
  });

  describe("ResearchAgent", () => {
    it("should be importable and have a run method", async () => {
      const { ResearchAgent } = await import("../../agents/research");
      expect(ResearchAgent).toBeDefined();
      expect(typeof ResearchAgent.run).toBe("function");
    });

    it("should return a valid result", async () => {
      const { ResearchAgent } = await import("../../agents/research");
      const result = await ResearchAgent.run("test query");
      expect(result).toHaveProperty("output");
      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("toolCalls");
      expect(result).toHaveProperty("tokensUsed");
      expect(result).toHaveProperty("cost");
      expect(result).toHaveProperty("duration");
      expect(result).toHaveProperty("loops");
    });
  });

  describe("CodeReviewAgent", () => {
    it("should be importable and have a run method", async () => {
      const { CodeReviewAgent } = await import("../../agents/code-review");
      expect(CodeReviewAgent).toBeDefined();
      expect(typeof CodeReviewAgent.run).toBe("function");
    });
  });

  describe("ContentWriter", () => {
    it("should be importable and have a run method", async () => {
      const { ContentWriter } = await import("../../agents/content-writer");
      expect(ContentWriter).toBeDefined();
      expect(typeof ContentWriter.run).toBe("function");
    });
  });

  describe("DataAnalyst", () => {
    it("should be importable and have a run method", async () => {
      const { DataAnalyst } = await import("../../agents/data-analyst");
      expect(DataAnalyst).toBeDefined();
      expect(typeof DataAnalyst.run).toBe("function");
    });
  });

  describe("CompetitorAnalyzer", () => {
    it("should be importable and have a run method", async () => {
      const { CompetitorAnalyzer } = await import(
        "../../agents/competitor-analyzer"
      );
      expect(CompetitorAnalyzer).toBeDefined();
      expect(typeof CompetitorAnalyzer.run).toBe("function");
    });
  });

  describe("EmailDrafter", () => {
    it("should be importable and have a run method", async () => {
      const { EmailDrafter } = await import("../../agents/email-drafter");
      expect(EmailDrafter).toBeDefined();
      expect(typeof EmailDrafter.run).toBe("function");
    });

    it("should return a valid result", async () => {
      const { EmailDrafter } = await import("../../agents/email-drafter");
      const result = await EmailDrafter.run("Write a follow-up email");
      expect(result.success).toBe(true);
      expect(result.output).toBeTruthy();
    });
  });

  describe("SEOAuditor", () => {
    it("should be importable and have a run method", async () => {
      const { SEOAuditor } = await import("../../agents/seo-auditor");
      expect(SEOAuditor).toBeDefined();
      expect(typeof SEOAuditor.run).toBe("function");
    });
  });

  describe("BugTriager", () => {
    it("should be importable and have a run method", async () => {
      const { BugTriager } = await import("../../agents/bug-triager");
      expect(BugTriager).toBeDefined();
      expect(typeof BugTriager.run).toBe("function");
    });
  });
});

describe("Agent exports", () => {
  beforeEach(() => {
    process.env.CLAUDE_CODE_OAUTH_TOKEN = "test-oauth-token";
  });

  afterEach(() => {
    delete process.env.CLAUDE_CODE_OAUTH_TOKEN;
  });

  it("should export all 8 agents from the main index", async () => {
    const agents = await import("../../index");
    expect(agents.ResearchAgent).toBeDefined();
    expect(agents.CodeReviewAgent).toBeDefined();
    expect(agents.ContentWriter).toBeDefined();
    expect(agents.DataAnalyst).toBeDefined();
    expect(agents.CompetitorAnalyzer).toBeDefined();
    expect(agents.EmailDrafter).toBeDefined();
    expect(agents.SEOAuditor).toBeDefined();
    expect(agents.BugTriager).toBeDefined();
  });

  it("should export configure and createAgent", async () => {
    const agents = await import("../../index");
    expect(agents.configure).toBeDefined();
    expect(agents.createAgent).toBeDefined();
  });

  it("should export Agent base class", async () => {
    const agents = await import("../../index");
    expect(agents.Agent).toBeDefined();
  });
});
