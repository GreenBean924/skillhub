import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { TagChip } from "@/components/TagChip";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("TagChip", () => {
  it("renders tag name", () => {
    render(<TagChip tag="security" />);
    expect(screen.getByText("security")).toBeInTheDocument();
  });

  it("renders as button by default", () => {
    render(<TagChip tag="python" />);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("renders as link when href provided", () => {
    render(<TagChip tag="python" href="/tags/python" />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/tags/python");
  });

  it("applies active styles when active", () => {
    const { container } = render(<TagChip tag="test" active />);
    expect(container.firstChild).toHaveClass("bg-neon-magenta/10");
  });
});
