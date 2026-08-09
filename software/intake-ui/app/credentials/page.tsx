import type { Metadata } from "next";
import { CredentialReview } from "../CredentialReview";

export const metadata: Metadata = {
  title: "Quick credential check-in",
  description:
    "A fast, participant-friendly review of credential meaning and work application.",
};

export default function CredentialsPage() {
  return <CredentialReview />;
}
