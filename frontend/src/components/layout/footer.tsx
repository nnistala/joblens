import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <span className="text-xl font-bold text-primary-600">JobLens</span>
            <p className="mt-2 text-sm text-gray-500">
              Every Job, From The Source. One search across every company and
              platform in India.
            </p>
            <p className="mt-4 text-xs font-medium text-gray-400">
              Made in India
            </p>
          </div>

          {/* For Job Seekers */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900">
              For Job Seekers
            </h3>
            <ul className="mt-4 space-y-2">
              <li>
                <Link
                  href="/jobs"
                  className="text-sm text-gray-500 hover:text-primary-600"
                >
                  Browse Jobs
                </Link>
              </li>
              <li>
                <Link
                  href="/companies"
                  className="text-sm text-gray-500 hover:text-primary-600"
                >
                  Companies
                </Link>
              </li>
              <li>
                <Link
                  href="/dashboard"
                  className="text-sm text-gray-500 hover:text-primary-600"
                >
                  Saved Jobs
                </Link>
              </li>
              <li>
                <Link
                  href="/dashboard"
                  className="text-sm text-gray-500 hover:text-primary-600"
                >
                  Job Alerts
                </Link>
              </li>
            </ul>
          </div>

          {/* For Employers */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900">
              For Employers
            </h3>
            <ul className="mt-4 space-y-2">
              <li>
                <Link
                  href="/hr"
                  className="text-sm text-gray-500 hover:text-primary-600"
                >
                  List Jobs Free
                </Link>
              </li>
              <li>
                <Link
                  href="/hr"
                  className="text-sm text-gray-500 hover:text-primary-600"
                >
                  HR Portal
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900">Legal</h3>
            <ul className="mt-4 space-y-2">
              <li>
                <Link
                  href="/privacy"
                  className="text-sm text-gray-500 hover:text-primary-600"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link
                  href="/terms"
                  className="text-sm text-gray-500 hover:text-primary-600"
                >
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link
                  href="/contact"
                  className="text-sm text-gray-500 hover:text-primary-600"
                >
                  Contact Us
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t border-gray-200 pt-8 text-center">
          <p className="text-xs text-gray-400">
            &copy; {new Date().getFullYear()} JobLens. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
