import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import GapReportCard from "../components/GapReportCard";
import type { GapReport } from "../types";

const baseReport: GapReport = {
  ats_score: 72,
  issues: [
    { kind: "missing_summary", message: "No professional summary", severity: "warning" },
  ],
  suggestions: [],
  keyword_overlap: {},
};

describe("GapReportCard", () => {
  it("renders the ATS score", () => {
    render(<GapReportCard report={baseReport} />);
    expect(screen.getByText("72")).toBeInTheDocument();
    expect(screen.getByText(/out of 100/i)).toBeInTheDocument();
  });

  it("renders high-level issues", () => {
    render(<GapReportCard report={baseReport} />);
    expect(screen.getByText(/no professional summary/i)).toBeInTheDocument();
  });

  it("renders 'no issues' when issues array is empty", () => {
    render(<GapReportCard report={{ ...baseReport, issues: [] }} />);
    expect(screen.getByText(/no high-level issues/i)).toBeInTheDocument();
  });

  it("renders keyword overlap when present", () => {
    render(
      <GapReportCard
        report={{
          ...baseReport,
          keyword_overlap: { python: true, kubernetes: false },
        }}
      />,
    );
    expect(screen.getByText(/keyword overlap/i)).toBeInTheDocument();
    expect(screen.getByText("python")).toBeInTheDocument();
    expect(screen.getByText("kubernetes")).toBeInTheDocument();
    expect(screen.getByText(/1\/2/)).toBeInTheDocument();
  });

  it("hides the keyword section when overlap is empty", () => {
    render(<GapReportCard report={baseReport} />);
    expect(screen.queryByText(/keyword overlap/i)).toBeNull();
  });
});
