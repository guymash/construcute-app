"use client";

import React, { useState } from "react";
import type { AdminStage } from "../lib/adminClient";

type Props = {
  stage: AdminStage;
  onChange: (updated: AdminStage) => void;
};

export const StageEditor: React.FC<Props> = ({ stage, onChange }) => {
  const [local, setLocal] = useState<AdminStage>(stage);
  const [saving, setSaving] = useState(false);

  const updateField = (field: keyof AdminStage, value: string) => {
    setLocal((prev) => ({ ...prev, [field]: value }));
  };

  const updateCheckTitle = (index: number, value: string) => {
    setLocal((prev) => {
      const checks = [...prev.checks];
      checks[index] = { ...checks[index], title: value };
      return { ...prev, checks };
    });
  };

  const onSave = async () => {
    setSaving(true);
    try {
      await onChange(local);
    } finally {
      setSaving(false);
    }
  };

  return (
    <section
      style={{
        backgroundColor: "#ffffff",
        borderRadius: 8,
        padding: 16,
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)"
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: 8 }}>
        {local.title}{" "}
        <span style={{ fontSize: 12, color: "#777" }}>({local.slug})</span>
      </h2>

      <div style={{ display: "grid", gap: 8, marginBottom: 12 }}>
        <label>
          <div style={{ fontSize: 12, fontWeight: 600 }}>הסבר קצר</div>
          <textarea
            value={local.short_explanation}
            onChange={(e) => updateField("short_explanation", e.target.value)}
            rows={3}
            style={{ width: "100%" }}
          />
        </label>
        <label>
          <div style={{ fontSize: 12, fontWeight: 600 }}>טעויות נפוצות</div>
          <textarea
            value={local.common_mistakes}
            onChange={(e) => updateField("common_mistakes", e.target.value)}
            rows={3}
            style={{ width: "100%" }}
          />
        </label>
        <label>
          <div style={{ fontSize: 12, fontWeight: 600 }}>מה חשוב לתעד</div>
          <textarea
            value={local.must_document}
            onChange={(e) => updateField("must_document", e.target.value)}
            rows={3}
            style={{ width: "100%" }}
          />
        </label>
      </div>

      <div>
        <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>
          פריטי צ&apos;קליסט
        </div>
        {local.checks.map((c, idx) => (
          <div key={c.id} style={{ marginBottom: 4 }}>
            <input
              type="text"
              value={c.title}
              onChange={(e) => updateCheckTitle(idx, e.target.value)}
              style={{ width: "100%" }}
            />
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={onSave}
        disabled={saving}
        style={{
          marginTop: 12,
          padding: "6px 12px",
          borderRadius: 4,
          border: "none",
          backgroundColor: "#2563eb",
          color: "#ffffff",
          cursor: "pointer",
          opacity: saving ? 0.7 : 1
        }}
      >
        {saving ? "שומר…" : "שמור שינויים"}
      </button>
    </section>
  );
};

