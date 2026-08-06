import type { Metadata } from "next";
import { ParticipantStart } from "./ParticipantStart";

export const metadata: Metadata = {
  title: "Begin private participant intake",
  description:
    "A private, participant-controlled starting point for professional evidence and initial documents.",
};

export default function Home() {
  return <ParticipantStart />;
}
