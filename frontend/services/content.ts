import { apiClient } from "@/lib/api-client";
import type { ConceptRead, ContentRead, SummaryRead } from "@/types/content";

export async function uploadContent(file: File, title?: string): Promise<ContentRead> {
  const form = new FormData();
  form.append("file", file);
  // Deliberately NOT setting Content-Type manually — the browser must set it
  // itself so it includes the multipart boundary; setting it by hand breaks upload parsing.
  const { data } = await apiClient.post<ContentRead>("/content/upload", form, {
    params: title ? { title } : undefined,
  });
  return data;
}

export async function listContent(): Promise<ContentRead[]> {
  const { data } = await apiClient.get<ContentRead[]>("/content");
  return data;
}

export async function getContent(id: string): Promise<ContentRead> {
  const { data } = await apiClient.get<ContentRead>(`/content/${id}`);
  return data;
}

export async function triggerProcessing(id: string): Promise<void> {
  await apiClient.post(`/content/${id}/process`);
}

export async function getStatus(id: string): Promise<ContentRead> {
  const { data } = await apiClient.get<ContentRead>(`/content/${id}/status`);
  return data;
}

export async function getSummary(id: string): Promise<SummaryRead> {
  const { data } = await apiClient.get<SummaryRead>(`/content/${id}/summary`);
  return data;
}

export async function getConcepts(id: string): Promise<ConceptRead[]> {
  const { data } = await apiClient.get<ConceptRead[]>(`/content/${id}/concepts`);
  return data;
}
