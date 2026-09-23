/**
 * C23: persistent disclaimer banner shown on every relevant view.
 */
export default function DisclaimerBanner({ text }: { text?: string }) {
  const disclaimer =
    text ||
    "Namma Nyaya provides general legal information, not legal advice. " +
      "For your specific situation, please consult a licensed advocate.";
  return <div className="disclaimer-banner">{disclaimer}</div>;
}
