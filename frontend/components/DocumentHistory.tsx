/**
 * Document-history cards (issue #8): each card shows the document type, title,
 * and date. Data is mocked here — the visual foundation for the real list that
 * will fetch /api/documents once the app screen is wired up (#2).
 */
type DocSummary = {
  id: number;
  title: string;
  documentType: string;
  date: string;
};

const MOCK_DOCS: DocSummary[] = [
  { id: 3, title: "NDA with Acme Corp", documentType: "Mutual NDA", date: "09.07.2026" },
  { id: 2, title: "Consulting Agreement", documentType: "Service Agreement", date: "08.07.2026" },
  { id: 1, title: "Freelance Contract", documentType: "Employment", date: "07.07.2026" },
];

export default function DocumentHistory() {
  if (MOCK_DOCS.length === 0) {
    return (
      <div className="empty-state">
        Ще немає збережених документів. Згенеруйте перший — і він зʼявиться тут.
      </div>
    );
  }

  return (
    <div className="doc-grid">
      {MOCK_DOCS.map((doc) => (
        <article key={doc.id} className="doc-card">
          <span className="doc-card__type">{doc.documentType}</span>
          <h3 className="doc-card__title">{doc.title}</h3>
          <span className="doc-card__date">{doc.date}</span>
        </article>
      ))}
    </div>
  );
}
