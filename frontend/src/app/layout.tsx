import "./globals.css";
import { Navbar } from "@/components/navbar";

export const metadata = {
  title: "Universal AI Discovery Platform",
  description: "AI-Powered Discovery and Entity Intelligence Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-gray-800/60 py-6 text-center text-xs text-gray-400">
          <p>© 2026 Universal AI Discovery Platform. Powered by FastAPI, PostgreSQL pgvector & Next.js.</p>
        </footer>
      </body>
    </html>
  );
}
