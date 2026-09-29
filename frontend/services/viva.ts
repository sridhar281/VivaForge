import { apiClient } from "@/lib/api-client";
import type { AnswerSubmitResponse, SessionStartResponse } from "@/types/viva";

export async function generateVivaPdf(contentId: string): Promise<{ artifact_id: string }> {
  const { data } = await apiClient.post(`/content/${contentId}/viva/generate`);
  return data;
}

export function artifactDownloadUrl(artifactId: string): string {
  return `${apiClient.defaults.baseURL}/artifacts/${artifactId}`;
}

export async function startVivaSession(contentId: string): Promise<SessionStartResponse> {
  const { data } = await apiClient.post<SessionStartResponse>("/viva/session", null, {
    params: { content_id: contentId },
  });
  return data;
}

export async function submitAnswer(
  sessionId: string,
  questionId: string,
  answerText: string,
  wasSpoken = false
): Promise<AnswerSubmitResponse> {
  const { data } = await apiClient.post<AnswerSubmitResponse>(`/viva/session/${sessionId}/answer`, {
    question_id: questionId,
    answer_text: answerText,
    was_spoken: wasSpoken,
  });
  return data;
}
