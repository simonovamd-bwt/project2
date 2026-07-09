import BrandHeader from "../components/BrandHeader";
import ChatInterface from "../components/ChatInterface";
import DocumentHistory from "../components/DocumentHistory";

export default function HomePage() {
  return (
    <main>
      <div className="app-header">
        <BrandHeader />
      </div>

      <section>
        <h2 className="section-title">Створити документ</h2>
        <ChatInterface />
      </section>

      <section style={{ marginTop: "3rem" }} className="chat-history-section">
        <h2 className="section-title">Історія документів</h2>
        <DocumentHistory />
      </section>
    </main>
  );
}
