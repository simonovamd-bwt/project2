/**
 * Legal disclaimer shown above any document-generation UI.
 *
 * Required by issue #7: every generated document must be clearly marked as a
 * draft subject to legal review, and not legal advice. Rendered in the root
 * layout so it appears on every page, including the future chat interface (#2).
 */
export default function DisclaimerBanner() {
  return (
    <div className="disclaimer-banner" role="note">
      <strong>Draft only.</strong> Documents generated here are drafts and are{" "}
      <strong>subject to legal review</strong>. They are not legal advice.
    </div>
  );
}
