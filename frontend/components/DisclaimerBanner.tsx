/**
 * C23: persistent disclaimer banner shown on every relevant view.
 */
export default function DisclaimerBanner({ text }: { text?: string }) {
  if (text) {
    return (
      <div className="disclaimer-banner">
        <p>{text}</p>
      </div>
    );
  }
  return (
    <div className="disclaimer-banner">
      <p>
        <strong>Information, not advice.</strong> Namma Nyaya explains
        documents. It isn&apos;t a lawyer and can be wrong.
      </p>
    </div>
  );
}
