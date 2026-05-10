import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import SuggestionDiff from "../components/SuggestionDiff";
import type { Bullet, Suggestion } from "../types";

const bullet: Bullet = {
  id: "b1",
  text: "Was responsible for stuff",
  section: "experience",
  parent_id: "job-1",
};

function makeSuggestion(accepted: boolean | null = null): Suggestion {
  return {
    id: "s1",
    bullet_id: "b1",
    issue: "weak_verb",
    rationale: "passive voice",
    rewrite: "Built thing X for 10K users",
    accepted,
  };
}

describe("SuggestionDiff", () => {
  it("renders original and rewrite text", () => {
    render(
      <SuggestionDiff bullet={bullet} suggestion={makeSuggestion()} onToggle={vi.fn()} />,
    );
    expect(screen.getByText(bullet.text)).toBeInTheDocument();
    expect(screen.getByText(/Built thing X/)).toBeInTheDocument();
  });

  it("calls onToggle(true) when Accept is clicked", async () => {
    const onToggle = vi.fn();
    render(
      <SuggestionDiff bullet={bullet} suggestion={makeSuggestion()} onToggle={onToggle} />,
    );
    await userEvent.click(screen.getByRole("button", { name: /accept/i }));
    expect(onToggle).toHaveBeenCalledWith("s1", true);
  });

  it("calls onToggle(false) when Reject is clicked", async () => {
    const onToggle = vi.fn();
    render(
      <SuggestionDiff bullet={bullet} suggestion={makeSuggestion()} onToggle={onToggle} />,
    );
    await userEvent.click(screen.getByRole("button", { name: /reject/i }));
    expect(onToggle).toHaveBeenCalledWith("s1", false);
  });

  it("toggles back to null when an active state is clicked again", async () => {
    const onToggle = vi.fn();
    render(
      <SuggestionDiff
        bullet={bullet}
        suggestion={makeSuggestion(true)}
        onToggle={onToggle}
      />,
    );
    await userEvent.click(screen.getByRole("button", { name: /accepted/i }));
    expect(onToggle).toHaveBeenCalledWith("s1", null);
  });
});
