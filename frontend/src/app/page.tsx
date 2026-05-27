import SearchBar from "@/components/search-bar";
import { Briefcase, Building2, Globe, ArrowRight } from "lucide-react";

const STATS = [
  { label: "Jobs", value: "50,000+", icon: Briefcase },
  { label: "Companies", value: "500+", icon: Building2 },
  { label: "Platforms", value: "200+", icon: Globe },
];

const TOP_COMPANIES = [
  "Google",
  "Microsoft",
  "Amazon",
  "Flipkart",
  "Swiggy",
  "Razorpay",
  "PhonePe",
  "Zerodha",
  "CRED",
  "Infosys",
  "TCS",
  "Wipro",
];

export default function HomePage() {
  return (
    <div>
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 px-4 pb-20 pt-16 sm:px-6 sm:pb-28 sm:pt-24 lg:px-8">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-40" />
        <div className="relative mx-auto max-w-4xl text-center">
          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl">
            Every Job, From The Source
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-primary-100 sm:text-xl">
            One search across every company and platform. Zero noise, every
            opportunity in India.
          </p>

          {/* Search bar */}
          <div className="mx-auto mt-10 max-w-3xl">
            <SearchBar size="large" />
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="-mt-10 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto grid max-w-4xl grid-cols-1 gap-4 sm:grid-cols-3">
          {STATS.map((stat) => (
            <div
              key={stat.label}
              className="flex items-center gap-4 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary-50 text-primary-600">
                <stat.icon className="h-6 w-6" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-500">{stat.label}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Top Companies */}
      <section className="bg-gray-50 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900">
              Top Companies Hiring
            </h2>
            <p className="mt-3 text-gray-500">
              Explore opportunities at India&apos;s leading employers.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
            {TOP_COMPANIES.map((company) => (
              <div
                key={company}
                className="flex h-20 items-center justify-center rounded-xl border border-gray-200 bg-white text-sm font-medium text-gray-700 transition-shadow hover:shadow-md"
              >
                {company}
              </div>
            ))}
          </div>

          <div className="mt-8 text-center">
            <a
              href="/companies"
              className="inline-flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700"
            >
              View all companies
              <ArrowRight className="h-4 w-4" />
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
