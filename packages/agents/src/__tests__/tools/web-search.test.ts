import { webSearchTool } from "../../tools/web-search";

// Mock axios
jest.mock("axios", () => ({
  get: jest.fn(),
}));

const axios = require("axios");

describe("webSearchTool", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    delete process.env.BRAVE_SEARCH_API_KEY;
  });

  it("should have correct metadata", () => {
    expect(webSearchTool.name).toBe("web_search");
    expect(webSearchTool.description).toBeTruthy();
    expect(webSearchTool.input_schema.properties).toHaveProperty("query");
    expect(webSearchTool.input_schema.required).toContain("query");
  });

  describe("with Brave API key", () => {
    it("should use Brave Search when key is set", async () => {
      process.env.BRAVE_SEARCH_API_KEY = "test-brave-key";

      axios.get.mockResolvedValue({
        data: {
          web: {
            results: [
              {
                title: "Test Result",
                url: "https://example.com",
                description: "A test result",
              },
            ],
          },
        },
      });

      const result = await webSearchTool.execute({ query: "test query" });

      expect(axios.get).toHaveBeenCalledWith(
        "https://api.search.brave.com/res/v1/web/search",
        expect.objectContaining({
          params: { q: "test query", count: 5 },
          headers: expect.objectContaining({
            "X-Subscription-Token": "test-brave-key",
          }),
        })
      );
      expect(result).toContain("Test Result");
      expect(result).toContain("https://example.com");
    });

    it("should handle empty Brave results", async () => {
      process.env.BRAVE_SEARCH_API_KEY = "test-brave-key";

      axios.get.mockResolvedValue({
        data: { web: { results: [] } },
      });

      const result = await webSearchTool.execute({ query: "no results" });
      expect(result).toContain("No results found");
    });

    it("should respect max_results", async () => {
      process.env.BRAVE_SEARCH_API_KEY = "test-brave-key";

      axios.get.mockResolvedValue({
        data: {
          web: {
            results: Array(10).fill({
              title: "Result",
              url: "https://example.com",
              description: "desc",
            }),
          },
        },
      });

      await webSearchTool.execute({ query: "test", max_results: 3 });

      expect(axios.get).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          params: { q: "test", count: 3 },
        })
      );
    });
  });

  describe("with DuckDuckGo fallback", () => {
    it("should use DDG when no Brave key is set", async () => {
      axios.get.mockResolvedValue({
        data: {
          Abstract: "DuckDuckGo abstract result",
          AbstractURL: "https://ddg.example.com",
          RelatedTopics: [],
        },
      });

      const result = await webSearchTool.execute({ query: "test" });

      expect(axios.get).toHaveBeenCalledWith(
        "https://api.duckduckgo.com/",
        expect.objectContaining({
          params: expect.objectContaining({ q: "test" }),
        })
      );
      expect(result).toContain("DuckDuckGo abstract result");
    });

    it("should include related topics from DDG", async () => {
      axios.get.mockResolvedValue({
        data: {
          Abstract: "",
          RelatedTopics: [
            { Text: "Related topic 1", FirstURL: "https://example.com/1" },
            { Text: "Related topic 2", FirstURL: "https://example.com/2" },
          ],
        },
      });

      const result = await webSearchTool.execute({ query: "test" });
      expect(result).toContain("Related topic 1");
      expect(result).toContain("Related topic 2");
    });

    it("should handle DDG errors gracefully", async () => {
      axios.get.mockRejectedValue(new Error("Network error"));

      const result = await webSearchTool.execute({ query: "test" });
      expect(result).toContain("Search failed");
    });

    it("should handle no DDG results", async () => {
      axios.get.mockResolvedValue({
        data: { Abstract: "", RelatedTopics: [] },
      });

      const result = await webSearchTool.execute({ query: "obscure" });
      expect(result).toContain("No results found");
    });
  });
});
