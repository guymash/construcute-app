const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const ADMIN_TOKEN =
  process.env.NEXT_PUBLIC_ADMIN_TOKEN ?? "admin-secret";

export type AdminCheckItem = {
  id: string;
  stage_id: string;
  title: string;
  description: string | null;
  order_index: number;
};

export type AdminStage = {
  id: string;
  slug: string;
  title: string;
  short_explanation: string;
  common_mistakes: string;
  must_document: string;
  order_index: number;
  checks: AdminCheckItem[];
};

async function adminRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Token": ADMIN_TOKEN,
      ...(options.headers || {})
    }
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Admin request failed: ${res.status} ${text}`);
  }
  return (await res.json()) as T;
}

export async function fetchAdminStages(): Promise<AdminStage[]> {
  return adminRequest<AdminStage[]>("/admin/stages");
}

export async function saveAdminStage(
  stage: AdminStage
): Promise<AdminStage> {
  return adminRequest<AdminStage>("/admin/stages", {
    method: "POST",
    body: JSON.stringify(stage)
  });
}

