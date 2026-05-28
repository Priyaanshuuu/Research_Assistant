import { Skeleton } from "@/components/ui/skeleton";

export function ReportSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Title */}
      <div className="space-y-2">
        <Skeleton className="h-8 w-3/4" />
        <Skeleton className="h-4 w-40" />
      </div>

      {/* Summary box */}
      <div className="border border-slate-200 rounded-xl p-5 space-y-3">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <Skeleton className="h-4 w-4/6" />
      </div>

      {/* Takeaways */}
      <div className="border border-slate-200 rounded-xl p-5 space-y-3">
        <Skeleton className="h-4 w-28" />
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-4 w-full" />
        ))}
      </div>

      {/* Sections */}
      <div className="space-y-4">
        <Skeleton className="h-5 w-36" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-5 py-4 bg-slate-50">
              <Skeleton className="h-4 w-2/3" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}