"use client";

import React, { useEffect, useState } from "react";
import { StageEditor } from "./components/StageEditor";
import { fetchAdminStages, saveAdminStage, AdminStage } from "./lib/adminClient";

export default function AdminHomePage() {
  const [stages, setStages] = useState<AdminStage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAdminStages();
      setStages(data.sort((a, b) => a.order_index - b.order_index));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const handleSaveStage = async (stage: AdminStage) => {
    try {
      const saved = await saveAdminStage(stage);
      setStages((prev) =>
        prev.map((s) => (s.id === saved.id ? saved : s))
      );
    } catch (e) {
      alert((e as Error).message);
    }
  };

  return (
    <main style={{ padding: 24 }}>
      <h1 style={{ marginBottom: 8 }}>ניהול שלבים</h1>
      <p style={{ marginBottom: 16, color: "#555" }}>
        עריכת טקסט של שלבים ופריטי צ&apos;קליסט. השינויים נשמרים ב‑API שבו
        משתמשת אפליקציית המובייל.
      </p>
      {error && (
        <div
          style={{
            backgroundColor: "#ffe5e5",
            color: "#b00020",
            padding: 8,
            marginBottom: 12,
            borderRadius: 4
          }}
        >
          {error}
        </div>
      )}
      {loading ? (
        <p>טוען…</p>
      ) : (
        <div style={{ display: "grid", gap: 16 }}>
          {stages.map((stage) => (
            <StageEditor
              key={stage.id}
              stage={stage}
              onChange={handleSaveStage}
            />
          ))}
        </div>
      )}
    </main>
  );
}

