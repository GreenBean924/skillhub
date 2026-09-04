import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { SecurityBadge } from "@/components/SecurityBadge";

describe("SecurityBadge", () => {
  it("renders safe level", () => {
    render(<SecurityBadge level="safe" score={95} />);
    expect(screen.getByText("安全")).toBeInTheDocument();
  });

  it("renders low risk level", () => {
    render(<SecurityBadge level="low" score={75} />);
    expect(screen.getByText("低风险")).toBeInTheDocument();
  });

  it("renders medium risk level", () => {
    render(<SecurityBadge level="medium" score={55} />);
    expect(screen.getByText("中等风险")).toBeInTheDocument();
  });

  it("renders high risk level", () => {
    render(<SecurityBadge level="high" score={30} />);
    expect(screen.getByText("高风险")).toBeInTheDocument();
  });

  it("renders critical risk level", () => {
    render(<SecurityBadge level="critical" score={10} />);
    expect(screen.getByText("极高风险")).toBeInTheDocument();
  });

  it("renders pending level", () => {
    render(<SecurityBadge level="pending" score={0} />);
    expect(screen.getByText("待审查")).toBeInTheDocument();
  });

  it("displays score in large mode", () => {
    render(<SecurityBadge level="safe" score={95} size="lg" />);
    expect(screen.getByText("Score: 95/100")).toBeInTheDocument();
  });
});
