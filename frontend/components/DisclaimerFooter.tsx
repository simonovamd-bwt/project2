/**
 * Short recurring reminder in the page footer (issue #7).
 *
 * Mirrors the banner's message in a compact form so the "draft, subject to
 * legal review" caveat is present even when the banner scrolls out of view.
 */
export default function DisclaimerFooter() {
  return (
    <footer className="disclaimer-footer">
      Prototype · documents are drafts subject to legal review — not legal advice.
    </footer>
  );
}
