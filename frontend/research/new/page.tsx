import { auth } from "@/auth";
import { redirect } from "next/navigation";
import { AppLayout } from "@/components/layout/AppLayout";
import { ResearchForm } from "@/components/research/ResearchForm";

export default async function NewResearchPage() {
  const session = await auth();
  if (!session?.user) redirect("/login");

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold text-slate-900">New Research</h1>
          <p className="text-sm text-slate-500">
            Enter a topic and our AI agents will research, evaluate, and write a
            structured report for you.
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <ResearchForm />
        </div>
      </div>
    </AppLayout>
  );
}