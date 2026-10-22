// All calls to the backend go through this file.
// Relative URLs ("/api/...") work in Dev (Vite proxy) and Live (nginx proxy).

export type Criterion = {
  criterion_type: "inclusion" | "exclusion";
  text: string;
  span: [number, number];
  field: string | null;
  operator: string | null;
  value: number | string | boolean | number[] | null;
  unit: string | null;
  status: "structured" | "manual_review";
  rules_matched: string[];
};

export type AnalysisResult = {
  method: string;
  analysis_id?: number;
  summary: {
    total: number;
    structured: number;
    manual_review: number;
    inclusion: number;
    exclusion: number;
  };
  criteria: Criterion[];
};

export type Health = { status: string; database: string; environment: string };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    // Show the backend's error message if there is one
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export const getHealth = () => request<Health>("/api/health");

export const analyzeCriteria = (text: string, title = "Untitled") =>
  request<AnalysisResult>("/api/criteria/analyze", {
    method: "POST",
    body: JSON.stringify({ text, title }),
  });
