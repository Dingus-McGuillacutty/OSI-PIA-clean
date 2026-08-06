import type { Metadata } from "next";
import { DocumentationUpdate } from "./DocumentationUpdate";

export const metadata: Metadata = {
  title: "Use your PIA report",
  description:
    "Review evidence-based suggestions and create an editable LinkedIn, résumé, or CV draft without changing the original document.",
};

export default function ReportPage() {
  return <DocumentationUpdate />;
}
