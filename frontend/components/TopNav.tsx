import Link from "next/link";

export default function TopNav() {
  return (
    <nav className="top-nav">
      <span className="brand">Namma Nyaya</span>
      <Link href="/">Document</Link>
      <Link href="/compare">Compare</Link>
      <Link href="/law-mapping">Law Mapping</Link>
      <Link href="/navigator">Navigator</Link>
    </nav>
  );
}
