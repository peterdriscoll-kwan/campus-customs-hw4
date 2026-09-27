// The catalogue's `name` field is inconsistent about whether residential-college
// items say "College" (e.g. "Davenport College Crewneck" vs. "Berkeley 1 4 Zip").
// This normalizes display names only — the underlying db field is untouched.
const RESIDENTIAL_COLLEGES = [
  "Benjamin Franklin",
  "Grace Hopper",
  "Jonathan Edwards",
  "Pauli Murray",
  "Timothy Dwight",
  "Ezra Stiles",
  "Berkeley",
  "Branford",
  "Davenport",
  "Morse",
  "Pierson",
  "Saybrook",
  "Silliman",
  "Trumbull",
].sort((a, b) => b.length - a.length);

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function formatProductName(name: string): string {
  for (const college of RESIDENTIAL_COLLEGES) {
    const pattern = new RegExp(`^(${escapeRegExp(college)})(?!\\s*College\\b)`, "i");
    if (pattern.test(name)) {
      return name.replace(pattern, `$1 College`);
    }
  }
  return name;
}
