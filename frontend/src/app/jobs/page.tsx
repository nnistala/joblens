"use client";

import { useState, useCallback, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { SlidersHorizontal, ChevronLeft, ChevronRight } from "lucide-react";
import { searchJobs, saveJob, unsaveJob } from "@/lib/api";
import SearchBar from "@/components/search-bar";
import JobCard from "@/components/job-card";
import FilterPanel, { type FilterValues } from "@/components/filter-panel";
import type { SearchParams } from "@/types";

function JobSearchContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [filterOpen, setFilterOpen] = useState(false);
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());

  // Read search params
  const q = searchParams.get("q") || "";
  const location = searchParams.get("location") || "";
  const jobType = searchParams.get("job_type") || "";
  const workMode = searchParams.get("work_mode") || "";
  const experienceMin = searchParams.get("experience_min") || "";
  const experienceMax = searchParams.get("experience_max") || "";
  const salaryMin = searchParams.get("salary_min") || "";
  const skills = searchParams.get("skills") || "";
  const sortBy = (searchParams.get("sort_by") as SearchParams["sort_by"]) || "relevance";
  const page = parseInt(searchParams.get("page") || "1", 10);

  const params: SearchParams = {
    q: q || undefined,
    location: location || undefined,
    job_type: jobType || undefined,
    work_mode: workMode || undefined,
    experience_min: experienceMin ? Number(experienceMin) : undefined,
    experience_max: experienceMax ? Number(experienceMax) : undefined,
    salary_min: salaryMin ? Number(salaryMin) : undefined,
    skills: skills || undefined,
    sort_by: sortBy,
    page,
    page_size: 20,
  };

  const { data, isLoading, isError } = useQuery({
    queryKey: ["jobs", params],
    queryFn: () => searchJobs(params),
  });

  const updateParams = useCallback(
    (updates: Record<string, string | undefined>) => {
      const next = new URLSearchParams(searchParams.toString());
      Object.entries(updates).forEach(([key, value]) => {
        if (value) {
          next.set(key, value);
        } else {
          next.delete(key);
        }
      });
      // Reset to page 1 when filters change (unless we're explicitly setting page)
      if (!("page" in updates)) {
        next.delete("page");
      }
      router.push(`/jobs?${next.toString()}`);
    },
    [searchParams, router]
  );

  const handleApplyFilters = (filters: FilterValues) => {
    updateParams({
      job_type: filters.job_type.join(",") || undefined,
      work_mode: filters.work_mode.join(",") || undefined,
      experience_min: filters.experience_min || undefined,
      experience_max: filters.experience_max || undefined,
      salary_min: filters.salary_min || undefined,
      skills: filters.skills.join(",") || undefined,
    });
    setFilterOpen(false);
  };

  const handleClearFilters = () => {
    updateParams({
      job_type: undefined,
      work_mode: undefined,
      experience_min: undefined,
      experience_max: undefined,
      salary_min: undefined,
      skills: undefined,
    });
    setFilterOpen(false);
  };

  const handleSave = async (jobId: string) => {
    if (savedJobs.has(jobId)) {
      setSavedJobs((prev) => {
        const next = new Set(prev);
        next.delete(jobId);
        return next;
      });
      try {
        await unsaveJob(jobId);
      } catch { /* ignore */ }
    } else {
      setSavedJobs((prev) => new Set(prev).add(jobId));
      try {
        await saveJob(jobId);
      } catch { /* ignore */ }
    }
  };

  const filterInitial: Partial<FilterValues> = {
    job_type: jobType ? jobType.split(",") : [],
    work_mode: workMode ? workMode.split(",") : [],
    experience_min: experienceMin,
    experience_max: experienceMax,
    salary_min: salaryMin,
    skills: skills ? skills.split(",") : [],
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Search bar */}
      <SearchBar initialQuery={q} initialLocation={location} />

      {/* Toolbar */}
      <div className="mt-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setFilterOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 lg:hidden"
          >
            <SlidersHorizontal className="h-4 w-4" />
            Filters
          </button>
          {data && (
            <p className="text-sm text-gray-500">
              <span className="font-medium text-gray-900">{data.total.toLocaleString()}</span>{" "}
              results found
            </p>
          )}
        </div>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => updateParams({ sort_by: e.target.value })}
          className="rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-700 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        >
          <option value="relevance">Sort by Relevance</option>
          <option value="date">Sort by Date</option>
          <option value="salary">Sort by Salary</option>
        </select>
      </div>

      {/* Content */}
      <div className="mt-6 flex gap-6">
        {/* Filter panel */}
        <FilterPanel
          initialValues={filterInitial}
          onApply={handleApplyFilters}
          onClear={handleClearFilters}
          open={filterOpen}
          onClose={() => setFilterOpen(false)}
        />

        {/* Job list */}
        <div className="flex-1">
          {isLoading && (
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div
                  key={i}
                  className="h-36 animate-pulse rounded-xl border border-gray-200 bg-gray-50"
                />
              ))}
            </div>
          )}

          {isError && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-8 text-center">
              <p className="text-sm text-red-600">
                Something went wrong while fetching jobs. Please try again.
              </p>
            </div>
          )}

          {data && data.items.length === 0 && (
            <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
              <p className="text-lg font-medium text-gray-900">No jobs found</p>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your search or filters.
              </p>
            </div>
          )}

          {data && data.items.length > 0 && (
            <>
              <div className="space-y-4">
                {data.items.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    onSave={handleSave}
                    isSaved={savedJobs.has(job.id)}
                  />
                ))}
              </div>

              {/* Pagination */}
              {data.total_pages > 1 && (
                <div className="mt-8 flex items-center justify-center gap-2">
                  <button
                    onClick={() => updateParams({ page: String(page - 1) })}
                    disabled={page <= 1}
                    className="inline-flex items-center gap-1 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <ChevronLeft className="h-4 w-4" />
                    Previous
                  </button>
                  <span className="px-4 text-sm text-gray-500">
                    Page {page} of {data.total_pages}
                  </span>
                  <button
                    onClick={() => updateParams({ page: String(page + 1) })}
                    disabled={page >= data.total_pages}
                    className="inline-flex items-center gap-1 rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Next
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function JobsPage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <div className="space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="h-36 animate-pulse rounded-xl border border-gray-200 bg-gray-50"
              />
            ))}
          </div>
        </div>
      }
    >
      <JobSearchContent />
    </Suspense>
  );
}
