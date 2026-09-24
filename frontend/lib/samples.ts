import type { SampleDocument } from "@/components/DocumentUpload";

/**
 * Real, small synthetic sample documents (served as static files from
 * /public/samples) used by the "try a sample" affordances on the design.
 * These are uploaded through the exact same live POST /documents call as a
 * manually chosen file — not mocked data — so they exercise the real
 * ingestion/classification/explanation pipeline end to end.
 */
export const RENTAL_HSR_LAYOUT_SAMPLE: SampleDocument = {
  label: "Rental agreement · HSR Layout",
  url: "/samples/rental-agreement-hsr-layout.pdf",
  filename: "rental-agreement-hsr-layout.pdf",
};

export const RENTAL_KORAMANGALA_SAMPLE: SampleDocument = {
  label: "Use sample: Koramangala",
  url: "/samples/rental-agreement-koramangala.pdf",
  filename: "rental-agreement-koramangala.pdf",
};

export const OFFER_WHITEFIELD_SAMPLE: SampleDocument = {
  label: "Offer letter · Whitefield",
  url: "/samples/offer-letter-whitefield.pdf",
  filename: "offer-letter-whitefield.pdf",
};

export const HIGH_STAKES_SAMPLE: SampleDocument = {
  label: "High-stakes example",
  url: "/samples/high-stakes-example.pdf",
  filename: "high-stakes-example.pdf",
};

export const DOCUMENT_PAGE_SAMPLES: SampleDocument[] = [
  RENTAL_HSR_LAYOUT_SAMPLE,
  OFFER_WHITEFIELD_SAMPLE,
  HIGH_STAKES_SAMPLE,
];

export const COMPARE_SAMPLE_A: SampleDocument = {
  label: "Use sample: HSR Layout",
  url: "/samples/rental-agreement-hsr-layout.pdf",
  filename: "rental-agreement-hsr-layout.pdf",
};

export const COMPARE_SAMPLE_B: SampleDocument = RENTAL_KORAMANGALA_SAMPLE;
