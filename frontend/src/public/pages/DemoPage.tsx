import { Play } from "lucide-react";
import { ComingSoon } from "../components/ComingSoon";

export function DemoPage() {
  return (
    <ComingSoon
      icon={Play}
      title="Demo"
      description="An interactive walkthrough is on the way."
    />
  );
}
