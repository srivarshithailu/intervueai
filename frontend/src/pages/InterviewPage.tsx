// The live interview screen: question, status line, transcript and controls. Placeholder until M3.

import { Link, useParams } from "react-router";

export default function InterviewPage() {
  const { id } = useParams();
  return (
    <>
      <h1>Interview</h1>
      <p className="muted">Interview {id}: the interview screen is built in milestone M3.</p>
      <Link to="/">Back to home</Link>
    </>
  );
}
