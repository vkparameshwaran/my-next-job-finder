export type SectionKind = "experience" | "projects" | "education";

export type IssueKind =
  | "no_metric"
  | "weak_verb"
  | "vague"
  | "passive_voice"
  | "keyword_miss"
  | "redundant"
  | "too_long"
  | "ats_unfriendly"
  | "missing_summary"
  | "timeline_gap"
  | "short_stint";

export type Severity = "info" | "warning" | "error";

export interface Contact {
  name: string;
  email?: string | null;
  phone?: string | null;
  location?: string | null;
  linkedin?: string | null;
  github?: string | null;
  portfolio?: string | null;
}

export interface Bullet {
  id: string;
  text: string;
  section: SectionKind;
  parent_id: string;
}

export interface Job {
  id: string;
  company: string;
  title: string;
  location?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  bullets: Bullet[];
}

export interface Project {
  id: string;
  name: string;
  link?: string | null;
  description?: string | null;
  bullets: Bullet[];
}

export interface Degree {
  id: string;
  institution: string;
  qualification: string;
  field_of_study?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  grade?: string | null;
  bullets: Bullet[];
}

export interface ResumeDoc {
  contact: Contact;
  summary: string | null;
  experience: Job[];
  projects: Project[];
  education: Degree[];
  skills: string[];
  raw_text: string;
}

export interface Issue {
  kind: IssueKind;
  message: string;
  severity: Severity;
}

export interface Suggestion {
  id: string;
  bullet_id: string;
  issue: IssueKind;
  rationale: string;
  rewrite: string;
  accepted: boolean | null;
}

export interface GapReport {
  ats_score: number;
  issues: Issue[];
  suggestions: Suggestion[];
  keyword_overlap: Record<string, boolean>;
}

export interface AnalyzeResponse {
  record_id: string;
  resume: ResumeDoc;
  report: GapReport;
}
