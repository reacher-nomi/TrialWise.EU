import { useState } from "react";
import { analyzeCriteria, getHealth, type AnalysisResult, type Criterion, type Health } from "./api";

const EXAMPLE = `Inclusion Criteria:
* Age ≥ 18 years
* Histologically confirmed stage IV non-small cell lung cancer
* ECOG performance status of 0 or 1
* Hemoglobin ≥ 9 g/dL

Exclusion Criteria:
* Known brain metastases
* Pregnant or breastfeeding women`;

function formatValue(c: Criterion): string {
  if (c.value === null) return "—";
  const v = Array.isArray(c.value) ? c.value.join("–") : String(c.value);
  return `${c.operator ?? ""} ${v} ${c.unit ?? ""}`.trim();
}

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [text, setText] = useState(EXAMPLE);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // "One-button app": proves frontend -> backend -> database all work together
  async function checkSystem() {
    setError(null);
    try {
      setHealth(await getHealth());
    } catch (e) {
      setHealth(null);
      setError(String(e));
    }
  }

  async function analyze() {
    setLoading(true);
    setError(null);
    try {
      setResult(await analyzeCriteria(text));
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false); // runs on success AND failure
    }
  }

  return (
    <main>
      <header>
        <h1>TrialWise</h1>
        <p className="tagline">Clinical trial eligibility criteria, made structured and explainable.</p>
      </header>

      <section className="card">
        <h2>System check</h2>
        <button onClick={checkSystem}>Check system</button>
        {health && (
          <p role="status" className={health.status === "ok" ? "ok" : "warn"}>
            API: {health.status} · Database: {health.database} · Env: {health.environment}
          </p>
        )}
      </section>

      <section className="card">
        <h2>Criteria Analyzer</h2>
        <label htmlFor="criteria">Paste eligibility criteria</label>
        <textarea
          id="criteria"
          rows={12}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button onClick={analyze} disabled={loading || text.trim().length < 5}>
          {loading ? "Analyzing…" : "Analyze"}
        </button>
      </section>

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      {result && (
        <section className="card">
          <h2>Results</h2>
          <p>
            {result.summary.total} criteria · {result.summary.structured} structured ·{" "}
            <strong>{result.summary.manual_review} need manual review</strong>
          </p>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Original text (evidence)</th>
                  <th>Field</th>
                  <th>Rule</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {result.criteria.map((c) => (
                  <tr key={c.span.join("-")}>
                    <td>{c.criterion_type}</td>
                    <td>{c.text}</td>
                    <td>{c.field ?? "—"}</td>
                    <td>{formatValue(c)}</td>
                    <td>
                      <span className={`badge ${c.status}`}>
                        {c.status === "structured" ? "structured" : "manual review"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </main>
  );
}
