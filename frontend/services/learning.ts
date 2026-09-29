import { apiClient } from "@/lib/api-client";
import type { FlashcardRead, GraphRead, RevisionScene } from "@/types/content";
import type { ExplainBackPrompt, ExplainBackResult, KnowledgeProfile, RevisionPlan } from "@/types/viva";

export async function getKnowledgeProfile(): Promise<KnowledgeProfile> {
  const { data } = await apiClient.get<KnowledgeProfile>("/knowledge-profile");
  return data;
}

export async function getRevisionPlan(): Promise<RevisionPlan> {
  const { data } = await apiClient.get<RevisionPlan>("/revision-plan");
  return data;
}

export async function regenerateRevisionPlan(): Promise<RevisionPlan> {
  const { data } = await apiClient.post<RevisionPlan>("/revision-plan/regenerate");
  return data;
}

export async function getGraph(contentId: string): Promise<GraphRead> {
  const { data } = await apiClient.get<GraphRead>(`/content/${contentId}/graph`);
  return data;
}

export async function getFlashcards(contentId: string): Promise<FlashcardRead[]> {
  const { data } = await apiClient.get<FlashcardRead[]>(`/content/${contentId}/flashcards`);
  return data;
}

export async function markFlashcard(contentId: string, concept: string, status: "mastered" | "difficult") {
  await apiClient.post(`/content/${contentId}/flashcards/mark`, { concept, status });
}

export async function getRevisionVideo(contentId: string): Promise<RevisionScene[]> {
  const { data } = await apiClient.get<RevisionScene[]>(`/content/${contentId}/revision-video`);
  return data;
}

export async function getExplainBackPrompt(contentId: string): Promise<ExplainBackPrompt> {
  const { data } = await apiClient.get<ExplainBackPrompt>(`/explain-back/${contentId}/prompt`);
  return data;
}

export async function submitExplainBack(
  contentId: string,
  conceptId: string,
  explanationText: string
): Promise<ExplainBackResult> {
  const { data } = await apiClient.post<ExplainBackResult>("/explain-back/evaluate", {
    content_id: contentId,
    concept_id: conceptId,
    explanation_text: explanationText,
  });
  return data;
}
