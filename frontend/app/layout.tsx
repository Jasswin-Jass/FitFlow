import type { Metadata } from "next";
import { Toaster } from "sonner";
import QueryProvider from "@/lib/query-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "FitFlow — Business Intelligence Platform for Gyms",
  description: "Turn gym operations data into actionable business intelligence.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#09090b] text-zinc-100 antialiased">
        <QueryProvider>
          {children}
          <Toaster
            theme="dark"
            position="bottom-right"
            toastOptions={{
              style: {
                background: "#18181b",
                border: "1px solid #27272a",
                color: "#fafafa",
              },
            }}
          />
        </QueryProvider>
      </body>
    </html>
  );
}
