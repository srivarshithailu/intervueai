// Final report: scores, feedback, communication and camera metrics. Placeholder until M3.

import { Link, useParams } from "react-router";

export default function ReportPage() {
  const { id } = useParams();
  return (
    <>
      <h1>Report</h1>
      <p className="muted">Report {id}: the report page is built in milestone M3.</p>
      <Link to="/">Back to home</Link>
    </>
  );
}
