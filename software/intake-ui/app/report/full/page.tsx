import type { Metadata } from "next";
import { FullReport } from "./FullReport";

export const metadata: Metadata = {
  title: "Full PIA evidence report",
  description:
    "The complete evidence-linked narrative, capability register, interpretation limits, and development questions behind a PIA participant overview.",
};

export default function FullReportPage() {
  return <FullReport />;
}
