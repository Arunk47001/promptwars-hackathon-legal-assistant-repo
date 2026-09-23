/**
 * C23: distinct "please consult a lawyer / legal aid" screen, wired to
 * C16's high-stakes redirect message from the backend's guardrail metadata.
 */
export default function LegalAidRedirect({ message }: { message: string }) {
  return (
    <div className="legal-aid-redirect" role="alert">
      <h3>This needs a lawyer, not this app</h3>
      <p>{message}</p>
    </div>
  );
}
