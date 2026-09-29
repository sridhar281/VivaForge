export type ContentType = "video" | "audio" | "pdf" | "pptx";
export type ProcessingStatus =
  | "uploaded"
  | "processing"
  | "transcribing"
  | "understanding"
  | "generating"
  | "completed"
  | "failed";

export interface ContentRead {
  id: string;
  title: string;
  content_type: ContentType;
  original_filename: string;
  status: ProcessingStatus;
  status_message: string | null;
  duration_seconds: number | null;
  page_count: number | null;
  created_at: string;
}

export interface ConceptRead {
  id: string;
  name: string;
  explanation: string | null;
  source_label: string | null;
}

export interface SummaryRead {
  executive_summary: string;
  topic_summaries: { topic: string; summary: string }[];
  key_concepts: string[];
  definitions: { term: string; definition: string }[];
  examples: string[];
  quick_revision_notes: string[];
}

export interface FlashcardRead {
  front: string;
  back: string;
  concept: string;
}

export interface GraphNode {
  id: string;
  name: string;
  explanation: string | null;
  mastery_score: number | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation_type: string;
}

export interface GraphRead {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface RevisionScene {
  concept: string;
  narration: string;
  subtitle_text: string;
  source_label: string | null;
}
