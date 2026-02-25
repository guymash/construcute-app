import type { Metadata } from "next";
import React from "react";

export const metadata: Metadata = {
  title: "Constructure Admin",
  description: "Admin panel for stages and checklists"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          fontFamily:
            "-apple-system, BlinkMacSystemFont, system-ui, -system-ui, sans-serif",
          backgroundColor: "#f5f5f5"
        }}
      >
        {children}
      </body>
    </html>
  );
}

