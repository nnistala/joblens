import Link from "next/link";

interface CompanyPageProps {
  params: { slug: string };
}

async function getCompany(slug: string) {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/companies/${slug}`,
    { next: { revalidate: 3600 } }
  );
  if (!res.ok) return null;
  return res.json();
}

async function getCompanyJobs(companyId: string) {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/companies/${companyId}/jobs`,
    { next: { revalidate: 600 } }
  );
  if (!res.ok) return [];
  return res.json();
}

export default async function CompanyPage({ params }: CompanyPageProps) {
  const company = await getCompany(params.slug);

  if (!company) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-gray-900">Company not found</h1>
        <Link href="/" className="text-indigo-600 hover:underline mt-4 inline-block">
          Back to home
        </Link>
      </div>
    );
  }

  const jobs = await getCompanyJobs(company.id);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="bg-white rounded-xl shadow-sm border p-8 mb-8">
        <div className="flex items-start gap-6">
          {company.logo_url && (
            <img
              src={company.logo_url}
              alt={company.name}
              className="w-20 h-20 rounded-lg object-contain border"
            />
          )}
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{company.name}</h1>
            {company.industry && (
              <p className="text-gray-600 mt-1">{company.industry}</p>
            )}
            {company.size_bucket && (
              <p className="text-sm text-gray-500 mt-1">
                {company.size_bucket} employees
              </p>
            )}
            <div className="flex gap-3 mt-4">
              {company.is_verified && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Verified
                </span>
              )}
              {company.career_page_url && (
                <a
                  href={company.career_page_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-indigo-600 hover:underline"
                >
                  Career Page
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Open Positions ({jobs.length || 0})
      </h2>

      {jobs.length === 0 ? (
        <p className="text-gray-500">No open positions found.</p>
      ) : (
        <div className="space-y-4">
          {jobs.map((job: any) => (
            <Link
              key={job.id}
              href={`/jobs/${job.id}`}
              className="block bg-white rounded-lg border p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {job.title}
                  </h3>
                  <p className="text-gray-600 mt-1">
                    {job.location_city}
                    {job.location_state && `, ${job.location_state}`}
                  </p>
                  <div className="flex gap-2 mt-2">
                    {job.work_mode && (
                      <span className="px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-700">
                        {job.work_mode}
                      </span>
                    )}
                    {job.job_type && (
                      <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700">
                        {job.job_type.replace("_", " ")}
                      </span>
                    )}
                  </div>
                </div>
                {job.salary_min && (
                  <span className="text-sm text-gray-600">
                    ₹{(job.salary_min / 100000).toFixed(0)}L - ₹
                    {(job.salary_max / 100000).toFixed(0)}L
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
