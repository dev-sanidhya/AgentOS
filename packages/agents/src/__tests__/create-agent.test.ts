import { createAgent, CustomAgent } from "../create-agent";
import { configure } from "../config";

// Mock the Claude Agent SDK
jest.mock("@anthropic-ai/claude-agent-sdk", () => ({
  query: jest.fn(),
}));

const getQueryMock = () => {
  return require("@anthropic-ai/claude-agent-sdk").query as jest.Mock;
};

describe("createAgent", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    process.env.CLAUDE_CODE_OAUTH_TOKEN = "test-oauth-token";
    configure({});

    // Default mock: return a valid agent config JSON
    const mockQuery = getQueryMock();
    mockQuery.mockReturnValue(
      (async function* () {
        yield {
          type: "result",
          subtype: "success",
          result: JSON.stringify({
            systemPrompt:
              "You are a helpful assistant for summarizing articles.",
            temperature: 0.4,
            maxLoops: 8,
          }),
          total_cost_usd: 0.001,
          num_turns: 1,
          usage: { input_tokens: 100, output_tokens: 200 },
        };
      })()
    );
  });

  afterEach(() => {
    delete process.env.CLAUDE_CODE_OAUTH_TOKEN;
  });

  describe("from string description", () => {
    it("should create a custom agent", async () => {
      const agent = await createAgent(
        "An agent that summarizes news articles"
      );

      expect(agent).toBeInstanceOf(CustomAgent);
      expect(agent.description).toBe(
        "An agent that summarizes news articles"
      );
    });

    it("should have a working run method", async () => {
      const agent = await createAgent("A test agent");

      expect(typeof agent.run).toBe("function");
    });
  });

  describe("from AgentSpec", () => {
    it("should build directly with tools specified (no LLM call)", async () => {
      const mockQuery = getQueryMock();

      const agent = await createAgent({
        task: "Analyze data files",
        inputs: "CSV file path",
        outputs: "Summary statistics",
        tools: ["read_file"],
      });

      // Should NOT call the SDK since tools are specified
      expect(mockQuery).not.toHaveBeenCalled();
      expect(agent).toBeInstanceOf(CustomAgent);
      expect(agent.description).toBe("Analyze data files");
    });

    it("should include additional instructions", async () => {
      const agent = await createAgent({
        task: "Research topics",
        tools: ["web_search"],
        additionalInstructions: "Always include citations",
      });

      expect(agent).toBeInstanceOf(CustomAgent);
    });
  });

  describe("error handling", () => {
    it("should use fallback when SDK returns invalid JSON", async () => {
      const mockQuery = getQueryMock();
      mockQuery.mockReturnValue(
        (async function* () {
          yield {
            type: "result",
            subtype: "success",
            result: "not valid json at all",
            total_cost_usd: 0.001,
            num_turns: 1,
            usage: { input_tokens: 10, output_tokens: 10 },
          };
        })()
      );

      const agent = await createAgent("A test agent");

      // Should still return a working agent (using fallback config)
      expect(agent).toBeInstanceOf(CustomAgent);
    });

    it("should use fallback when SDK throws", async () => {
      const mockQuery = getQueryMock();
      mockQuery.mockImplementation(() => {
        throw new Error("SDK failed");
      });

      const agent = await createAgent("A test agent");
      expect(agent).toBeInstanceOf(CustomAgent);
    });
  });
});
