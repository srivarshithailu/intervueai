// Diagnostics: provider tests, mic, camera and speech timings as plain text. Placeholder until M7.

import { Link } from "react-router";

export default function DiagnosticsPage() {
  return (
    <>
      <h1>Diagnostics</h1>
      <p className="muted">The full diagnostics panel is built in milestone M7.</p>
      <Link to="/">Back to home</Link>
    </>
  );
}
