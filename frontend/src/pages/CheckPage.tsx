// Pre-interview check: mic, camera, speech output and consent. Placeholder until M4-M7.

import { Link } from "react-router";

export default function CheckPage() {
  return (
    <>
      <h1>Check your setup</h1>
      <p className="muted">Microphone, camera and voice checks are built in milestones M4 to M7.</p>
      <Link to="/">Back to home</Link>
    </>
  );
}
