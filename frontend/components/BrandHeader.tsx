/**
 * Branded header (issue #8): logo mark + product name, used across screens.
 * `compact` centers it for the auth card; default lays it out in a page header.
 */
export default function BrandHeader({ compact = false }: { compact?: boolean }) {
  return (
    <div className={compact ? "brand auth-card__brand" : "brand"}>
      <span className="brand-mark" aria-hidden>
        P
      </span>
      <div>
        <div className="brand-name">Pre-legal</div>
        {!compact && (
          <p className="brand-tag">Генерація юридичних угод на основі шаблонів</p>
        )}
      </div>
    </div>
  );
}
