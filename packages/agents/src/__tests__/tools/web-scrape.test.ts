import { webScrapeTool } from "../../tools/web-scrape";

// Mock axios
jest.mock("axios", () => ({
  get: jest.fn(),
}));

const axios = require("axios");

describe("webScrapeTool", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should have correct metadata", () => {
    expect(webScrapeTool.name).toBe("web_scrape");
    expect(webScrapeTool.description).toBeTruthy();
    expect(webScrapeTool.input_schema.properties).toHaveProperty("url");
    expect(webScrapeTool.input_schema.required).toContain("url");
  });

  it("should extract content from HTML", async () => {
    axios.get.mockResolvedValue({
      data: `
        <html>
          <head><title>Test Page</title></head>
          <body>
            <nav>Navigation</nav>
            <article>
              <h1>Article Title</h1>
              <p>This is the main content of the article that should be extracted by the scraper tool for analysis purposes.</p>
            </article>
            <footer>Footer content</footer>
          </body>
        </html>
      `,
    });

    const result = await webScrapeTool.execute({ url: "https://example.com/article" });

    expect(result).toContain("Test Page");
    expect(result).toContain("main content");
    // Nav and footer should be removed
    expect(result).not.toContain("Navigation");
    expect(result).not.toContain("Footer content");
  });

  it("should use custom CSS selector when provided", async () => {
    axios.get.mockResolvedValue({
      data: `
        <html>
          <body>
            <div class="sidebar">Sidebar content here</div>
            <div class="main-content">This is the targeted content that we want to extract specifically.</div>
          </body>
        </html>
      `,
    });

    const result = await webScrapeTool.execute({
      url: "https://example.com",
      selector: ".main-content",
    });

    expect(result).toContain("targeted content");
  });

  it("should handle fetch errors", async () => {
    axios.get.mockRejectedValue(new Error("Connection refused"));

    const result = await webScrapeTool.execute({ url: "https://bad.example.com" });

    expect(result).toContain("Failed to scrape");
    expect(result).toContain("Connection refused");
  });

  it("should handle pages with no meaningful content", async () => {
    axios.get.mockResolvedValue({
      data: "<html><body><script>var x=1;</script></body></html>",
    });

    const result = await webScrapeTool.execute({ url: "https://empty.example.com" });

    expect(result).toContain("Could not extract meaningful content");
  });

  it("should truncate very long content", async () => {
    const longContent = "A".repeat(20000);
    axios.get.mockResolvedValue({
      data: `<html><body><article>${longContent}</article></body></html>`,
    });

    const result = await webScrapeTool.execute({ url: "https://long.example.com" });

    expect(result).toContain("[Content truncated...]");
    expect(result.length).toBeLessThan(20000);
  });
});
