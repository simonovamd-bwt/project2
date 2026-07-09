import BrandHeader from "../components/BrandHeader";
import AuthCard from "../components/AuthCard";
import DocumentHistory from "../components/DocumentHistory";

export default function HomePage() {
  return (
    <main>
      <div className="app-header">
        <BrandHeader />
      </div>

      <AuthCard />

      <section style={{ marginTop: "3rem" }}>
        <h2 className="section-title">Історія документів</h2>
        <DocumentHistory />
      </section>
    </main>
  );
}
