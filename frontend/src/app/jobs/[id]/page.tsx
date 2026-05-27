import Link from "next/link";
import Image from "next/image";
import {
  MapPin,
  Briefcase,
  Clock,
  DollarSign,
  ExternalLink,
  Layers,
  Heart,
  ArrowLeft,
  Sparkles,
  Building2,
} from "lucide-react";
import { formatSalary, formatDate, cn } from "@/lib/utils";
import type { JobDetail } from "@/types";

const WORK_MODE_COLORS: Record<string, string> = {
  remote: "bg-green-100 text-green-700",
  hybrid: "bg-blue-100 text-blue-700",
  onsite: "bg-orange-100 text-orange-700",
};

const JOB_TYPE_LABELS: Record<string, string> = {
  full_time: "Full Time",
  part_time: "Part Time",
  contract: "Contract",
  internship: "Internship",
};

async function fetchJob(id: string): Promise<JobDetail> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  const res = await fetch(`${apiUrl}/jobs/${id}`, { next: { revalidate: 300 } });
  if (!res.ok) {
    throw new Error("Failed to fetch job");
  }
  return res.json();
}

async function fetchRelatedJobs(jobId: string): Promise<JobDetail[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  try {
    const res = await fetch(`${apiUrl}/jobs/${jobId}/related?limit=4`, {
      next: { revalidate: 600 },
    });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function JobDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const [job, relatedJobs] = await Promise.all([
    fetchJob(params.id),
    fetchRelatedJobs(params.id),
  ]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Back */}
      <Link
        href="/jobs"
        className="mb-6 inline-flex items-center gap-1 text-sm text-gray-500 hover:text-primary-600"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to search
      </Link>

      <div className="flex flex-col gap-8 lg:flex-row">
        {/* Main content */}
        <div className="flex-1">
          <div className="rounded-xl border border-gray-200 bg-white p-6 sm:p-8">
            {/* Header */}
            <div className="flex gap-4">
              {job.company_logo ? (
                <Image
                  src={job.company_logo}
                  alt={job.company_name}
                  width={64}
                  height={64}
                  className="hidden rounded-xl border border-gray-100 object-contain sm:block"
                />
              ) : (
                <div className="hidden h-16 w-16 items-center justify-center rounded-xl border border-gray-100 bg-gray-50 text-2xl font-semibold text-gray-400 sm:flex">
                  {job.company_name.charAt(0)}
                </div>
              )}

              <div className="flex-1">
                <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">
                  {job.title}
                </h1>
                <div className="mt-1 flex flex-wrap items-center gap-2 text-base text-gray-600">
                  <Link
                    href={`/companies/${job.company_slug}`}
                    className="font-medium hover:text-primary-600"
                  >
                    {job.company_name}
                  </Link>
                </div>
              </div>
            </div>

            {/* Meta */}
            <div className="mt-6 flex flex-wrap gap-3">
              <span className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600">
                <MapPin className="h-4 w-4 text-gray-400" />
                {job.location}
              </span>
              <span
                className={cn(
                  "inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium capitalize",
                  WORK_MODE_COLORS[job.work_mode] || "bg-gray-100 text-gray-700"
                )}
              >
                {job.work_mode}
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600">
                <Briefcase className="h-4 w-4 text-gray-400" />
                {JOB_TYPE_LABELS[job.job_type] || job.job_type}
              </span>
              {(job.salary_min || job.salary_max) && (
                <span className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600">
                  <DollarSign className="h-4 w-4 text-gray-400" />
                  {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
                </span>
              )}
              {(job.experience_min !== null || job.experience_max !== null) && (
                <span className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600">
                  <Clock className="h-4 w-4 text-gray-400" />
                  {job.experience_min ?? 0} - {job.experience_max ?? "any"} yrs
                </span>
              )}
            </div>

            {/* Actions */}
            <div className="mt-6 flex flex-wrap gap-3">
              {job.apply_mode === "redirect" && job.apply_url ? (
                <a
                  href={job.apply_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-primary-700"
                >
                  Apply Now
                  <ExternalLink className="h-4 w-4" />
                </a>
              ) : (
                <button className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-primary-700">
                  Apply Now
                </button>
              )}
              <button className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-6 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50">
                <Heart className="h-4 w-4" />
                Save Job
              </button>
            </div>

            {/* AI Summary */}
            {job.ai_summary && (
              <div className="mt-8 rounded-lg border border-primary-200 bg-primary-50 p-5">
                <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-primary-700">
                  <Sparkles className="h-4 w-4" />
                  AI Summary
                </div>
                <p className="text-sm leading-relaxed text-primary-900">
                  {job.ai_summary}
                </p>
              </div>
            )}

            {/* Skills */}
            {job.skills.length > 0 && (
              <div className="mt-8">
                <h2 className="text-sm font-semibold text-gray-900">
                  Skills & Technologies
                </h2>
                <div className="mt-3 flex flex-wrap gap-2">
                  {job.skills.map((skill) => (
                    <span
                      key={skill}
                      className="rounded-full bg-gray-100 px-3 py-1 text-sm font-medium text-gray-700"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Description */}
            <div className="mt-8">
              <h2 className="text-sm font-semibold text-gray-900">
                Job Description
              </h2>
              <div
                className="prose prose-sm mt-3 max-w-none text-gray-600"
                dangerouslySetInnerHTML={{ __html: job.description }}
              />
            </div>

            {/* Sources */}
            {job.sources.length > 0 && (
              <div className="mt-8 rounded-lg border border-gray-200 bg-gray-50 p-5">
                <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-900">
                  <Layers className="h-4 w-4 text-primary-600" />
                  Found on {job.sources.length} platform
                  {job.sources.length !== 1 ? "s" : ""}
                </div>
                <div className="space-y-2">
                  {job.sources.map((source) => (
                    <a
                      key={source.id}
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between rounded-lg bg-white px-4 py-2.5 text-sm transition-colors hover:bg-gray-100"
                    >
                      <span className="font-medium text-gray-700">
                        {source.platform}
                      </span>
                      <ExternalLink className="h-4 w-4 text-gray-400" />
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Posted date */}
            <p className="mt-6 text-xs text-gray-400">
              Posted {formatDate(job.posted_at)}
            </p>
          </div>
        </div>

        {/* Sidebar */}
        <aside className="w-full shrink-0 lg:w-80">
          {/* Company card */}
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-50 text-gray-400">
                <Building2 className="h-5 w-5" />
              </div>
              <div>
                <Link
                  href={`/companies/${job.company_slug}`}
                  className="text-sm font-semibold text-gray-900 hover:text-primary-600"
                >
                  {job.company_name}
                </Link>
                <p className="text-xs text-gray-500">{job.location}</p>
              </div>
            </div>
            <Link
              href={`/companies/${job.company_slug}`}
              className="mt-4 block rounded-lg border border-gray-200 px-4 py-2 text-center text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              View Company Profile
            </Link>
          </div>

          {/* Related jobs */}
          {relatedJobs.length > 0 && (
            <div className="mt-6 rounded-xl border border-gray-200 bg-white p-5">
              <h3 className="mb-4 text-sm font-semibold text-gray-900">
                Related Jobs
              </h3>
              <div className="space-y-3">
                {relatedJobs.map((related) => (
                  <Link
                    key={related.id}
                    href={`/jobs/${related.id}`}
                    className="block rounded-lg p-3 transition-colors hover:bg-gray-50"
                  >
                    <p className="text-sm font-medium text-gray-900">
                      {related.title}
                    </p>
                    <p className="mt-0.5 text-xs text-gray-500">
                      {related.company_name} &middot; {related.location}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
