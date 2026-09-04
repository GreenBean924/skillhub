import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { SearchBar } from "@/components/SearchBar";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("SearchBar", () => {
  it("renders with placeholder text", () => {
    render(<SearchBar />);
    expect(screen.getByPlaceholderText(/搜索技能/)).toBeInTheDocument();
  });

  it("renders with default value", () => {
    render(<SearchBar defaultValue="python" />);
    expect(screen.getByDisplayValue("python")).toBeInTheDocument();
  });

  it("shows clear button when value is present", () => {
    render(<SearchBar defaultValue="test" />);
    const clearBtn = screen.getByRole("button", { name: "" });
    expect(clearBtn).toBeInTheDocument();
  });

  it("clears input when clear button clicked", () => {
    render(<SearchBar defaultValue="test" />);
    const clearBtn = screen.getByRole("button", { name: "" });
    fireEvent.click(clearBtn);
    expect(screen.getByPlaceholderText(/搜索技能/)).toHaveValue("");
  });

  it("renders submit button", () => {
    render(<SearchBar />);
    expect(screen.getByRole("button", { name: "搜索" })).toBeInTheDocument();
  });
});
