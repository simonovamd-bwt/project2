import "./globals.css";
import DisclaimerBanner from "../components/DisclaimerBanner";
import DisclaimerFooter from "../components/DisclaimerFooter";

export const metadata = {
  title: "Pre-legal",
  description: "SaaS для генерації юридичних угод на основі шаблонів",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="uk">
      <body>
        <DisclaimerBanner />
        {children}
        <DisclaimerFooter />
      </body>
    </html>
  );
}
